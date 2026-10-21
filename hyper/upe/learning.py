"""
hyper/upe/learning.py
=====================
ENGINE 14: Adaptive Learning.

Learns from accumulated benchmark runs and counterexamples to continuously
refine candidate pathway selection rankings.
- Maintains inspectable empirical weights for transformation rules per workload family.
- Increases ranking score for rules with consistently verified speedups.
- Decreases ranking score or prunes rules that fail verification or cause regressions.
"""

from __future__ import annotations

import collections
import dataclasses
import json
import time
from typing import Any, Dict, List, Optional
import numpy as np

from hyper.upe.memory import SQLitePathwayStore


@dataclasses.dataclass
class RuleEmpiricalStats:
    rule_id: str
    total_evaluations: int = 0
    verification_successes: int = 0
    verification_failures: int = 0
    average_speedup: float = 1.0
    counterexample_count: int = 0
    confidence_weight: float = 1.0


class AdaptivePathwayLearner:
    """
    Empirical learning model that refines candidate selection from historical records.
    """

    def __init__(self, store: Optional[SQLitePathwayStore] = None) -> None:
        self.store = store
        self.stats: Dict[str, RuleEmpiricalStats] = collections.defaultdict(
            lambda: RuleEmpiricalStats(rule_id="unknown")
        )
        self._load_historical_records()

    def _load_historical_records(self) -> None:
        if self.store is None:
            return
        try:
            benchmarks = self.store.list_benchmarks(limit=200)
            for b in benchmarks:
                r_id = b.get("pathway_id", "").split("_")[1] if "_" in b.get("pathway_id", "") else "generic"
                s = self.stats[r_id]
                s.rule_id = r_id
                s.total_evaluations += 1
                s.verification_successes += 1
                speedup = b.get("measured_speedup", 1.0)
                # Running average speedup
                s.average_speedup = (s.average_speedup * (s.total_evaluations - 1) + speedup) / s.total_evaluations
                s.confidence_weight = min(2.5, max(0.5, s.average_speedup * 0.8))
        except Exception:
            pass

    def record_run(
        self,
        rule_id: str,
        verified: bool,
        measured_speedup: float,
        counterexample_found: bool = False,
    ) -> None:
        s = self.stats[rule_id]
        s.rule_id = rule_id
        s.total_evaluations += 1
        if verified:
            s.verification_successes += 1
            s.average_speedup = (s.average_speedup * (s.total_evaluations - 1) + measured_speedup) / s.total_evaluations
        else:
            s.verification_failures += 1

        if counterexample_found:
            s.counterexample_count += 1

        # Calculate confidence weight: reward verified speedup, heavily penalize counterexamples
        penalty = 0.5 ** s.counterexample_count
        s.confidence_weight = max(0.1, (s.average_speedup * (s.verification_successes / max(1, s.total_evaluations))) * penalty)

    def get_rule_weight(self, rule_id: str) -> float:
        if rule_id in self.stats:
            return self.stats[rule_id].confidence_weight
        return 1.0

    def get_summary(self) -> Dict[str, Any]:
        return {
            rule: {
                "total_evaluations": s.total_evaluations,
                "verification_successes": s.verification_successes,
                "verification_failures": s.verification_failures,
                "average_speedup": round(s.average_speedup, 2),
                "counterexamples": s.counterexample_count,
                "confidence_weight": round(s.confidence_weight, 3),
            }
            for rule, s in self.stats.items()
        }
