"""
hyper/defense/contamination_defense.py
======================================
Benchmark Contamination Defense (Section 51):
Guards against hidden precomputation, synthetic lookup tables,
hardcoded inputs, test-specific shortcuts, and asynchronous timing bugs.
Evaluates both known and freshly generated random unseen inputs.
"""

import time
import numpy as np
from typing import Dict, Any, Callable, Tuple


class ContaminationDefenseEngine:
    """
    Validates that performance gains are genuine and generalize to unseen inputs.
    """
    def __init__(self):
        pass

    def audit_unseen_input_generalization(
        self,
        known_input_fn: Callable[[], Tuple[float, bool]],
        unseen_input_fn: Callable[[], Tuple[float, bool]]
    ) -> Dict[str, Any]:
        """
        Compares speedup/accuracy on known benchmark inputs vs unseen synthetic inputs.
        If gain collapses on unseen inputs, flags potential contamination.
        """
        t_known, known_pass = known_input_fn()
        t_unseen, unseen_pass = unseen_input_fn()

        ratio = t_unseen / max(1e-6, t_known)
        is_contaminated = (ratio > 3.0) or (not unseen_pass)

        return {
            "known_input_time_ms": round(t_known, 3),
            "unseen_input_time_ms": round(t_unseen, 3),
            "unseen_overhead_ratio": round(ratio, 2),
            "known_passed": known_pass,
            "unseen_passed": unseen_pass,
            "contamination_detected": is_contaminated,
            "status": "HONEST_GENERALIZATION" if not is_contaminated else "CONTAMINATION_SUSPECTED"
        }
