"""
hyper_x/wormhole_compiler/algorithm_crossover.py
=============================================================================
HYPER-X Algorithm Genome Crossover (Phase 10)
=============================================================================
Recombines orthogonal, successful substructures from two parent AlgorithmGenomes.

Example:
  Candidate A:
      LOW_RANK + BLOCK
  Candidate B:
      DELTA + REUSE

  Offspring:
      LOW_RANK + BLOCK + DELTA + REUSE + RESIDUAL_CORRECTION
"""

from __future__ import annotations
import random
from typing import Tuple

from hyper_x.wormhole_compiler.algorithm_genome import AlgorithmGenome


class AlgorithmCrossover:
    """Genetic crossover operator for algorithm genomes."""

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def crossover(
        self,
        parent_a: AlgorithmGenome,
        parent_b: AlgorithmGenome,
    ) -> AlgorithmGenome:
        """
        Recombines traits from parent A and parent B into an offspring genome.
        Prefers non-default traits to preserve novel discovered substructures.
        """
        def _pick(val_a: str, val_b: str, default: str = "NONE") -> str:
            if val_a != default and val_b == default:
                return val_a
            elif val_b != default and val_a == default:
                return val_b
            else:
                return val_a if self.rng.random() < 0.5 else val_b

        rep = _pick(parent_a.representation, parent_b.representation, "DENSE")
        dec = _pick(parent_a.decomposition, parent_b.decomposition, "NONE")
        ord_val = _pick(parent_a.ordering, parent_b.ordering, "ROW_MAJOR")
        reu = _pick(parent_a.reuse, parent_b.reuse, "NONE")
        prd = _pick(parent_a.prediction, parent_b.prediction, "NONE")
        app = _pick(parent_a.approximation, parent_b.approximation, "NONE")
        cor = _pick(parent_a.correction, parent_b.correction, "NONE")
        exe = _pick(parent_a.execution, parent_b.execution, "CPU_AVX2")
        ver = _pick(parent_a.verification, parent_b.verification, "FREIVALDS_15R")

        # Merge parameter dictionaries
        merged_params = dict(parent_a.parameters)
        merged_params.update(parent_b.parameters)

        return AlgorithmGenome(
            representation=rep,
            decomposition=dec,
            ordering=ord_val,
            reuse=reu,
            prediction=prd,
            approximation=app,
            correction=cor,
            communication=parent_a.communication,
            memory=parent_a.memory,
            execution=exe,
            verification=ver,
            parameters=merged_params,
        )
