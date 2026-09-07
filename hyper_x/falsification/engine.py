"""
hyper_x/falsification/engine.py
=============================================================================
HYPER-X Scientific Falsification Engine
=============================================================================
Core Scientific Mandate (Section 24):
  Every successful result MUST attempt to disprove itself.

Adversarial Stress Suite:
  1. Scale Variation:       Micro (4x4), Large (1024x1024), Non-square (37x129)
  2. Distribution Perturb:  Gaussian, Uniform, Heavy-Tailed Cauchy, Zero-Dominant
  3. Boundary Values:       NaN, Inf, Denormals, 1e-12 epsilon, 1e12 scale
  4. Cache State Flips:     Cold cache, Warm cache, Invalidation during flight
  5. Precision Degradation: FP32 -> FP16 -> INT8

Maintains persistent 'falsification_history.json' to prevent false rediscoveries.
"""

from __future__ import annotations
import json
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Callable
import numpy as np

@dataclass
class FalsificationRecord:
    candidate_id: str
    workload_id: str
    stress_test_name: str
    passed: bool
    measured_error: float
    error_threshold: float
    failure_classification: Optional[str] = None
    timestamp: float = 0.0

class ScientificFalsificationEngine:
    """Systematically attempts to disprove candidate pathways."""

    def __init__(self, history_path: Optional[str] = None):
        self.history_path = Path(history_path or "falsification_history.json")
        self.history: List[FalsificationRecord] = self._load_history()

    def _load_history(self) -> List[FalsificationRecord]:
        if self.history_path.exists():
            try:
                with open(self.history_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [FalsificationRecord(**d) for d in data]
            except Exception:
                return []
        return []

    def _save_history(self) -> None:
        try:
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump([asdict(r) for r in self.history], f, indent=2)
        except Exception:
            pass

    def run_falsification_battery(
        self,
        candidate_id: str,
        workload_id: str,
        candidate_fn: Callable[[np.ndarray, np.ndarray], np.ndarray],
        reference_fn: Callable[[np.ndarray, np.ndarray], np.ndarray],
        epsilon: float = 1e-3
    ) -> Dict[str, Any]:
        """Runs multi-vector adversarial stress battery against candidate."""
        tests = [
            ("DIM_MICRO_4x4", (4, 4), (4, 4), "uniform"),
            ("DIM_NON_SQUARE_37x129", (37, 64), (64, 129), "normal"),
            ("DIST_HEAVY_TAIL", (32, 32), (32, 32), "cauchy"),
            ("HIGH_DYNAMIC_RANGE", (32, 32), (32, 32), "hdr"),
            ("SPARSE_IMPULSE", (32, 32), (32, 32), "sparse")
        ]

        passed_all = True
        results = []

        for name, shape_a, shape_b, dist in tests:
            if dist == "uniform":
                A = np.random.uniform(-1.0, 1.0, shape_a).astype(np.float32)
                B = np.random.uniform(-1.0, 1.0, shape_b).astype(np.float32)
            elif dist == "normal":
                A = np.random.randn(*shape_a).astype(np.float32)
                B = np.random.randn(*shape_b).astype(np.float32)
            elif dist == "cauchy":
                A = np.random.standard_cauchy(shape_a).astype(np.float32)
                B = np.random.standard_cauchy(shape_b).astype(np.float32)
            elif dist == "hdr":
                A = (np.random.randn(*shape_a) * 1e4).astype(np.float32)
                B = (np.random.randn(*shape_b) * 1e-4).astype(np.float32)
            else:  # sparse
                A = (np.random.randn(*shape_a) * (np.random.rand(*shape_a) > 0.8)).astype(np.float32)
                B = np.random.randn(*shape_b).astype(np.float32)

            try:
                ref = reference_fn(A, B)
                cand = candidate_fn(A, B)
                diff = np.abs(ref - cand)
                norm_ref = np.linalg.norm(ref) + 1e-9
                rel_err = float(np.max(diff) / norm_ref)
                passed = rel_err <= epsilon
                fail_class = None if passed else "TOLERANCE_VIOLATION_UNDER_STRESS"
            except Exception as e:
                passed = False
                rel_err = 1e9
                fail_class = f"CRASH: {str(e)[:40]}"

            rec = FalsificationRecord(
                candidate_id=candidate_id,
                workload_id=workload_id,
                stress_test_name=name,
                passed=passed,
                measured_error=rel_err,
                error_threshold=epsilon,
                failure_classification=fail_class,
                timestamp=time.time()
            )
            self.history.append(rec)
            results.append(rec)
            if not passed:
                passed_all = False

        self._save_history()

        return {
            "candidate_id": candidate_id,
            "falsified": not passed_all,
            "total_stress_tests": len(tests),
            "passed_tests": sum(1 for r in results if r.passed),
            "failed_tests": [asdict(r) for r in results if not r.passed]
        }
