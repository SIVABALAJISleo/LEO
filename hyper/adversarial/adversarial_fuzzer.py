"""
hyper/adversarial/adversarial_fuzzer.py
=======================================
Adversarial Fuzzing and 4-Way Blind Holdout Test Suite for LEO/HYPER.
Fulfills Section 24, 25, 42, 43, 58:
Generates pathological inputs (zeros, inf, nan, subnormals, ill-conditioned matrices,
boundary values) and splits test suites into Discovery, Validation, Adversarial, and Holdout sets.
"""

from __future__ import annotations
import math
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper.semantics.types import DataType


@dataclass
class FuzzCampaignResult:
    total_tests: int
    passed_tests: int
    failed_tests: int
    counterexamples: List[Dict[str, Any]] = field(default_factory=list)
    max_absolute_error: float = 0.0
    elapsed_seconds: float = 0.0

    @property
    def pass_rate_pct(self) -> float:
        return (self.passed_tests / max(1, self.total_tests)) * 100.0


class AdversarialFuzzer:
    """
    Hostile test generator and fuzzing campaign coordinator.
    """

    def __init__(self, seed: int = 1337) -> None:
        self.rng = np.random.RandomState(seed)

    def generate_corner_cases(
        self,
        shape: Tuple[int, ...],
        dtype: DataType = DataType.FP32,
    ) -> List[np.ndarray]:
        """
        Generates comprehensive boundary and pathological test arrays.
        """
        cases: List[np.ndarray] = []
        np_dt = dtype.to_numpy_dtype()

        # 1. Exact Zeros
        cases.append(np.zeros(shape, dtype=np_dt))

        # 2. Exact Ones
        cases.append(np.ones(shape, dtype=np_dt))

        # 3. Signed Zeros (-0.0)
        neg_zero = np.zeros(shape, dtype=np_dt)
        if dtype.is_floating_point:
            neg_zero = np.copysign(neg_zero, -1.0)
        cases.append(neg_zero)

        if dtype.is_floating_point:
            # 4. Infinities (+inf, -inf)
            inf_pos = np.full(shape, np.inf, dtype=np_dt)
            inf_neg = np.full(shape, -np.inf, dtype=np_dt)
            cases.append(inf_pos)
            cases.append(inf_neg)

            # 5. NaNs
            nan_arr = np.full(shape, np.nan, dtype=np_dt)
            cases.append(nan_arr)

            # 6. Subnormal numbers
            subnorm_val = 1e-40 if dtype == DataType.FP32 else 1e-315
            cases.append(np.full(shape, subnorm_val, dtype=np_dt))

            # 7. Extreme dynamic range (1e-25 to 1e25)
            extreme = self.rng.uniform(-1e15, 1e15, size=shape).astype(np_dt)
            cases.append(extreme)

            # 8. Ill-Conditioned / Degenerate Matrix (if 2D)
            if len(shape) == 2 and shape[0] == shape[1]:
                N = shape[0]
                # Hilbert matrix (classic high condition number)
                hilbert = np.fromfunction(lambda i, j: 1.0 / (i + j + 1.0), (N, N), dtype=np_dt)
                cases.append(hilbert)

                # Rank-1 Degenerate Matrix
                u = self.rng.randn(N, 1).astype(np_dt)
                v = self.rng.randn(1, N).astype(np_dt)
                cases.append(np.matmul(u, v))

        elif dtype.is_integer:
            # Fixed width integer boundaries: min, max, -1, 0, 1
            info = np.iinfo(np_dt)
            cases.append(np.full(shape, info.min, dtype=np_dt))
            cases.append(np.full(shape, info.max, dtype=np_dt))
            cases.append(np.full(shape, -1, dtype=np_dt))

        return cases

    def generate_4way_split(
        self,
        shape: Tuple[int, ...],
        dtype: DataType = DataType.FP32,
        num_discovery: int = 10,
        num_val: int = 10,
        num_adv: int = 10,
        num_holdout: int = 20,
    ) -> Dict[str, List[np.ndarray]]:
        """
        Strict 4-way data partition ensuring candidate is never tuned on holdout set.
        """
        np_dt = dtype.to_numpy_dtype()

        def make_samples(n: int) -> List[np.ndarray]:
            return [self.rng.randn(*shape).astype(np_dt) for _ in range(n)]

        adv_samples = self.generate_corner_cases(shape, dtype)
        while len(adv_samples) < num_adv:
            adv_samples.append(self.rng.exponential(scale=10.0, size=shape).astype(np_dt))

        return {
            "discovery": make_samples(num_discovery),
            "validation": make_samples(num_val),
            "adversarial": adv_samples[:num_adv],
            "blind_holdout": make_samples(num_holdout),
        }

    def run_fuzz_campaign(
        self,
        candidate_fn: Callable[[np.ndarray], np.ndarray],
        reference_fn: Callable[[np.ndarray], np.ndarray],
        shape: Tuple[int, ...],
        num_tests: int = 10000,
        tolerance: float = 1e-4,
    ) -> FuzzCampaignResult:
        """
        Section 43: Runs a 10,000-sample randomized and hostile fuzzing campaign.
        """
        t0 = time.perf_counter()
        passed = 0
        failed = 0
        counterexamples: List[Dict[str, Any]] = []
        max_abs = 0.0

        for trial in range(num_tests):
            # Interleave boundary cases and random inputs
            if trial % 20 == 0:
                test_in = self.rng.choice([0.0, 1.0, -1.0, 1e-5, 1e5]) * np.ones(shape, dtype=np.float32)
            elif trial % 50 == 0:
                test_in = self.rng.uniform(-1e4, 1e4, size=shape).astype(np.float32)
            else:
                test_in = self.rng.randn(*shape).astype(np.float32)

            try:
                ref_out = reference_fn(test_in)
                cand_out = candidate_fn(test_in)

                diff = np.abs(cand_out.astype(np.float64) - ref_out.astype(np.float64))
                cur_abs = float(np.nanmax(diff)) if diff.size > 0 else 0.0
                if cur_abs > max_abs:
                    max_abs = cur_abs

                if cur_abs <= tolerance or np.array_equal(cand_out, ref_out, equal_nan=True):
                    passed += 1
                else:
                    failed += 1
                    if len(counterexamples) < 10:
                        counterexamples.append({
                            "trial": trial,
                            "error": cur_abs,
                            "tolerance": tolerance,
                        })
            except Exception as e:
                failed += 1
                if len(counterexamples) < 10:
                    counterexamples.append({"trial": trial, "crash": str(e)})

        elapsed = time.perf_counter() - t0
        return FuzzCampaignResult(
            total_tests=num_tests,
            passed_tests=passed,
            failed_tests=failed,
            counterexamples=counterexamples,
            max_absolute_error=max_abs,
            elapsed_seconds=elapsed,
        )
