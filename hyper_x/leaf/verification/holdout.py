"""
hyper_x/leaf/verification/holdout.py
===================================
Blind holdout and out-of-distribution evaluation for LEAF.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np


class BlindHoldoutEvaluator:
    """Evaluates escape candidates on unseen holdout datasets."""

    def evaluate_holdout(
        self,
        candidate_fn: Callable[[np.ndarray], np.ndarray],
        reference_fn: Callable[[np.ndarray], np.ndarray],
        holdout_generator: Callable[[], np.ndarray],
        trials: int = 10,
        tolerance: float = 1e-4,
    ) -> Tuple[bool, float, float]:
        """Runs candidate against reference on freshly generated unseen inputs."""
        max_err = 0.0
        avg_err = 0.0

        for _ in range(trials):
            inp = holdout_generator()
            ref = reference_fn(inp)
            cand = candidate_fn(inp)

            denom = np.linalg.norm(ref)
            err = float(np.linalg.norm(cand - ref) / max(1e-12, denom))
            max_err = max(max_err, err)
            avg_err += err

        avg_err /= max(1, trials)
        passed = max_err <= tolerance
        return passed, max_err, avg_err
