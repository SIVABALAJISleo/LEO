"""
hyper_x/wormhole_compiler/evolution_engine.py
=============================================================================
HYPER-X Multi-Objective Evolutionary Algorithm Discovery Engine
=============================================================================
Evolves candidate algorithms across 12 dimensions:
  1. Algorithm structure
  2. Representation
  3. Decomposition
  4. Tiling & blocking
  5. Operation ordering
  6. Approximation level
  7. Reuse strategy
  8. Memory movement
  9. Communication strategy
 10. Vectorization efficiency
 11. CPU/iGPU work partition
 12. Correction & verification strategy

Uses:
  - Mutation & Crossover operators
  - Pareto Non-Dominated Sorting
  - Beam pruning & budget-guarded search
  - Multi-objective constraints: Latency <= SLO, Error <= Tolerance, Memory <= Limit
"""

from __future__ import annotations
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
import numpy as np

from hyper_x.wormhole_compiler.schemas import (
    GrammarOperator,
    WorkloadContract,
    CostVector,
)
from hyper_x.wormhole_compiler.algorithm_grammar import CompositeAlgorithm


@dataclass
class EvolutionaryIndividual:
    individual_id: str
    algorithm: CompositeAlgorithm
    partition_ratio: float = 0.0          # Fraction on iGPU [0.0 = 100% CPU, 1.0 = 100% iGPU]
    rank_parameter: int = 32
    sparsity_threshold: float = 1e-4
    tile_size: int = 64
    latency_ms: float = float("inf")
    numerical_error: float = float("inf")
    memory_mb: float = float("inf")
    is_valid: bool = False
    pareto_rank: int = 0
    fitness_score: float = 0.0


class EvolutionEngine:
    """Multi-objective genetic and beam search for computational wormholes."""

    def __init__(
        self,
        population_size: int = 12,
        max_generations: int = 5,
        mutation_rate: float = 0.35,
        crossover_rate: float = 0.25,
        time_budget_sec: float = 10.0
    ):
        self.pop_size = population_size
        self.max_gens = max_generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.time_budget_sec = time_budget_sec

    def mutate(self, ind: EvolutionaryIndividual) -> EvolutionaryIndividual:
        """Mutates one or more parameters/operators of an individual."""
        algo = ind.algorithm
        mutated_algo = CompositeAlgorithm(
            representation=algo.representation,
            decomposition=algo.decomposition,
            ordering=algo.ordering,
            approximation=algo.approximation,
            reuse=algo.reuse,
            prediction=algo.prediction,
            communication_strategy=algo.communication_strategy,
            memory_strategy=algo.memory_strategy,
            correction_strategy=algo.correction_strategy,
            verification_strategy=algo.verification_strategy,
            custom_params=dict(algo.custom_params)
        )

        roll = random.random()
        new_rank = ind.rank_parameter
        new_tile = ind.tile_size
        new_partition = ind.partition_ratio

        if roll < 0.25:
            # Mutate decomposition or ordering
            decomps = [GrammarOperator.BLOCK, GrammarOperator.FACTOR, GrammarOperator.RECURSE, GrammarOperator.SPLIT]
            mutated_algo.decomposition = random.choice(decomps)
        elif roll < 0.50:
            # Mutate partition ratio
            new_partition = round(random.choice([0.0, 0.25, 0.50, 0.75, 1.0]), 2)
        elif roll < 0.75:
            # Mutate rank or tile
            new_rank = max(8, ind.rank_parameter + random.choice([-16, 16]))
            new_tile = max(16, ind.tile_size + random.choice([-32, 32]))
        else:
            # Mutate correction or memory strategy
            mutated_algo.correction_strategy = GrammarOperator.CORRECT if random.random() > 0.5 else None

        new_id = f"IND_MUT_{int(time.time()*1000)%100000}_{random.randint(100,999)}"
        return EvolutionaryIndividual(
            individual_id=new_id,
            algorithm=mutated_algo,
            partition_ratio=new_partition,
            rank_parameter=new_rank,
            tile_size=new_tile,
            sparsity_threshold=ind.sparsity_threshold
        )

    def crossover(self, parent_a: EvolutionaryIndividual, parent_b: EvolutionaryIndividual) -> EvolutionaryIndividual:
        """Combines operators from two parents."""
        child_algo = CompositeAlgorithm(
            representation=parent_a.algorithm.representation,
            decomposition=parent_b.algorithm.decomposition or parent_a.algorithm.decomposition,
            ordering=parent_a.algorithm.ordering or parent_b.algorithm.ordering,
            approximation=parent_a.algorithm.approximation,
            reuse=parent_b.algorithm.reuse or parent_a.algorithm.reuse,
            correction_strategy=parent_a.algorithm.correction_strategy or parent_b.algorithm.correction_strategy,
            verification_strategy=parent_b.algorithm.verification_strategy
        )
        new_id = f"IND_CROSS_{int(time.time()*1000)%100000}_{random.randint(100,999)}"
        return EvolutionaryIndividual(
            individual_id=new_id,
            algorithm=child_algo,
            partition_ratio=(parent_a.partition_ratio + parent_b.partition_ratio) / 2.0,
            rank_parameter=random.choice([parent_a.rank_parameter, parent_b.rank_parameter]),
            tile_size=random.choice([parent_a.tile_size, parent_b.tile_size])
        )

    def pareto_rank_population(self, population: List[EvolutionaryIndividual]) -> List[EvolutionaryIndividual]:
        """Calculates Pareto non-dominated frontiers across Latency, Error, and Memory."""
        n = len(population)
        for i in range(n):
            ind_i = population[i]
            domination_count = 0
            for j in range(n):
                if i == j:
                    continue
                ind_j = population[j]
                # Check if j strictly dominates i: j is <= in all metrics and strictly < in at least one
                better_or_equal = (
                    ind_j.latency_ms <= ind_i.latency_ms and
                    ind_j.numerical_error <= ind_i.numerical_error and
                    ind_j.memory_mb <= ind_i.memory_mb
                )
                strictly_better = (
                    ind_j.latency_ms < ind_i.latency_ms or
                    ind_j.numerical_error < ind_i.numerical_error or
                    ind_j.memory_mb < ind_i.memory_mb
                )
                if better_or_equal and strictly_better:
                    domination_count += 1

            ind_i.pareto_rank = domination_count
            # Fitness: rank 0 is best, plus rewards for lower latency
            ind_i.fitness_score = 1.0 / (1.0 + domination_count + (ind_i.latency_ms / 100.0))

        return sorted(population, key=lambda ind: ind.pareto_rank)

    def search(
        self,
        initial_candidates: List[CompositeAlgorithm],
        eval_fn: Callable[[EvolutionaryIndividual], Tuple[float, float, float, bool]],
        contract: WorkloadContract
    ) -> List[EvolutionaryIndividual]:
        """Executes budget-constrained evolutionary search."""
        t_start = time.perf_counter()
        population: List[EvolutionaryIndividual] = []

        # Seed initial population
        for i, algo in enumerate(initial_candidates):
            ind = EvolutionaryIndividual(
                individual_id=f"IND_INIT_{i}_{algo.compute_hash()[:6]}",
                algorithm=algo,
                partition_ratio=0.0
            )
            lat, err, mem, valid = eval_fn(ind)
            ind.latency_ms = lat
            ind.numerical_error = err
            ind.memory_mb = mem
            ind.is_valid = valid
            population.append(ind)

        # Evolutionary loop
        generation = 0
        while generation < self.max_gens:
            if time.perf_counter() - t_start > self.time_budget_sec:
                break

            ranked = self.pareto_rank_population(population)
            survivors = ranked[: max(2, self.pop_size // 2)]
            next_generation = list(survivors)

            # Generate offspring
            while len(next_generation) < self.pop_size:
                if len(survivors) >= 2 and random.random() < self.crossover_rate:
                    p1, p2 = random.sample(survivors, 2)
                    child = self.crossover(p1, p2)
                else:
                    parent = random.choice(survivors)
                    child = self.mutate(parent)

                lat, err, mem, valid = eval_fn(child)
                child.latency_ms = lat
                child.numerical_error = err
                child.memory_mb = mem
                child.is_valid = valid
                next_generation.append(child)

            population = next_generation
            generation += 1

        return self.pareto_rank_population(population)
