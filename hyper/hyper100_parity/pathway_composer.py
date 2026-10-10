"""
hyper/hyper100_parity/pathway_composer.py
==========================================
Pathway Composition & Interaction Re-Verification Engine (Section 35).

Implements:
1. Combinatorial Pathway Composition:
   If verified transformations exist:
     T_A = verified
     T_B = verified
     T_C = verified
   Composes and explores:
     T_A + T_B
     T_A + T_C
     T_B + T_C
     T_A + T_B + T_C

2. Strict Re-Verification Mandate:
   Every composed candidate MUST enter the verification gauntlet independently.
   Rule: Never assume individually valid transformations remain valid when composed.
   Detects destructive interference, numerical drift, and cache conflicts.
"""

from __future__ import annotations
import copy
import itertools
from typing import Any, Callable, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from .pathway_ir import PathwayIR, TransformationRecord
from .contract_engine import PerformanceContract
from .verification_engine import IndependentVerifier, VerificationResult


class CompositionResult(BaseModel):
    composed_pathway_id: str
    constituent_transformations: List[str]
    composition_valid: bool
    interaction_type: str  # SYNERGISTIC, NEUTRAL, DESTRUCTIVE_INTERFERENCE
    compounded_speedup: float
    verification: Optional[Dict[str, Any]] = None


class PathwayComposer:
    """
    Composes verified transformations and rigorously re-verifies joint behavior.
    """

    def __init__(self, verifier: Optional[IndependentVerifier] = None) -> None:
        self.verifier = verifier or IndependentVerifier()

    def compose_transformations(
        self,
        base_pathway: PathwayIR,
        available_transformations: List[TransformationRecord],
        reference_fn: Callable[[Any], Any],
        candidate_builder_fn: Callable[[List[str]], Callable[[Any], Any]],
        sample_input: Any,
        contract: PerformanceContract,
    ) -> List[CompositionResult]:
        """
        Generates 2-way and 3-way compositions and re-verifies each one on sample input.
        """
        results: List[CompositionResult] = []

        # Generate combinations of length 2 and 3
        combos: List[List[TransformationRecord]] = []
        for r in range(2, min(4, len(available_transformations) + 1)):
            for comb in itertools.combinations(available_transformations, r):
                combos.append(list(comb))

        for comb in combos:
            names = [t.name for t in comb]
            comp_id = f"pw-comp-{'-'.join([n[:4] for n in names])}"

            # Build composite candidate callable
            composed_fn = candidate_builder_fn(names)

            # Re-verify composition
            vr = self.verifier.verify(
                workload_name=f"Composed_{comp_id}",
                reference_fn=reference_fn,
                candidate_fn=composed_fn,
                sample_input=sample_input,
                contract=contract,
            )

            # Calculate interaction type
            if vr.is_correct and vr.measured_speedup > 1.3:
                interaction = "SYNERGISTIC"
            elif vr.is_correct:
                interaction = "NEUTRAL"
            else:
                interaction = "DESTRUCTIVE_INTERFERENCE"

            results.append(
                CompositionResult(
                    composed_pathway_id=comp_id,
                    constituent_transformations=names,
                    composition_valid=vr.is_correct,
                    interaction_type=interaction,
                    compounded_speedup=vr.measured_speedup,
                    verification=vr.model_dump(),
                )
            )

        return results
