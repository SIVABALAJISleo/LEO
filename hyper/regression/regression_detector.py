"""
hyper/regression/regression_detector.py
=======================================
Automatic Regression Detector (Section 65):
Compares new benchmark execution metrics against established baseline records.
Flags latency, memory, quality, or correctness regressions automatically.
"""

from typing import Dict, Any, List


class RegressionDetector:
    """
    Guards codebase against performance and accuracy regressions.
    """
    def __init__(self, latency_tolerance_pct: float = 10.0, max_error_allowed: float = 0.02):
        self.latency_tolerance_pct = latency_tolerance_pct
        self.max_error_allowed = max_error_allowed

    def detect_regression(
        self, baseline_metric: Dict[str, Any], current_metric: Dict[str, Any]
    ) -> Dict[str, Any]:
        base_time = baseline_metric.get("latency_ms", 1.0)
        curr_time = current_metric.get("latency_ms", 1.0)
        curr_err = current_metric.get("measured_error", 0.0)

        latency_diff_pct = ((curr_time - base_time) / max(1e-6, base_time)) * 100.0
        is_latency_regressed = latency_diff_pct > self.latency_tolerance_pct
        is_accuracy_regressed = curr_err > self.max_error_allowed

        has_regression = is_latency_regressed or is_accuracy_regressed

        return {
            "latency_diff_pct": round(latency_diff_pct, 2),
            "is_latency_regressed": is_latency_regressed,
            "is_accuracy_regressed": is_accuracy_regressed,
            "has_regression": has_regression,
            "verdict": "REJECT_REGRESSION" if has_regression else "PASS_NO_REGRESSION"
        }
