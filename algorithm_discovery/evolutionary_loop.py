"""
algorithm_discovery/evolutionary_loop.py
Implements an autonomous evolutionary optimization loop that mutates, benchmarks,
verifies, and selects candidate computational strategies along a Pareto frontier.
"""

from typing import Dict, Any, List, Optional
import random
import copy
from .generator import AlgorithmStrategy, StrategyCandidateGenerator


class CandidateIndividual:
    """An individual strategy with measured multi-objective fitness scores."""
    def __init__(self, strategy: AlgorithmStrategy):
        self.strategy = strategy
        self.latency_us: float = float("inf")
        self.vwa: float = 0.0
        self.max_relative_error: float = float("inf")
        self.is_verified: bool = False
        self.fitness_score: float = 0.0

    def calculate_fitness(self, max_allowed_error: float = 0.50) -> float:
        """Computes a scalar fitness score penalizing contract violations."""
        if not self.is_verified or self.max_relative_error > max_allowed_error:
            self.fitness_score = -1000.0  # Disqualified
            return self.fitness_score

        # Higher VWA is rewarded, lower latency is rewarded
        speed_factor = 1000.0 / max(self.latency_us, 1.0)
        self.fitness_score = (self.vwa * 50.0) + speed_factor
        return self.fitness_score


class EvolutionaryOptimizationLoop:
    """Autonomous evolutionary search for optimal execution strategies."""

    def __init__(self, population_size: int = 8, max_generations: int = 3):
        self.population_size = population_size
        self.max_generations = max_generations
        self.pareto_frontier: List[CandidateIndividual] = []

    def mutate(self, strategy: AlgorithmStrategy) -> AlgorithmStrategy:
        """Mutates strategy parameters within legal bounds."""
        mutated = copy.deepcopy(strategy)
        mutated.strategy_id = f"{strategy.strategy_id}_mut_{random.randint(100, 999)}"

        # Possible mutations
        choice = random.choice(["tile", "cpu_ratio", "approx"])
        if choice == "tile":
            mutated.tile_size = random.choice([32, 64, 128, 256])
        elif choice == "cpu_ratio":
            mutated.cpu_ratio = round(random.uniform(0.2, 0.8), 2)
        elif choice == "approx":
            mutated.approximation_param = round(max(0.01, mutated.approximation_param + random.uniform(-0.02, 0.02)), 3)

        return mutated

    def run_evolution(
        self,
        workload_name: str,
        evaluate_fn,
        max_allowed_error: float = 0.50
    ) -> Dict[str, Any]:
        """Runs the generation-evaluation-selection cycle."""
        # 1. Initialize population
        initial_strategies = StrategyCandidateGenerator.generate_candidates(workload_name, allow_approx=True)
        population: List[CandidateIndividual] = [CandidateIndividual(s) for s in initial_strategies]

        best_individual: Optional[CandidateIndividual] = None

        for gen in range(self.max_generations):
            # Evaluate all individuals
            for ind in population:
                lat_us, vwa, rel_err, is_valid = evaluate_fn(ind.strategy)
                ind.latency_us = lat_us
                ind.vwa = vwa
                ind.max_relative_error = rel_err
                ind.is_verified = is_valid
                ind.calculate_fitness(max_allowed_error)

                # Update Pareto frontier
                if is_valid and (best_individual is None or ind.fitness_score > best_individual.fitness_score):
                    best_individual = ind
                    self.pareto_frontier.append(ind)

            # Sort population by fitness
            population = sorted(population, key=lambda x: x.fitness_score, reverse=True)

            # Select top performers and mutate
            survivors = population[:max(2, len(population) // 2)]
            new_population = list(survivors)

            while len(new_population) < self.population_size:
                parent = random.choice(survivors)
                mutated_strat = self.mutate(parent.strategy)
                new_population.append(CandidateIndividual(mutated_strat))

            population = new_population

        chosen = best_individual if best_individual is not None else population[0]
        return {
            "workload": workload_name,
            "generations_evaluated": self.max_generations,
            "best_strategy_id": chosen.strategy.strategy_id,
            "best_algorithm": chosen.strategy.algorithm_name,
            "best_device": chosen.strategy.device_mapping,
            "measured_latency_us": chosen.latency_us,
            "measured_vwa": chosen.vwa,
            "max_relative_error": chosen.max_relative_error,
            "verified": chosen.is_verified,
            "pareto_size": len(self.pareto_frontier)
        }
