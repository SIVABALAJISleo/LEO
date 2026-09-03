"""
hyper_mvc_dar/algorithm_discovery.py
Algorithm Discovery & Synthesis: Strategy genome representation, evolutionary search,
mutation, crossover, and multi-objective Pareto optimization.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import random
import copy


@dataclass
class StrategyGenome:
    strategy_id: str
    algorithm: str
    representation: str
    precision: str
    tile_size: int
    cpu_ratio: float
    igpu_ratio: float
    sampling_strength: float
    verification_method: str
    fitness_scores: Dict[str, float] = field(default_factory=dict)

    def mutate(self) -> "StrategyGenome":
        child = copy.deepcopy(self)
        child.strategy_id = f"strat_{random.randint(1000, 9999)}"

        mutation_choice = random.choice(["tile", "partition", "sampling", "precision"])
        if mutation_choice == "tile":
            child.tile_size = random.choice([16, 32, 64, 128])
        elif mutation_choice == "partition":
            new_cpu = round(random.uniform(0.1, 1.0), 2)
            child.cpu_ratio = new_cpu
            child.igpu_ratio = round(1.0 - new_cpu, 2)
        elif mutation_choice == "sampling":
            child.sampling_strength = round(random.uniform(0.2, 1.0), 2)
        elif mutation_choice == "precision":
            child.precision = random.choice(["FP32", "FP16", "INT8", "TERNARY"])

        return child


class StrategySearchEngine:
    """Maintains population of candidate genomes and evolves toward Pareto-optimal frontier."""

    def __init__(self, population_size: int = 8):
        self.population: List[StrategyGenome] = self._init_population(population_size)
        self.pareto_frontier: List[StrategyGenome] = []

    def _init_population(self, size: int) -> List[StrategyGenome]:
        pop = []
        for i in range(size):
            pop.append(StrategyGenome(
                strategy_id=f"init_strat_{i}",
                algorithm=random.choice(["DenseTiled", "RandomizedSVD", "SparseCSR", "TernaryBitNet"]),
                representation=random.choice(["Dense", "Sparse2:4", "Ternary", "LowRank"]),
                precision=random.choice(["FP32", "FP16", "INT8"]),
                tile_size=random.choice([32, 64]),
                cpu_ratio=0.7,
                igpu_ratio=0.3,
                sampling_strength=1.0,
                verification_method="Freivalds"
            ))
        return pop

    def evolve_generation(self) -> List[StrategyGenome]:
        new_pop = []
        for parent in self.population:
            new_pop.append(parent)
            new_pop.append(parent.mutate())
        self.population = new_pop[: len(self.population)]
        return self.population
