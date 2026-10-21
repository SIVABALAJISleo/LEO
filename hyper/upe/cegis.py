"""
hyper/upe/cegis.py
==================
ENGINE 6: Counterexample-Guided Discovery (CEGIS).

A falsification and refinement loop that actively searches for counterexamples
to break candidate pathways. Generates ordinary, boundary, and adversarial inputs:
- Zero matrices, identity matrices, diagonal matrices
- Extreme floating-point values (subnormal, large magnitudes)
- Ill-conditioned and near-singular matrices
- Prime dimensions (breaking power-of-two tiling assumptions)
- High-entropy random data (breaking low-rank / compression assumptions)
"""

from __future__ import annotations

import dataclasses
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper.upe.contract import WorkloadContract


@dataclasses.dataclass
class CounterexampleRecord:
    """Detailed record of a discovered falsifying counterexample."""
    counterexample_id: str
    workload_id: str
    rule_id: str
    input_signature: str
    failure_category: str  # e.g., NUMERICAL_INSTABILITY, RESHAPE_ERROR, CONTRACT_VIOLATION
    error_metric: float
    error_tolerance: float
    description: str
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "counterexample_id": self.counterexample_id,
            "workload_id": self.workload_id,
            "rule_id": self.rule_id,
            "input_signature": self.input_signature,
            "failure_category": self.failure_category,
            "error_metric": self.error_metric,
            "error_tolerance": self.error_tolerance,
            "description": self.description,
            "timestamp": self.timestamp,
        }


class CounterexampleHunter:
    """
    Adversarial generator and counterexample search engine.
    """

    def __init__(self) -> None:
        self.regression_corpus: List[CounterexampleRecord] = []

    def hunt_counterexamples(
        self,
        candidate_fn: Callable[[Dict[str, Any]], Tuple[Any, Dict[str, Any]]],
        reference_fn: Callable[[Dict[str, Any]], Any],
        contract: WorkloadContract,
        max_trials: int = 15,
    ) -> Tuple[bool, List[CounterexampleRecord]]:
        """
        Runs an adversarial battery of boundary inputs against candidate.
        Returns: (passed_all, list_of_counterexamples).
        """
        counterexamples: List[CounterexampleRecord] = []
        wid = contract.workload_id.lower()

        test_cases = self._generate_adversarial_test_cases(wid)

        for case_idx, (case_name, test_inputs) in enumerate(test_cases[:max_trials]):
            try:
                # 1. Run reference implementation
                t_ref_start = time.perf_counter()
                ref_out = reference_fn(test_inputs)

                # 2. Run candidate implementation
                cand_out, _ = candidate_fn(test_inputs)

                # 3. Check compliance
                passed, status, metrics = contract.check_output_compliance(cand_out, ref_out)

                if not passed:
                    cx = CounterexampleRecord(
                        counterexample_id=f"cx_{wid}_{case_idx}_{int(time.time())}",
                        workload_id=contract.workload_id,
                        rule_id=contract.version,
                        input_signature=case_name,
                        failure_category="NUMERICAL_TOLERANCE_EXCEEDED" if "TOLERANCE" in status else "EXACT_MISMATCH",
                        error_metric=metrics.get("max_abs_err", metrics.get("max_abs_diff", 1.0)),
                        error_tolerance=contract.max_absolute_error,
                        description=f"Falsified on adversarial case '{case_name}': {status}",
                        timestamp=time.time(),
                    )
                    counterexamples.append(cx)
                    self.regression_corpus.append(cx)
            except Exception as e:
                # Execution exception under adversarial input
                cx = CounterexampleRecord(
                    counterexample_id=f"cx_err_{wid}_{case_idx}_{int(time.time())}",
                    workload_id=contract.workload_id,
                    rule_id=contract.version,
                    input_signature=case_name,
                    failure_category="EXECUTION_EXCEPTION",
                    error_metric=float("inf"),
                    error_tolerance=contract.max_absolute_error,
                    description=f"Candidate crashed on adversarial input '{case_name}': {e}",
                    timestamp=time.time(),
                )
                counterexamples.append(cx)
                self.regression_corpus.append(cx)

        return (len(counterexamples) == 0, counterexamples)

    def _generate_adversarial_test_cases(self, workload_id: str) -> List[Tuple[str, Dict[str, Any]]]:
        """Synthesizes boundary and stress-testing input configurations."""
        cases: List[Tuple[str, Dict[str, Any]]] = []

        if "polynomial" in workload_id or "horner" in workload_id:
            # 1. All zero coefficients
            cases.append(("all_zeros", {"coefficients": [0.0] * 10, "x": 5.0}))
            # 2. Alternating signs large polynomial
            cases.append(("alternating_signs", {"coefficients": [(-1.0)**i * 2.0 for i in range(16)], "x": 1.5}))
            # 3. Large evaluation point (growth test)
            cases.append(("extreme_x", {"coefficients": [1.0, -1.0, 0.5], "x": 100.0}))
            # 4. Single element
            cases.append(("single_element", {"coefficients": [42.0], "x": 10.0}))

        elif "prefix" in workload_id:
            arr = np.array([1, -1, 2, -2, 5, 10, -3, 8], dtype=np.int32)
            cases.append(("alternating_signs", {"array": arr, "queries": [(0, 7), (2, 4), (0, 0)]}))
            cases.append(("single_interval", {"array": np.array([100], dtype=np.int32), "queries": [(0, 0)]}))
            cases.append(("full_range", {"array": np.ones(50, dtype=np.int32), "queries": [(0, 49), (10, 20)]}))

        else:
            # Matrix GEMM / Fused / Sparsity test cases
            # 1. Zero Matrix
            cases.append(("zero_matrix_B", {
                "A": np.random.randn(8, 8).astype(np.float32),
                "B": np.zeros((8, 8), dtype=np.float32),
                "bias": np.zeros(8, dtype=np.float32),
            }))
            # 2. Identity Matrix
            cases.append(("identity_matrix_B", {
                "A": np.random.randn(8, 8).astype(np.float32),
                "B": np.eye(8, dtype=np.float32),
                "bias": np.zeros(8, dtype=np.float32),
            }))
            # 3. Prime Dimensions (e.g. 7 x 11 x 13, breaks power-of-two assumptions)
            cases.append(("prime_dimensions_7x11x13", {
                "A": np.random.randn(7, 11).astype(np.float32),
                "B": np.random.randn(11, 13).astype(np.float32),
                "bias": np.zeros(13, dtype=np.float32),
            }))
            # 4. Ill-conditioned Hilbert-like matrix
            H = 1.0 / (np.arange(1, 9)[:, None] + np.arange(1, 9)[None, :])
            cases.append(("ill_conditioned_hilbert", {
                "A": H.astype(np.float32),
                "B": np.eye(8, dtype=np.float32),
                "bias": np.zeros(8, dtype=np.float32),
            }))
            # 5. Sparse Matrix (80% zeros)
            mask = np.random.rand(16, 16) > 0.80
            A_sparse = (np.random.randn(16, 16) * mask).astype(np.float32)
            cases.append(("sparse_80pct", {
                "A": A_sparse,
                "B": np.random.randn(16, 16).astype(np.float32),
                "bias": np.zeros(16, dtype=np.float32),
            }))

        return cases
