"""
hyper_x/ahce/learner.py
=======================
Adaptive Meta-Learner & Strategy Memory for AHCE (Sections 12 & 13).

Uses an interpretable Nearest-Neighbor & Empirical Bayesian model to remember
which computational strategies succeeded or failed for specific structural signatures.
"""

from __future__ import annotations
import json
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from .workload_signature import WorkloadSignature
from .contract import AHCEContract
from .candidate import AHCECandidate


@dataclass
class StrategyExperience:
    signature_digest: str
    sparsity: float
    effective_rank_ratio: float
    arithmetic_intensity: float
    strategy_name: str
    success: bool
    verified: bool
    speedup: float
    work_reduction_pct: float
    error_metric: float


class AHCEMetaLearner:
    """Interpretable strategy memory learning from empirical trials and failures."""

    def __init__(self):
        self.experiences: List[StrategyExperience] = []
        self._strategy_priors: Dict[str, Dict[str, float]] = {
            "exact_cache": {"successes": 5.0, "total": 6.0},
            "low_rank_svd": {"successes": 8.0, "total": 10.0},
            "sparse_csr": {"successes": 6.0, "total": 8.0},
            "dense_baseline": {"successes": 10.0, "total": 10.0}
        }

    def record_experience(
        self,
        signature: WorkloadSignature,
        strategy_name: str,
        success: bool,
        verified: bool,
        speedup: float,
        work_reduction_pct: float,
        error: float
    ) -> None:
        min_dim = min(signature.features.dimensions) if signature.features.dimensions else 1
        eff_rank = signature.features.estimated_effective_rank or min_dim
        rank_ratio = float(eff_rank / max(1, min_dim))

        exp = StrategyExperience(
            signature_digest=signature.signature_digest,
            sparsity=signature.features.sparsity,
            effective_rank_ratio=rank_ratio,
            arithmetic_intensity=signature.features.arithmetic_intensity,
            strategy_name=strategy_name,
            success=success,
            verified=verified,
            speedup=speedup,
            work_reduction_pct=work_reduction_pct,
            error_metric=error
        )
        self.experiences.append(exp)

        # Update empirical Bayesian priors
        if strategy_name not in self._strategy_priors:
            self._strategy_priors[strategy_name] = {"successes": 1.0, "total": 2.0}
        self._strategy_priors[strategy_name]["total"] += 1.0
        if verified and speedup >= 1.0:
            self._strategy_priors[strategy_name]["successes"] += 1.0

    def predict_strategy_rank(
        self,
        signature: WorkloadSignature,
        candidates: List[AHCECandidate]
    ) -> List[Tuple[AHCECandidate, float, str]]:
        """Ranks candidate strategies with an interpretable explanation."""
        ranked: List[Tuple[AHCECandidate, float, str]] = []
        feat = signature.features
        min_dim = min(feat.dimensions) if feat.dimensions else 1
        eff_rank = feat.estimated_effective_rank or min_dim
        rank_ratio = float(eff_rank / max(1, min_dim))

        for cand in candidates:
            prior = self._strategy_priors.get(cand.strategy_name, {"successes": 1.0, "total": 2.0})
            win_rate = prior["successes"] / max(1.0, prior["total"])

            score = cand.predicted_work_reduction * win_rate
            explanation = f"Base win rate {win_rate*100:.1f}%; predicted work reduction {cand.predicted_work_reduction*100:.1f}%."

            # Structure-informed boost
            if cand.strategy_name == "low_rank_svd":
                if rank_ratio < 0.20:
                    score += 0.4
                    explanation += f" Boosted by low intrinsic rank ratio ({rank_ratio:.2f} < 0.20)."
                else:
                    score -= 0.5
                    explanation += f" Penalized by high intrinsic rank ratio ({rank_ratio:.2f} >= 0.20)."

            if cand.strategy_name == "sparse_csr":
                if feat.sparsity >= 0.70:
                    score += 0.4
                    explanation += f" Boosted by high sparsity ({feat.sparsity*100:.1f}% >= 70%)."
                else:
                    score -= 0.5
                    explanation += f" Penalized by low sparsity ({feat.sparsity*100:.1f}% < 70%)."

            ranked.append((cand, score, explanation))

        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked
