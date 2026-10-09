"""
hyper/godmode/pathway_evolution/evolution_engine.py
===================================================
Pathway Evolution Engine for HYPER-GODMODE.
Implements Section 9 (Pathway Evolution Engine):
- Discovers alternative pathways across 5 generations:
    Gen 0: Reference baseline pathway
    Gen 1: Primitive single transformations
    Gen 2: Combinations of successful transformations
    Gen 3: Mutations (parameter tuning, tiling thresholds)
    Gen 4: Workload-specific specialization
    Gen 5: Cross-breeding independent successful strategies
- Tracks searched space vs total possible space.
"""

from __future__ import annotations
import random
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from hyper.parity_engine.pathway_ir import PathwayIR, TransformationType


class GenerationSummary(BaseModel):
    generation_number: int
    candidate_count: int
    survivors_count: int
    best_speedup: float
    best_work_reduction_pct: float
    description: str


class EvolutionarySearchTrace(BaseModel):
    trace_id: str
    workload_name: str
    generations_completed: int
    total_candidates_evaluated: int
    searched_space_estimate: int
    total_possible_space_estimate: int
    generation_summaries: List[GenerationSummary] = Field(default_factory=list)
    fittest_pathway_id: Optional[str] = None
    fittest_speedup: float = 1.0


class PathwayEvolutionEngine:
    """
    Multi-generational genetic search engine evolving computational pathways.
    """

    TRANSFORMATION_GENES = [
        "L1_L2_CACHE_BLOCKING",
        "CONTIGUOUS_MEMORY_PREFETCH",
        "ALGEBRAIC_IDENTITY_REASSOCIATION",
        "SEPARABLE_FILTER_FACTORIZATION",
        "TEMPORAL_HISTORY_BUFFER_REUSE",
        "WAVEFRONT_ACTIVE_SET_PRUNING",
        "STRUCTURED_BLOCK_SPARSITY",
        "FORCE_SYMMETRY_HALVING",
        "EARLY_Z_SLAB_REJECTION",
        "REGISTER_FUSED_LOOP_ACCUMULATION",
    ]

    def __init__(self, seed: int = 42) -> None:
        self.rng = random.Random(seed)

    def evolve_pathways(
        self,
        workload_name: str,
        base_pathway: PathwayIR,
        evaluate_fitness_fn: Callable[[List[str]], Tuple[bool, float, float]],  # (is_valid, speedup, work_reduction)
        generations: int = 5,
        population_size: int = 6,
    ) -> EvolutionarySearchTrace:
        """
        Executes evolutionary search across multiple generations.
        """
        summaries: List[GenerationSummary] = []
        current_population: List[List[str]] = [[]]  # Gen 0: empty transformations (reference)
        best_pathway_genes: List[str] = []
        best_speedup = 1.0
        best_reduction = 0.0
        total_evals = 0

        for gen in range(generations + 1):
            survivors = []
            gen_best_speedup = 1.0
            gen_best_reduction = 0.0

            if gen == 0:
                # Gen 0: Reference baseline
                candidates = [[]]
                desc = "Gen 0: Reference baseline pathway."
            elif gen == 1:
                # Gen 1: Primitive single transformations
                candidates = [[gene] for gene in self.TRANSFORMATION_GENES[:population_size]]
                desc = "Gen 1: Isolated primitive transformations."
            elif gen == 2:
                # Gen 2: Pairwise combinations of survivors
                candidates = []
                pool = best_pathway_genes if best_pathway_genes else self.TRANSFORMATION_GENES[:3]
                for g1 in pool:
                    for g2 in self.TRANSFORMATION_GENES[3:6]:
                        candidates.append([g1, g2])
                desc = "Gen 2: Pairwise composition of successful primitives."
            elif gen == 3:
                # Gen 3: Mutations (add cache or register tuning)
                candidates = []
                for p in current_population[:population_size]:
                    mutated = list(p)
                    new_gene = self.rng.choice(self.TRANSFORMATION_GENES)
                    if new_gene not in mutated:
                        mutated.append(new_gene)
                    candidates.append(mutated)
                desc = "Gen 3: Mutation and gene insertion."
            elif gen == 4:
                # Gen 4: Workload-specific specialization
                candidates = [
                    list(set(best_pathway_genes + [self.TRANSFORMATION_GENES[0], self.TRANSFORMATION_GENES[1]])),
                    list(set(best_pathway_genes + [self.TRANSFORMATION_GENES[2], self.TRANSFORMATION_GENES[6]])),
                ]
                desc = "Gen 4: Workload structural specialization."
            else:
                # Gen 5: Cross-breeding independent strategies
                candidates = [
                    list(set(best_pathway_genes + self.TRANSFORMATION_GENES[:3])),
                    list(set(best_pathway_genes + self.TRANSFORMATION_GENES[3:6])),
                ]
                desc = "Gen 5: Cross-breeding independent successful pathways."

            for c in candidates:
                total_evals += 1
                valid, speedup, red = evaluate_fitness_fn(c)
                if valid and speedup >= 1.0:
                    survivors.append(c)
                    if speedup > gen_best_speedup:
                        gen_best_speedup = speedup
                        gen_best_reduction = red
                    if speedup > best_speedup:
                        best_speedup = speedup
                        best_reduction = red
                        best_pathway_genes = c

            current_population = survivors if survivors else candidates[:2]
            summaries.append(
                GenerationSummary(
                    generation_number=gen,
                    candidate_count=len(candidates),
                    survivors_count=len(survivors),
                    best_speedup=round(gen_best_speedup, 2),
                    best_work_reduction_pct=round(gen_best_reduction, 2),
                    description=desc,
                )
            )

        return EvolutionarySearchTrace(
            trace_id=f"EVO_{workload_name}_{int(time.time()*1000)%100000}",
            workload_name=workload_name,
            generations_completed=generations,
            total_candidates_evaluated=total_evals,
            searched_space_estimate=total_evals,
            total_possible_space_estimate=2 ** len(self.TRANSFORMATION_GENES),
            generation_summaries=summaries,
            fittest_pathway_id=f"PTH_FIT_{workload_name}",
            fittest_speedup=round(best_speedup, 2),
        )
