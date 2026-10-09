"""
hyper/parity_engine/pathway_composer.py
=======================================
Pathway Composition & Transformation Pipeline Integrator.
Implements Section 35 of the HYPER 100% Master Mission.

Core Mandate:
When individual transformations A, B, C are verified:
Test combinations:
  A + B
  A + C
  B + C
  A + B + C
Reverify every composition!
DO NOT assume individually valid transformations remain valid when composed.
"""

from __future__ import annotations
import copy
import itertools
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from .pathway_ir import PathwayIR, TransformationRecord
from .contract_engine import WorkloadContract
from .verification_engine import VerificationEngine, VerificationRecord


class ComposedPathwayResult(BaseModel):
    composition_id: str = Field(default_factory=lambda: f"CMP_{uuid.uuid4().hex[:8]}")
    combined_transformations: List[str]
    is_valid: bool
    composed_speedup: float
    composed_work_reduction: float
    verification_passed: bool
    reverification_status: str
    verification_record: Optional[Dict[str, Any]] = None


class PathwayComposer:
    """
    Composes verified transformations and rigorously re-verifies their collective behavior.
    """

    @staticmethod
    def compose_pathways(
        base_pathway: PathwayIR,
        available_transformations: List[TransformationRecord],
        contract: WorkloadContract,
        execute_composed_fn: Callable[[List[TransformationRecord]], Any],
        reference_fn: Callable[[], Any],
    ) -> List[ComposedPathwayResult]:
        results: List[ComposedPathwayResult] = []

        if len(available_transformations) < 2:
            return results

        # Generate combinations of length 2 and 3
        combos = []
        for k in range(2, min(4, len(available_transformations) + 1)):
            combos.extend(itertools.combinations(available_transformations, k))

        for combo in combos:
            tx_list = list(combo)
            tx_names = [t.type.value for t in tx_list]
            comp_id = f"CMP_{'_'.join([t.type.value[:4] for t in tx_list])}_{uuid.uuid4().hex[:4]}"

            # Independent Re-verification
            try:
                candidate_wrapper = lambda: execute_composed_fn(tx_list)
                vrf_record = VerificationEngine.verify_candidate(
                    workload_id=base_pathway.workload_id,
                    capability_id=base_pathway.capability_id,
                    pathway_id=comp_id,
                    candidate_fn=candidate_wrapper,
                    reference_fn=reference_fn,
                    contract=contract,
                )
                is_valid = vrf_record.is_valid
                speedup = vrf_record.speedup
                work_red = max(0.0, min(1.0, 1.0 - (1.0 / max(speedup, 1.0))))
                verdict = "COMPOSED_AND_REVERIFIED_PASS" if is_valid else "COMPOSED_FAILED_REVERIFICATION"
                vrf_dict = vrf_record.model_dump()
            except Exception as e:
                is_valid = False
                speedup = 0.0
                work_red = 0.0
                verdict = f"COMPOSED_CRASH: {str(e)}"
                vrf_dict = None

            comp_result = ComposedPathwayResult(
                composition_id=comp_id,
                combined_transformations=tx_names,
                is_valid=is_valid,
                composed_speedup=speedup,
                composed_work_reduction=round(work_red, 3),
                verification_passed=is_valid,
                reverification_status=verdict,
                verification_record=vrf_dict,
            )
            results.append(comp_result)

        return results
