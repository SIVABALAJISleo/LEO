"""
Algorithm Discovery Engine: Coordinates multi-strategy algorithm discovery
(Beam Search, AlphaTensor-style bilinear search, AlphaDev low-level search, etc.)
"""
from typing import Any, Callable, Dict, List, Optional, Tuple
from hyper_universal.contract_ir import ContractIR
from hyper_omega.algorithm_discovery.strategies import (
    DiscoveryStrategy,
    BeamSearchStrategy,
    AlphaTensorBilinearDiscovery,
    AlphaDevLowLevelDiscovery,
    SearchCandidate,
    StrategyMetrics,
)


class AlgorithmDiscoveryEngine:
    """
    Central discovery coordinator running multiple autonomous search algorithms.
    """

    def __init__(self):
        self.strategies: Dict[str, DiscoveryStrategy] = {
            "beam_search": BeamSearchStrategy(),
            "alphatensor": AlphaTensorBilinearDiscovery(),
            "alphadev": AlphaDevLowLevelDiscovery(),
        }
        self.history: List[StrategyMetrics] = []

    def register_strategy(self, name: str, strategy: DiscoveryStrategy) -> None:
        self.strategies[name] = strategy

    def discover(
        self,
        strategy_name: str,
        workload_name: str,
        contract: ContractIR,
        budget: int,
        eval_fn: Callable[[str], Tuple[bool, float, bool]],
    ) -> Tuple[List[SearchCandidate], StrategyMetrics]:
        if strategy_name not in self.strategies:
            strategy_name = "beam_search"

        strategy = self.strategies[strategy_name]
        candidates, metrics = strategy.search(workload_name, contract, budget, eval_fn)
        self.history.append(metrics)
        return candidates, metrics

    def run_portfolio(
        self,
        workload_name: str,
        contract: ContractIR,
        budget_per_strategy: int,
        eval_fn: Callable[[str], Tuple[bool, float, bool]],
    ) -> Dict[str, Tuple[List[SearchCandidate], StrategyMetrics]]:
        """Run all registered discovery strategies concurrently or sequentially."""
        results = {}
        for name in list(self.strategies.keys()):
            cands, metrics = self.discover(name, workload_name, contract, budget_per_strategy, eval_fn)
            results[name] = (cands, metrics)
        return results
