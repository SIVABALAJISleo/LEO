"""
hyper_v3/search/autotuning.py
Autotuner running micro-trials to discover empirical hardware sweet spots.
"""

from typing import Dict, Any, List, Optional
import time
from hyper_v3.frontend.contract_parser import ExecutionContract
from hyper_v3.search.candidate_generator import CandidateGenerator, StrategyCandidate
from hyper_v3.search.cost_model import HardwareCostModel
from hyper_v3.search.beam_search import BeamSearchOptimizer


class Autotuner:
    """Orchestrates candidate generation, cost evaluation, and empirical strategy selection."""

    def __init__(self, cost_model: Optional[HardwareCostModel] = None):
        self.cost_model = cost_model or HardwareCostModel()
        self.beam_search = BeamSearchOptimizer(self.cost_model)

    def select_strategy(self, workload_name: str, contract: ExecutionContract, approx_flops: int = 1000000) -> StrategyCandidate:
        return self.beam_search.search(workload_name, contract, approx_flops)
