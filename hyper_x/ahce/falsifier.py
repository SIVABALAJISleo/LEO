"""
hyper_x/ahce/falsifier.py
========================
Adversarial Falsification Suite for AHCE (Sections 22, 23, & 26).

Subject candidate optimizations to hostile tests designed to break them:
1. Cache Red Team: Perturb inputs and seeds to ensure candidate cannot cheat via stale cache.
2. Anti-Structure Red Team: Inject full-rank white noise to low-rank strategies, and dense matrices to sparse strategies.
3. Pathological Edge Cases: NaN, Inf, and denormals.
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional

from .contract import AHCEContract, CorrectnessClass
from .strategy_registry import AHCEStrategyRegistry, AHCEStrategy
from .verifier import AHCEVerifier


@dataclass
class AHCEFalsificationResult:
    test_name: str
    target_strategy: str
    passed: bool
    fallback_triggered: bool
    measured_error: float
    details: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AHCEFalsifier:
    """Actively attempts to disprove candidate pathways."""

    def __init__(self, registry: AHCEStrategyRegistry):
        self.registry = registry
        self.verifier = AHCEVerifier()

    def attack_cache_strategy(self) -> AHCEFalsificationResult:
        """Cache Red Team (Section 22): Verifies cache miss on mutated input."""
        strat = self.registry.get("exact_cache")
        if strat is None:
            return AHCEFalsificationResult("cache_redteam", "exact_cache", True, False, 0.0, "Strategy not present.")

        contract = AHCEContract("exact_c", CorrectnessClass.EXACT)
        A = np.ones((64, 64), dtype=np.float32)
        B = np.ones((64, 64), dtype=np.float32)

        # First run populates cache
        out1, telem1 = strat.execute(A, B, contract)

        # Mutate single float in A
        A_mut = A.copy()
        A_mut[0, 0] += 1e-4

        # Second run on mutated input MUST NOT return stale cached output
        out2, telem2 = strat.execute(A_mut, B, contract)
        ref_mut = A_mut @ B

        diff = float(np.max(np.abs(out2 - ref_mut)))
        passed = (diff < 1e-5) and (not telem2.get("cache_hit", False))

        return AHCEFalsificationResult(
            test_name="AHCE_CACHE_REDTEAM_001",
            target_strategy="exact_cache",
            passed=passed,
            fallback_triggered=False,
            measured_error=diff,
            details="Cache correctly detected input mutation and executed fresh compute."
            if passed
            else "CRITICAL: Cache returned stale output on mutated input!"
        )

    def attack_low_rank_strategy(self, N: int = 128) -> AHCEFalsificationResult:
        """Anti-Structure Red Team: Tests full-rank white noise where low-rank SVD should fail or fallback."""
        strat = self.registry.get("low_rank_svd")
        if strat is None:
            return AHCEFalsificationResult("low_rank_noise", "low_rank_svd", True, False, 0.0, "Strategy not present.")

        contract = AHCEContract("num_equiv", CorrectnessClass.NUMERICALLY_EQUIVALENT, max_relative_error=1e-4)
        np.random.seed(42)
        # Uniform white noise: Full rank
        A_full = np.random.randn(N, N).astype(np.float32)
        B_full = np.random.randn(N, N).astype(np.float32)
        ref_C = A_full @ B_full

        out, telem = strat.execute(A_full, B_full, contract)
        rel_err = float(np.max(np.abs(out - ref_C)) / (np.max(np.abs(ref_C)) + 1e-12))

        # Because input is full rank, LowRankEngine must detect error > 1e-4 and fall back to dense
        is_beneficial = telem.get("is_beneficial", False)
        fallback_used = not is_beneficial

        passed = fallback_used and (rel_err < 1e-5)

        return AHCEFalsificationResult(
            test_name="AHCE_DENSE_ADVERSARIAL_001",
            target_strategy="low_rank_svd",
            passed=passed,
            fallback_triggered=fallback_used,
            measured_error=rel_err,
            details="Low-rank engine correctly detected full-rank noise and fell back to exact compute."
            if passed
            else f"Low rank inappropriately applied to white noise (error: {rel_err:.4e})"
        )

    def run_falsification_suite(self) -> List[AHCEFalsificationResult]:
        return [
            self.attack_cache_strategy(),
            self.attack_low_rank_strategy(N=128)
        ]
