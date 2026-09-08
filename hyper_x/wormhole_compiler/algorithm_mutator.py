"""
hyper_x/wormhole_compiler/algorithm_mutator.py
=============================================================================
HYPER-X Algorithm Genome Mutator (Phase 10)
=============================================================================
Applies stochastic, contract-guided mutations to an AlgorithmGenome.

Mutation Operations:
  - mutate_representation (e.g. DENSE -> LOW_RANK, SPARSE)
  - mutate_decomposition (e.g. NONE -> SVD_TRUNCATED, BLOCK)
  - mutate_ordering (e.g. ROW_MAJOR -> MORTON_Z, CACHE_TILED)
  - mutate_reuse (e.g. NONE -> TEMPORAL_DELTA, STATIC_WEIGHT_CACHE)
  - mutate_approximation (e.g. NONE -> ADAPTIVE_RANK, THRESHOLD_1E3)
  - mutate_correction (e.g. NONE -> RESIDUAL_EXACT, BILATERAL_GUARD)
  - mutate_execution (e.g. CPU_AVX2 -> INTEL_IGPU, HYBRID_DYNAMIC)
  - mutate_parameters (e.g. adjust rank, threshold, or tile size)
"""

from __future__ import annotations
import random
from typing import Dict, Any, List

from hyper_x.wormhole_compiler.algorithm_genome import AlgorithmGenome


class AlgorithmMutator:
    """Genetic mutator for algorithm genomes."""

    REPRESENTATION_OPTIONS = ["DENSE", "LOW_RANK", "SPARSE", "SPECTRAL_FFT", "LUT_KAN"]
    DECOMPOSITION_OPTIONS = ["NONE", "SVD_TRUNCATED", "BLOCK_4x4", "RANDOMIZED_RANGE"]
    ORDERING_OPTIONS = ["ROW_MAJOR", "MORTON_Z", "CACHE_TILED", "HILBERT"]
    REUSE_OPTIONS = ["NONE", "TEMPORAL_DELTA", "STATIC_WEIGHT_CACHE", "EVENT_DRIVEN"]
    PREDICTION_OPTIONS = ["NONE", "SPECTRAL_SURROGATE", "LINEAR_EXTRAPOLATE"]
    APPROXIMATION_OPTIONS = ["NONE", "ADAPTIVE_RANK", "THRESHOLD_1E3", "TOP_K_PROJECTION"]
    CORRECTION_OPTIONS = ["NONE", "RESIDUAL_EXACT", "BILATERAL_GUARD", "BOUNDED_FALLBACK"]
    EXECUTION_OPTIONS = ["CPU_AVX2", "INTEL_IGPU", "HYBRID_DYNAMIC"]
    VERIFICATION_OPTIONS = ["FREIVALDS_15R", "FROBENIUS_EXACT", "PERCEPTUAL_SSIM"]

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def mutate(self, genome: AlgorithmGenome, mutation_prob: float = 0.30) -> AlgorithmGenome:
        """Produces a mutated offspring AlgorithmGenome."""
        rep = genome.representation
        dec = genome.decomposition
        ord_val = genome.ordering
        reu = genome.reuse
        prd = genome.prediction
        app = genome.approximation
        cor = genome.correction
        exe = genome.execution
        ver = genome.verification
        params = dict(genome.parameters)

        if self.rng.random() < mutation_prob:
            rep = self.rng.choice(self.REPRESENTATION_OPTIONS)
        if self.rng.random() < mutation_prob:
            dec = self.rng.choice(self.DECOMPOSITION_OPTIONS)
        if self.rng.random() < mutation_prob:
            ord_val = self.rng.choice(self.ORDERING_OPTIONS)
        if self.rng.random() < mutation_prob:
            reu = self.rng.choice(self.REUSE_OPTIONS)
        if self.rng.random() < mutation_prob:
            prd = self.rng.choice(self.PREDICTION_OPTIONS)
        if self.rng.random() < mutation_prob:
            app = self.rng.choice(self.APPROXIMATION_OPTIONS)
        if self.rng.random() < mutation_prob:
            cor = self.rng.choice(self.CORRECTION_OPTIONS)
        if self.rng.random() < mutation_prob:
            exe = self.rng.choice(self.EXECUTION_OPTIONS)
        if self.rng.random() < mutation_prob:
            ver = self.rng.choice(self.VERIFICATION_OPTIONS)

        # Mutate numeric hyperparameters
        if "rank" in params and self.rng.random() < mutation_prob:
            params["rank"] = max(2, params["rank"] + self.rng.choice([-4, -2, 2, 4]))
        if "threshold" in params and self.rng.random() < mutation_prob:
            params["threshold"] = max(1e-6, params["threshold"] * self.rng.choice([0.5, 2.0]))

        return AlgorithmGenome(
            representation=rep,
            decomposition=dec,
            ordering=ord_val,
            reuse=reu,
            prediction=prd,
            approximation=app,
            correction=cor,
            communication=genome.communication,
            memory=genome.memory,
            execution=exe,
            verification=ver,
            parameters=params,
        )
