"""
hyper_v3/learning/online_learning.py
Online learning coordinator feeding back runtime metrics without modifying correctness constraints.
"""

from typing import Dict, Any
from hyper_v3.learning.cost_model import LearnedCostModel
from hyper_v3.search.strategy_memory import StrategyMemory


class OnlineLearningEngine:
    """Coordinates runtime adaptation and strategy persistence."""

    def __init__(self):
        self.cost_model = LearnedCostModel()
        self.strategy_memory = StrategyMemory()

    def record_feedback(self, workload_name: str, strategy: str, predicted_us: float, actual_us: float, vwa: float):
        self.cost_model.update_with_observation(predicted_us, actual_us)
        self.strategy_memory.record_strategy(workload_name, strategy, actual_us, vwa)
