"""
hyper_v3/learning/cost_model.py
Learned cost model updating predictive coefficients from empirical execution traces.
"""

from typing import Dict, Any, List


class LearnedCostModel:
    """Refines hardware cost models from actual benchmark observations."""

    def __init__(self):
        self.latency_correction_factor = 1.0

    def update_with_observation(self, predicted_us: float, actual_us: float):
        if predicted_us > 0 and actual_us > 0:
            ratio = actual_us / predicted_us
            self.latency_correction_factor = 0.8 * self.latency_correction_factor + 0.2 * ratio

    def adjust_prediction(self, raw_predicted_us: float) -> float:
        return raw_predicted_us * self.latency_correction_factor
