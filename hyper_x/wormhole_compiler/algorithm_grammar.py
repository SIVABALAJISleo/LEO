"""
hyper_x/wormhole_compiler/algorithm_grammar.py
=============================================================================
HYPER-X Compositional Algorithm Grammar: Generative Algorithm Synthesis
=============================================================================
Transforms fixed, hardcoded algorithms into a fully compositional search space:
    Algorithm =
        Representation
        + Decomposition
        + Ordering
        + Approximation
        + Reuse
        + Prediction
        + Communication strategy
        + Memory strategy
        + Correction strategy
        + Verification strategy

Supported Grammar Operators:
  DENSE, SPARSE, LOW_RANK, BLOCK, TILE, REORDER, FACTOR, DELTA, CACHE, PREDICT,
  APPROXIMATE, QUANTIZE, SKETCH, FFT, WAVELET, MULTIGRID, RECURSE, EVENT_DRIVEN,
  CONDITIONAL, STREAM, COMPRESS, DECOMPRESS, REUSE, SPECULATE, CORRECT, FUSE,
  SPLIT, PIPELINE, COMMUNICATION_AVOID, MEMORY_AVOID, OUTPUT_PROJECT, SUFFICIENT_STATISTIC.
"""

from __future__ import annotations
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
import numpy as np

from hyper_x.wormhole_compiler.schemas import (
    GrammarOperator,
    GrammarExpression,
    WorkloadContract,
    CorrectnessRequirement,
)


@dataclass
class CompositeAlgorithm:
    """Formal compositional algorithm instance."""
    representation: GrammarOperator
    decomposition: Optional[GrammarOperator] = None
    ordering: Optional[GrammarOperator] = None
    approximation: Optional[GrammarOperator] = None
    reuse: Optional[GrammarOperator] = None
    prediction: Optional[GrammarOperator] = None
    communication_strategy: Optional[GrammarOperator] = None
    memory_strategy: Optional[GrammarOperator] = None
    correction_strategy: Optional[GrammarOperator] = None
    verification_strategy: Optional[GrammarOperator] = None
    custom_params: Dict[str, Any] = field(default_factory=dict)

    def to_canonical_expression(self) -> str:
        parts = [self.representation.value]
        for op in [
            self.decomposition, self.ordering, self.approximation,
            self.reuse, self.prediction, self.communication_strategy,
            self.memory_strategy, self.correction_strategy, self.verification_strategy
        ]:
            if op is not None:
                parts.append(op.value)
        return " + ".join(parts)

    def compute_hash(self) -> str:
        expr = self.to_canonical_expression()
        return hashlib.sha256(expr.encode()).hexdigest()[:16]


class AlgorithmGrammar:
    """Grammar rules, generator, and validator for compositional algorithm discovery."""

    @staticmethod
    def validate_composition(algo: CompositeAlgorithm, contract: WorkloadContract) -> Tuple[bool, List[str]]:
        """Ensures a proposed composition does not violate structural grammar or contract rules."""
        violations = []

        # Exactness constraint
        if contract.correctness == CorrectnessRequirement.EXACT:
            has_unbounded_approx = (
                algo.approximation in [GrammarOperator.APPROXIMATE, GrammarOperator.QUANTIZE]
                and algo.correction_strategy != GrammarOperator.CORRECT
            )
            if has_unbounded_approx:
                violations.append("Exact contract forbids uncorrected approximation or quantization")

        # Cache policy constraint
        if contract.cache_policy.value == "COLD" and algo.reuse in [GrammarOperator.CACHE, GrammarOperator.REUSE]:
            violations.append("Contract specifies COLD cache; reuse/cache operators are invalid")

        return len(violations) == 0, violations

    @staticmethod
    def generate_candidate_combinations(
        contract: WorkloadContract,
        workload_traits: Dict[str, Any]
    ) -> List[CompositeAlgorithm]:
        """Generates legal compositional candidates tailored to the workload traits."""
        candidates = []

        # 1. Output Projection + Reorder (Extreme wormhole for vector projections)
        if workload_traits.get("is_vector_projection", False):
            candidates.append(CompositeAlgorithm(
                representation=GrammarOperator.DENSE,
                ordering=GrammarOperator.OUTPUT_PROJECT,
                decomposition=GrammarOperator.SPLIT,
                communication_strategy=GrammarOperator.COMMUNICATION_AVOID
            ))

        # 2. Candidate: Low-Rank + Residual Correction
        if workload_traits.get("rank_ratio", 1.0) < 0.6:
            candidates.append(CompositeAlgorithm(
                representation=GrammarOperator.LOW_RANK,
                decomposition=GrammarOperator.FACTOR,
                correction_strategy=GrammarOperator.CORRECT,
                verification_strategy=GrammarOperator.SPECULATE
            ))

        # 3. Candidate: Sparse + Conditional Pruning
        if workload_traits.get("sparsity", 0.0) > 0.35:
            candidates.append(CompositeAlgorithm(
                representation=GrammarOperator.SPARSE,
                decomposition=GrammarOperator.BLOCK,
                ordering=GrammarOperator.CONDITIONAL,
                memory_strategy=GrammarOperator.COMPRESS
            ))

        # 4. Candidate: Temporal Delta + Event Driven + Reuse
        if contract.cache_policy.value == "WARM" or workload_traits.get("has_prior_state", False):
            candidates.append(CompositeAlgorithm(
                representation=GrammarOperator.DELTA,
                decomposition=GrammarOperator.EVENT_DRIVEN,
                reuse=GrammarOperator.REUSE,
                correction_strategy=GrammarOperator.CORRECT
            ))

        # 5. Candidate: Spectral FFT Convolution
        if workload_traits.get("is_convolution", False):
            candidates.append(CompositeAlgorithm(
                representation=GrammarOperator.FFT,
                ordering=GrammarOperator.REORDER,
                memory_strategy=GrammarOperator.MEMORY_AVOID
            ))

        # 6. Fallback Baseline Candidate: Dense
        candidates.append(CompositeAlgorithm(
            representation=GrammarOperator.DENSE,
            ordering=GrammarOperator.TILE,
            memory_strategy=GrammarOperator.MEMORY_AVOID
        ))

        # Filter against contract admissibility
        valid_candidates = []
        for c in candidates:
            is_valid, _ = AlgorithmGrammar.validate_composition(c, contract)
            if is_valid:
                valid_candidates.append(c)

        return valid_candidates
