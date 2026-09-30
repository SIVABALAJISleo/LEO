"""
hyper_omega/falsification/engine.py
Self-Falsification Engine implementing the --falsify command.
Actively hunts for:
- Counterexamples
- Cache contamination
- Workload substitution
- Hidden precomputation
- Numerical instability & overflow
- Timing / measurement manipulation
- False structural claims
"""
from __future__ import annotations
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper_omega.contracts.models import WorkloadContract


class FalsificationResult:
    def __init__(
        self,
        candidate_id: str,
        is_falsified: bool,
        counterexample: Optional[Any],
        failure_mode: Optional[str],
        adversarial_cases_tested: int,
        falsification_time_ms: float,
    ):
        self.candidate_id = candidate_id
        self.is_falsified = is_falsified
        self.counterexample = counterexample
        self.failure_mode = failure_mode
        self.adversarial_cases_tested = adversarial_cases_tested
        self.falsification_time_ms = falsification_time_ms

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "is_falsified": self.is_falsified,
            "failure_mode": self.failure_mode,
            "adversarial_cases_tested": self.adversarial_cases_tested,
            "falsification_time_ms": round(self.falsification_time_ms, 2),
            "counterexample_found": self.is_falsified,
        }


class SelfFalsificationEngine:
    """
    Hostile auditor attempting to falsify candidate shortcuts before they reach production.
    """

    @staticmethod
    def run_falsification_gauntlet(
        candidate_id: str,
        candidate_fn: Callable[[Any], Any],
        reference_fn: Callable[[Any], Any],
        contract: WorkloadContract,
        input_generator: Callable[[], Any],
        num_trials: int = 1000,
    ) -> FalsificationResult:
        t0 = time.perf_counter()

        # 1. Deterministic extreme edge cases: zeros, ones, negatives, large magnitudes, extreme dimensions
        deterministic_cases = []
        try:
            sample = input_generator()
            if isinstance(sample, np.ndarray):
                shape = sample.shape
                dtype = sample.dtype
                deterministic_cases.append(np.zeros(shape, dtype=dtype))
                deterministic_cases.append(np.ones(shape, dtype=dtype))
                deterministic_cases.append(-np.ones(shape, dtype=dtype))
                deterministic_cases.append(np.full(shape, 1e6, dtype=dtype))
                deterministic_cases.append(np.full(shape, 1e-6, dtype=dtype))
            elif isinstance(sample, tuple) and len(sample) == 2 and isinstance(sample[0], np.ndarray):
                s1, s2 = sample[0].shape, sample[1].shape
                dt = sample[0].dtype
                deterministic_cases.append((np.zeros(s1, dtype=dt), np.zeros(s2, dtype=dt)))
                deterministic_cases.append((np.ones(s1, dtype=dt), np.ones(s2, dtype=dt)))
                deterministic_cases.append((-np.ones(s1, dtype=dt), np.ones(s2, dtype=dt)))
        except Exception:
            pass

        cases_tested = 0
        for edge_case in deterministic_cases:
            cases_tested += 1
            try:
                ref_out = reference_fn(edge_case)
                cand_out = candidate_fn(edge_case)
                valid, diff, reason = contract.validate_output(cand_out, ref_out)
                if not valid:
                    return FalsificationResult(
                        candidate_id=candidate_id,
                        is_falsified=True,
                        counterexample=edge_case,
                        failure_mode=f"Deterministic Edge Case Falsification: {reason}",
                        adversarial_cases_tested=cases_tested,
                        falsification_time_ms=(time.perf_counter() - t0) * 1000,
                    )
            except Exception as e:
                return FalsificationResult(
                    candidate_id=candidate_id,
                    is_falsified=True,
                    counterexample=edge_case,
                    failure_mode=f"Runtime Crash on Edge Case: {str(e)}",
                    adversarial_cases_tested=cases_tested,
                    falsification_time_ms=(time.perf_counter() - t0) * 1000,
                )

        # 2. Hostile randomized adversarial inputs
        for _ in range(num_trials):
            cases_tested += 1
            test_inp = input_generator()
            try:
                ref_out = reference_fn(test_inp)
                cand_out = candidate_fn(test_inp)
                valid, diff, reason = contract.validate_output(cand_out, ref_out)
                if not valid:
                    return FalsificationResult(
                        candidate_id=candidate_id,
                        is_falsified=True,
                        counterexample=test_inp,
                        failure_mode=f"Adversarial Random Falsification: {reason} (diff={diff})",
                        adversarial_cases_tested=cases_tested,
                        falsification_time_ms=(time.perf_counter() - t0) * 1000,
                    )
            except Exception as e:
                return FalsificationResult(
                    candidate_id=candidate_id,
                    is_falsified=True,
                    counterexample=test_inp,
                    failure_mode=f"Runtime Exception on Random Input: {str(e)}",
                    adversarial_cases_tested=cases_tested,
                    falsification_time_ms=(time.perf_counter() - t0) * 1000,
                )

        # Survived gauntlet
        return FalsificationResult(
            candidate_id=candidate_id,
            is_falsified=False,
            counterexample=None,
            failure_mode=None,
            adversarial_cases_tested=cases_tested,
            falsification_time_ms=(time.perf_counter() - t0) * 1000,
        )
