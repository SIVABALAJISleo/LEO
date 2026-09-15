"""
hyper_x/ahce/holdout.py
======================
Blind Holdout Evaluator for AHCE (Section 27).

Splits evaluation workloads into discovery, validation, and blind holdout partitions.
Measures generalization gap: Delta_gen = |Score_val - Score_holdout|
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Tuple
import numpy as np

from .contract import AHCEContract, CorrectnessClass
from .evaluator import AHCECandidateEvaluator
from .candidate import AHCECandidate, AHCETrialResult
from .strategy_registry import AHCEStrategyRegistry


@dataclass
class AHCEHoldoutResult:
    candidate_id: str
    strategy_name: str
    validation_work_reduction_pct: float
    holdout_work_reduction_pct: float
    generalization_gap_pct: float
    holdout_verified: bool
    passed: bool
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AHCEHoldoutEvaluator:
    """Evaluates candidates against strictly sequestered holdout tensors."""

    def __init__(self, registry: AHCEStrategyRegistry):
        self.registry = registry
        self.evaluator = AHCECandidateEvaluator(registry)

    def evaluate_holdout(
        self,
        candidate: AHCECandidate,
        contract: AHCEContract,
        validation_reduction: float,
        holdout_rank: int = 16
    ) -> AHCEHoldoutResult:
        # Generate unseen holdout matrix with distinct seed and aspect ratio (e.g. non-square 384 x 256)
        np.random.seed(888)
        M, K, N = 384, 256, 192
        r = holdout_rank
        A_holdout = (np.random.randn(M, r) @ np.random.randn(r, K)).astype(np.float32)
        B_holdout = np.random.randn(K, N).astype(np.float32)
        ref_holdout = A_holdout @ B_holdout

        res = self.evaluator.evaluate_candidate(
            candidate, A_holdout, B_holdout, contract, ref_holdout, reference_latency_ms=5.0
        )

        holdout_red = res.work_reduction_pct
        gap = abs(validation_reduction - holdout_red)
        passed = res.verified and (gap <= 15.0)

        return AHCEHoldoutResult(
            candidate_id=candidate.candidate_id,
            strategy_name=candidate.strategy_name,
            validation_work_reduction_pct=round(validation_reduction, 2),
            holdout_work_reduction_pct=round(holdout_red, 2),
            generalization_gap_pct=round(gap, 2),
            holdout_verified=res.verified,
            passed=passed,
            notes="Generalization confirmed on unseen aspect ratios and seeds."
            if passed
            else f"Generalization gap too wide ({gap:.1f}%) or verification failed."
        )
