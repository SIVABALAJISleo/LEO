"""
Meta-Search Engine: Evolves and tunes discovery search strategies themselves.
Implements the outer meta-loop:
SEARCH STRATEGY -> DISCOVERY -> MEASURE DISCOVERY YIELD -> LEARN -> MODIFY SEARCH STRATEGY -> SEARCH AGAIN
"""
from typing import Any, Callable, Dict, List, Optional, Tuple
from hyper_universal.types import ResultTaxonomy
from hyper_omega.meta_search.strategy_genome import SearchStrategyGenome


class MetaSearchEngine:
    """
    Orchestrates the optimization of discovery strategies.
    Scales search budget adaptively and detects search saturation.
    """

    def __init__(self, initial_strategy: Optional[SearchStrategyGenome] = None):
        self.current_strategy = initial_strategy or SearchStrategyGenome(
            strategy_id="meta_root_0",
            algorithm="beam_search",
            candidate_budget=20
        )
        self.strategy_history: List[SearchStrategyGenome] = [self.current_strategy]
        self.stagnation_counter = 0

    def run_meta_iteration(
        self,
        discovery_runner: Callable[[SearchStrategyGenome], float]  # returns discovery yield score
    ) -> Tuple[SearchStrategyGenome, ResultTaxonomy]:
        """
        Runs one iteration of meta-search:
        1. Evaluate current strategy
        2. Propose mutated strategy
        3. Evaluate candidate strategy
        4. Select winner and adapt scale
        """
        # 1. Run discovery with current strategy
        current_yield = discovery_runner(self.current_strategy)
        self.current_strategy.yield_score = current_yield

        # 2. Mutate to create candidate meta-strategy
        mutated_strategy = self.current_strategy.mutate_meta_strategy()
        candidate_yield = discovery_runner(mutated_strategy)
        mutated_strategy.yield_score = candidate_yield

        # 3. Selection
        if candidate_yield > current_yield * 1.05:  # At least 5% improvement
            self.current_strategy = mutated_strategy
            self.strategy_history.append(mutated_strategy)
            self.stagnation_counter = 0
            status = ResultTaxonomy.VERIFIED
        else:
            self.stagnation_counter += 1
            if self.stagnation_counter >= 3:
                # Improvement has stopped -> SEARCH_SATURATED (never fake NO SOLUTION)
                status = ResultTaxonomy.SEARCH_SATURATED
            else:
                status = ResultTaxonomy.FOUND

        return self.current_strategy, status
