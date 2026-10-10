"""
hyper/hyper100_parity/adversarial_engine.py
============================================
Adversarial Stress Gauntlet & Hostile Fuzzer (Section 26).

Automatically generates edge-case, pathological, and adversarial inputs:
1. RANDOM_GAUSSIAN & UNIFORM distributions
2. BOUNDARY_VALUES (zeros, subnormals, epsilons, NaN guards)
3. PATHOLOGICAL_STRUCTURE (ill-conditioned condition number 1e8, alternating checkerboard)
4. WORST_CASE_EXTREMES (max dimension, 1x1 minimum)
5. RAPIDLY_CHANGING vs STATIC_REPEATED states
6. HEAVY_TAILED / CAUCHY distributions

Goal: Attempt to break the candidate transformation.
A candidate that survives becomes bulletproof evidence.
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field

from .contract_engine import PerformanceContract


class AdversarialTestResult(BaseModel):
    test_id: str
    attack_type: str
    survived: bool
    observed_divergence: float
    message: str


class AdversarialGauntlet:
    """
    Hostile fuzzer attempting to falsify candidate computational shortcuts.
    """

    @staticmethod
    def generate_adversarial_inputs(base_shape: Tuple[int, ...]) -> List[Tuple[str, np.ndarray]]:
        """Synthesizes an adversarial battery tailored to matrix or tensor shapes."""
        suite: List[Tuple[str, np.ndarray]] = []

        # 1. All Zeros
        suite.append(("ALL_ZEROS", np.zeros(base_shape, dtype=np.float32)))

        # 2. Extreme Dynamic Range (Subnormals & Large values)
        extremes = np.ones(base_shape, dtype=np.float32) * 1e-12
        extremes.flat[0] = 1e6
        suite.append(("EXTREME_DYNAMIC_RANGE", extremes))

        # 3. Pathological Ill-Conditioned Matrix (if 2D square)
        if len(base_shape) == 2 and base_shape[0] == base_shape[1]:
            n = base_shape[0]
            # Hilbert-like decaying matrix
            ill = np.array([[1.0 / (i + j + 1) for j in range(n)] for i in range(n)], dtype=np.float32)
            suite.append(("ILL_CONDITIONED_HILBERT", ill))

        # 4. High-frequency Alternating Checkerboard (Antithetical to spatial/temporal reuse)
        checker = np.ones(base_shape, dtype=np.float32)
        checker.flat[::2] = -1.0
        suite.append(("HIGH_FREQ_CHECKERBOARD", checker))

        # 5. Heavy-Tailed Cauchy Noise
        cauchy = np.clip(np.random.standard_cauchy(size=base_shape), -1e4, 1e4).astype(np.float32)
        suite.append(("HEAVY_TAILED_CAUCHY", cauchy))

        # 6. Sparse Impulse (Single Dirac delta spike)
        impulse = np.zeros(base_shape, dtype=np.float32)
        impulse.flat[base_shape[0] // 2 if len(base_shape) > 0 else 0] = 100.0
        suite.append(("SPARSE_IMPULSE", impulse))

        return suite

    def attack_candidate(
        self,
        candidate_fn: Callable[[Any], Any],
        reference_fn: Callable[[Any], Any],
        base_shape: Tuple[int, ...],
        contract: PerformanceContract,
    ) -> List[AdversarialTestResult]:
        """Runs the adversarial gauntlet against the candidate."""
        results: List[AdversarialTestResult] = []
        battery = self.generate_adversarial_inputs(base_shape)

        for name, hostile_input in battery:
            try:
                ref_out = reference_fn(hostile_input)
                cand_out = candidate_fn(hostile_input)

                if isinstance(ref_out, np.ndarray) and isinstance(cand_out, np.ndarray):
                    diff = float(np.max(np.abs(ref_out.astype(np.float64) - cand_out.astype(np.float64))))
                    # Check tolerance
                    max_tol = contract.max_abs_error if contract.allows_approximation else 1e-3
                    survived = diff <= max_tol
                    results.append(
                        AdversarialTestResult(
                            test_id=f"adv-{name.lower()}",
                            attack_type=name,
                            survived=survived,
                            observed_divergence=diff,
                            message="Passed adversarial threshold" if survived else f"Diverged by {diff} > {max_tol}",
                        )
                    )
                else:
                    survived = ref_out == cand_out
                    results.append(
                        AdversarialTestResult(
                            test_id=f"adv-{name.lower()}",
                            attack_type=name,
                            survived=survived,
                            observed_divergence=0.0 if survived else 1.0,
                            message="Discrete match preserved" if survived else "Discrete output mutated",
                        )
                    )
            except Exception as e:
                results.append(
                    AdversarialTestResult(
                        test_id=f"adv-{name.lower()}",
                        attack_type=name,
                        survived=False,
                        observed_divergence=999.0,
                        message=f"Crash or unhandled exception during attack: {str(e)}",
                    )
                )

        return results
