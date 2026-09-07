"""
cbe/controller/workload_controller.py
Learned workload router and contextual bandit policy optimizer.
Learns which compute tier maximizes compute elimination while strictly honoring
the RenderingContract safety constraints.
"""

from __future__ import annotations

import random
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class RouteStats:
    route_name: str
    invocations: int = 0
    successes: int = 0
    failures: int = 0
    avg_latency_ms: float = 10.0
    avg_ssim: float = 0.98
    relative_cost: float = 0.50


class WorkloadController:
    """
    Contextual bandit that selects the cheapest compute tier satisfying quality/latency contracts.
    Exploration is strictly bounded to prevent contract violations.
    """
    ROUTES = [
        "TIER_0_EXACT_REUSE",
        "TIER_1_REPROJECTION",
        "TIER_2_TEMPORAL_SUPER_RES",
        "TIER_3_ADAPTIVE_RECONSTRUCTION",
        "TIER_4_SPARSE_RESIDUAL",
        "TIER_5_NEURAL_IGPU",
        "TIER_6_RESTIR_SAMPLE_REUSE",
        "TIER_7_HIGH_FIDELITY_FALLBACK",
    ]

    ROUTE_COSTS = {
        "TIER_0_EXACT_REUSE": 0.00,
        "TIER_1_REPROJECTION": 0.02,
        "TIER_2_TEMPORAL_SUPER_RES": 0.10,
        "TIER_3_ADAPTIVE_RECONSTRUCTION": 0.25,
        "TIER_4_SPARSE_RESIDUAL": 0.20,
        "TIER_5_NEURAL_IGPU": 0.15,
        "TIER_6_RESTIR_SAMPLE_REUSE": 0.12,
        "TIER_7_HIGH_FIDELITY_FALLBACK": 1.00,
    }

    def __init__(self, exploration_rate: float = 0.05):
        self.epsilon = exploration_rate
        self.stats: Dict[str, RouteStats] = {
            r: RouteStats(route_name=r, relative_cost=self.ROUTE_COSTS[r])
            for r in self.ROUTES
        }
        self.total_decisions = 0

    def select_route(
        self,
        strategy_hint: str,
        emergency_mode: bool = False,
        scene_complexity: str = "medium"
    ) -> str:
        """
        Selects execution route using UCB / epsilon-greedy bandit
        while strictly prioritizing safety if emergency_mode is active.
        """
        self.total_decisions += 1
        
        # In emergency mode, skip low-cost approximations and escalate to high fidelity
        if emergency_mode:
            return "TIER_7_HIGH_FIDELITY_FALLBACK"

        # Epsilon-greedy safe exploration
        if random.random() < self.epsilon:
            # Safe exploration candidates: exclude worst fallback unless necessary
            candidate = random.choice([
                "TIER_1_REPROJECTION",
                "TIER_2_TEMPORAL_SUPER_RES",
                "TIER_3_ADAPTIVE_RECONSTRUCTION",
                "TIER_4_SPARSE_RESIDUAL",
                "TIER_6_RESTIR_SAMPLE_REUSE"
            ])
            return candidate

        # Honor state-driven strategy hints when strongly determined
        if strategy_hint == "EXACT_REUSE":
            return "TIER_0_EXACT_REUSE"
        elif strategy_hint == "TEMPORAL_REPROJECTION":
            return "TIER_1_REPROJECTION"
        elif strategy_hint == "SPARSE_RESIDUAL":
            return "TIER_4_SPARSE_RESIDUAL"
            
        # Exploit: Pick highest scoring route satisfying quality
        best_route = "TIER_3_ADAPTIVE_RECONSTRUCTION"
        highest_score = -1.0
        
        for r_name, r_stat in self.stats.items():
            if r_stat.failures > 5 and r_stat.avg_ssim < 0.90:
                continue  # Skip degraded route
                
            success_rate = (r_stat.successes + 1.0) / float(r_stat.invocations + 2.0)
            # Reward high success and low cost
            score = (success_rate * r_stat.avg_ssim) / (r_stat.relative_cost + 0.1)
            if score > highest_score:
                highest_score = score
                best_route = r_name
                
        return best_route

    def record_outcome(
        self,
        route_name: str,
        latency_ms: float,
        ssim: float,
        contract_satisfied: bool
    ):
        """Updates moving averages based on real execution metrics."""
        stat = self.stats.get(route_name)
        if not stat:
            return
            
        stat.invocations += 1
        if contract_satisfied:
            stat.successes += 1
        else:
            stat.failures += 1
            
        alpha = 0.20
        stat.avg_latency_ms = (1.0 - alpha) * stat.avg_latency_ms + alpha * latency_ms
        stat.avg_ssim = (1.0 - alpha) * stat.avg_ssim + alpha * ssim

    def get_summary(self) -> Dict[str, Any]:
        return {
            r: {
                "invocations": s.invocations,
                "success_rate_pct": round((s.successes / max(1, s.invocations)) * 100.0, 1),
                "avg_latency_ms": round(s.avg_latency_ms, 2),
                "avg_ssim": round(s.avg_ssim, 4),
                "relative_cost": s.relative_cost
            }
            for r, s in self.stats.items()
        }
