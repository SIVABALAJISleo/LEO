"""
hyper_x/gauntlets/anti_structure.py
===================================
HYPER Anti-Structure & Falsification Gauntlet (Part 32).

Every claimed breakthrough must face anti-structural stress:
- Claim LOW_RANK        -> Test FULL_RANK (random noise, singular values flat)
- Claim SPARSE          -> Test FULL_DENSE (100% non-zero random matrix)
- Claim TEMPORAL_REUSE  -> Test RANDOMIZED_FRAMES (zero temporal coherence)
- Claim CACHE_REUSE     -> Test NOVEL_INPUT (cache miss)
- Claim PREDICTION      -> Test ADVERSARIAL_INPUT (pathological distribution shift)

Validates that:
1. The engine does NOT apply an invalid shortcut to anti-structural data.
2. The verification layer catches errors and triggers safe fallback.
3. Zero corrupted results are emitted.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, asdict
from typing import Dict, Any, List
import numpy as np
from hyper.low_rank.low_rank_engine import LowRankEngine
from hyper.sparsity.sparsity_engine import SparsityEngine
from hyper.cache.exact_cache import ExactCache, compute_cache_key


@dataclass
class AntiStructureResult:
    test_name: str
    claimed_property: str
    anti_structure_input: str
    shortcut_applied: bool
    fallback_triggered: bool
    correctness_preserved: bool
    measured_error: float
    passed_falsification: bool
    details: str


class AntiStructureGauntlet:
    """Attacks every optimization with inputs designed to break its structural assumptions."""

    def __init__(self):
        self.results: List[AntiStructureResult] = []

    def attack_low_rank(self, N: int = 128) -> AntiStructureResult:
        """
        Input has singular values distributed uniformly (Full Rank).
        If Low-Rank SVD is forced with small rank r=8, error must exceed threshold
        and trigger fallback to exact compute.
        """
        np.random.seed(999)
        A_full = np.random.randn(N, N).astype(np.float32)
        B_full = np.random.randn(N, N).astype(np.float32)
        ref_C = A_full @ B_full

        engine = LowRankEngine(default_rank=8)
        # Execute with low error tolerance (1e-4) on full rank input
        out_C, telem = engine.benchmark_and_execute(
            A_full, B_full, rank=8, max_allowed_rel_error=1e-4
        )

        err = float(np.max(np.abs(out_C - ref_C)) / (np.max(np.abs(ref_C)) + 1e-12))
        is_beneficial = telem.get("is_beneficial", False)
        fallback_triggered = not is_beneficial

        passed = (fallback_triggered and err < 1e-5) or (err <= 1e-4)
        details = (
            "Correctly rejected low-rank shortcut on full-rank input; executed exact dense compute."
            if fallback_triggered
            else f"Low rank applied with relative error {err:.4e}"
        )

        res = AntiStructureResult(
            test_name="anti_structure_full_rank",
            claimed_property="LOW_RANK",
            anti_structure_input="Uniform full-rank random matrix",
            shortcut_applied=is_beneficial,
            fallback_triggered=fallback_triggered,
            correctness_preserved=err < 1e-4,
            measured_error=err,
            passed_falsification=passed,
            details=details
        )
        self.results.append(res)
        return res

    def attack_sparse(self, N: int = 128) -> AntiStructureResult:
        """
        Input is 100% dense (zero zeros).
        SparsityEngine must measure overhead, detect sparsity=0, and refuse sparse CSR format.
        """
        np.random.seed(999)
        A_dense = np.random.randn(N, N).astype(np.float32) + 2.0  # Zero zeros
        B_dense = np.random.randn(N, N).astype(np.float32)
        ref_C = A_dense @ B_dense

        engine = SparsityEngine(default_threshold=1e-6)
        out_C, telem = engine.execute_with_overhead_check(A_dense, B_dense, threshold=1e-6)

        err = float(np.max(np.abs(out_C - ref_C)) / (np.max(np.abs(ref_C)) + 1e-12))
        path_chosen = telem.get("path_chosen", "EXACT")
        faster_than_dense = telem.get("faster_than_dense", False)

        passed = (path_chosen == "EXACT" or not faster_than_dense) and err < 1e-5
        details = f"Path chosen: {path_chosen}; density: {telem.get('density', 1.0):.2f}"

        res = AntiStructureResult(
            test_name="anti_structure_full_dense",
            claimed_property="SPARSE",
            anti_structure_input="100% non-zero dense Gaussian tensor",
            shortcut_applied=faster_than_dense,
            fallback_triggered=not faster_than_dense,
            correctness_preserved=err < 1e-5,
            measured_error=err,
            passed_falsification=passed,
            details=details
        )
        self.results.append(res)
        return res

    def attack_cache(self) -> AntiStructureResult:
        """
        Input tensor altered by infinitesimal perturbation (1e-5).
        ExactIdentityCache must return CACHE_MISS and NOT return stale cached output.
        """
        cache = ExactCache()
        t1 = np.ones((64, 64), dtype=np.float32)
        key1 = compute_cache_key(t1, model_identifier="model_v1")
        cache.put(key1, np.ones((64, 64), dtype=np.float32) * 5.0)

        # Alter input slightly
        t2 = t1.copy()
        t2[0, 0] += 1e-4
        key2 = compute_cache_key(t2, model_identifier="model_v1")

        cached_val, is_hit, _ = cache.get(key2)
        passed = (not is_hit) and (cached_val is None)  # Must be a miss!

        res = AntiStructureResult(
            test_name="anti_structure_cache_mutation",
            claimed_property="CACHE_REUSE",
            anti_structure_input="Infinitesimally mutated tensor (1e-4 delta)",
            shortcut_applied=cached_val is not None,
            fallback_triggered=cached_val is None,
            correctness_preserved=passed,
            measured_error=0.0,
            passed_falsification=passed,
            details="Cache correctly returned MISS on altered input hash." if passed else "CRITICAL: Cache returned false hit on altered input!"
        )
        self.results.append(res)
        return res

    def run_all(self) -> List[Dict[str, Any]]:
        self.attack_low_rank()
        self.attack_sparse()
        self.attack_cache()
        return [asdict(r) for r in self.results]
