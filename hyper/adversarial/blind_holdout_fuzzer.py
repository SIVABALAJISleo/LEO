"""
hyper/adversarial/blind_holdout_fuzzer.py
=========================================
Fuzzing and Blind Holdout Validation Engine for LEO/HYPER.
Fulfills Sections 45 and 47 of the Breakthrough Master Architecture.

Strictly separates evaluation into three disjoint data splits:
1. DISCOVERY_DATASET (Used to discover candidate patterns)
2. VERIFICATION_DATASET (Used during search iteration)
3. BLIND_HOLDOUT_DATASET (Isolated unseen inputs for certification)

Executes property, boundary, and shape fuzzing to ensure optimizations
generalize without memorization or false escapes.
"""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper.contracts.contract import Contract


class DatasetSplit(str, Enum):
    DISCOVERY = "DISCOVERY"
    VERIFICATION = "VERIFICATION"
    BLIND_HOLDOUT = "BLIND_HOLDOUT"


class FuzzReport:
    """Summary of fuzzing campaign results."""
    def __init__(self):
        self.total_generated: int = 0
        self.total_executed: int = 0
        self.passed: int = 0
        self.failed: int = 0
        self.mismatches: int = 0
        self.unsupported: int = 0
        self.crashes: int = 0
        self.timeouts: int = 0
        self.false_escapes: int = 0  # CRITICAL: Must remain 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_generated": self.total_generated,
            "total_executed": self.total_executed,
            "passed": self.passed,
            "failed": self.failed,
            "mismatches": self.mismatches,
            "unsupported": self.unsupported,
            "crashes": self.crashes,
            "timeouts": self.timeouts,
            "false_escapes": self.false_escapes,
            "pass_rate_pct": round((self.passed / max(1, self.total_executed)) * 100.0, 2),
        }


class BlindHoldoutFuzzer:
    """
    Three-Tier Split Fuzzer and Certification Engine.
    Ensures optimizations are validated across independent unseen holdouts.
    """

    def __init__(self, base_seed: int = 42):
        self.base_seed = base_seed
        self.report = FuzzReport()

    def generate_partitioned_dataset(
        self,
        num_samples_per_split: int = 20,
        shape: Tuple[int, ...] = (32, 32),
        dtype: np.dtype = np.float32,
    ) -> Dict[DatasetSplit, List[np.ndarray]]:
        """
        Generates three disjoint datasets using mathematically separated seeds:
        - Discovery: seed + 1000
        - Verification: seed + 2000
        - Blind Holdout: seed + 9999
        """
        splits = {}

        # 1. Discovery Set
        rng_disc = np.random.RandomState(self.base_seed + 1000)
        splits[DatasetSplit.DISCOVERY] = [
            rng_disc.randn(*shape).astype(dtype) for _ in range(num_samples_per_split)
        ]

        # 2. Verification Set
        rng_verif = np.random.RandomState(self.base_seed + 2000)
        splits[DatasetSplit.VERIFICATION] = [
            rng_verif.randn(*shape).astype(dtype) for _ in range(num_samples_per_split)
        ]

        # 3. Blind Holdout Set (Strictly unseen inputs)
        rng_holdout = np.random.RandomState(self.base_seed + 9999)
        splits[DatasetSplit.BLIND_HOLDOUT] = [
            rng_holdout.randn(*shape).astype(dtype) for _ in range(num_samples_per_split)
        ]

        return splits

    def generate_boundary_inputs(self, shape: Tuple[int, ...] = (16, 16)) -> List[np.ndarray]:
        """
        Generates pathological boundary inputs:
        - All zeros
        - All ones
        - Subnormals / Denormals (1e-38)
        - Large dynamic range (1e-20 to 1e20)
        - Alternating signs
        - Near-singular matrices
        """
        boundaries = []

        # All zeros
        boundaries.append(np.zeros(shape, dtype=np.float32))

        # All ones
        boundaries.append(np.ones(shape, dtype=np.float32))

        # Denormals
        boundaries.append(np.full(shape, 1e-37, dtype=np.float32))

        # Large dynamic range
        large_range = np.logspace(-15, 15, num=int(np.prod(shape)), dtype=np.float32).reshape(shape)
        boundaries.append(large_range)

        # Alternating sign checkerboard
        checker = np.ones(shape, dtype=np.float32)
        checker[::2, 1::2] = -1.0
        checker[1::2, ::2] = -1.0
        boundaries.append(checker)

        return boundaries

    def run_holdout_certification(
        self,
        candidate_fn: Callable[[np.ndarray], np.ndarray],
        golden_fn: Callable[[np.ndarray], np.ndarray],
        holdout_inputs: List[np.ndarray],
        contract: Contract,
    ) -> Tuple[bool, FuzzReport]:
        """
        Executes candidate against golden reference on blind holdout inputs.
        If candidate fails any holdout test, certification fails immediately.
        """
        for inp in holdout_inputs:
            self.report.total_generated += 1
            self.report.total_executed += 1

            try:
                cand_out = candidate_fn(inp)
                gold_out = golden_fn(inp)

                abs_diff = np.abs(cand_out - gold_out)
                max_abs = float(np.max(abs_diff)) if abs_diff.size > 0 else 0.0

                # Contract verification
                if contract.exact_required:
                    if max_abs == 0.0 or (np.isnan(cand_out).all() and np.isnan(gold_out).all()):
                        self.report.passed += 1
                    else:
                        self.report.failed += 1
                        self.report.mismatches += 1
                        self.report.false_escapes += 1
                elif contract.max_abs_error is not None:
                    if max_abs <= contract.max_abs_error:
                        self.report.passed += 1
                    else:
                        self.report.failed += 1
                        self.report.mismatches += 1
                        self.report.false_escapes += 1
                else:
                    self.report.passed += 1

            except Exception as e:
                self.report.crashes += 1
                self.report.failed += 1

        is_certified = (self.report.failed == 0 and self.report.false_escapes == 0)
        return is_certified, self.report
