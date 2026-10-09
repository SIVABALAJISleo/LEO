"""
hyper/parity_engine/counterfactual_engine.py
============================================
Counterfactual Hypothesis & Elimination Engine.
Implements Section 10 of the HYPER 100% Master Mission.

Evaluates the 13 Canonical Counterfactual Questions:
1. What happens if we do not perform this? (Omission)
2. What happens if we perform only part of it? (Partial Execution / Truncation)
3. What happens if we reuse its previous result? (Temporal / Cache Reuse)
4. What happens if we reconstruct it? (Spatial / Surrogate Reconstruction)
5. What happens if we derive it mathematically? (Analytical Closed Form)
6. What happens if we change its representation? (Frequency / Compressed / Sparse)
7. What happens if we reorder it? (Commutativity / Loop Reordering)
8. What happens if we fuse it? (Kernel / Operator Fusion)
9. What happens if we sparsify it? (Thresholding / Structured Zeroing)
10. What happens if we compute only the changed region? (Dirty Region / Delta)
11. What happens if CPU performs it? (AVX-512 / Vectorized Core)
12. What happens if iGPU performs it? (DirectCompute / OpenCL / Vulkan)
13. What happens if CPU and iGPU cooperate? (Heterogeneous Task Partitioning)

Transforms every counterfactual hypothesis into a testable experiment.
"""

from __future__ import annotations
import enum
import uuid
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field

from .pathway_ir import PathwayIR, TargetDevicePlacement, TransformationRecord, TransformationType
from .workload_decomposer import DecomposedWorkload, SubOperation


class CounterfactualType(str, enum.Enum):
    OMIT_COMPLETELY = "OMIT_COMPLETELY"
    PARTIAL_EXECUTION = "PARTIAL_EXECUTION"
    REUSE_PREVIOUS = "REUSE_PREVIOUS"
    RECONSTRUCT = "RECONSTRUCT"
    DERIVE_MATHEMATICALLY = "DERIVE_MATHEMATICALLY"
    CHANGE_REPRESENTATION = "CHANGE_REPRESENTATION"
    REORDER = "REORDER"
    FUSE_OPERATORS = "FUSE_OPERATORS"
    SPARSIFY = "SPARSIFY"
    DELTA_DIRTY_REGION = "DELTA_DIRTY_REGION"
    CPU_EXECUTION = "CPU_EXECUTION"
    IGPU_EXECUTION = "IGPU_EXECUTION"
    CPU_IGPU_COOPERATIVE = "CPU_IGPU_COOPERATIVE"


class CounterfactualHypothesis(BaseModel):
    hypothesis_id: str = Field(default_factory=lambda: f"CFH_{uuid.uuid4().hex[:8]}")
    target_operation: str
    counterfactual_type: CounterfactualType
    question: str
    expected_speedup: float
    expected_work_reduction: float
    potential_information_loss: float
    mathematical_justification: str
    experiment_runnable: bool = True


class CounterfactualResult(BaseModel):
    hypothesis_id: str
    counterfactual_type: CounterfactualType
    is_valid: bool
    measured_speedup: float = 1.0
    measured_work_reduction: float = 0.0
    error_introduced: float = 0.0
    verification_passed: bool = False
    survivor_verdict: str = "PENDING"
    notes: str = ""


class CounterfactualEngine:
    """
    Attacks computational workloads by formulating counterfactual alternatives to brute-force execution.
    """

    @staticmethod
    def generate_counterfactuals(decomposed: DecomposedWorkload) -> List[CounterfactualHypothesis]:
        hypotheses: List[CounterfactualHypothesis] = []

        for op in decomposed.operations:
            # 1. Omit Completely
            if op.can_be_eliminated or not op.is_strictly_necessary:
                hypotheses.append(
                    CounterfactualHypothesis(
                        target_operation=op.name,
                        counterfactual_type=CounterfactualType.OMIT_COMPLETELY,
                        question=f"What happens if we do not perform {op.name}?",
                        expected_speedup=1.15,
                        expected_work_reduction=0.15,
                        potential_information_loss=0.0,
                        mathematical_justification="Operation contributes zero or negligible information to contracted output.",
                    )
                )

            # 2. Reuse Previous Result
            hypotheses.append(
                CounterfactualHypothesis(
                    target_operation=op.name,
                    counterfactual_type=CounterfactualType.REUSE_PREVIOUS,
                    question=f"What happens if we reuse the previous result of {op.name}?",
                    expected_speedup=2.5,
                    expected_work_reduction=0.70,
                    potential_information_loss=0.0,
                    mathematical_justification="Temporal continuity and cache hits yield exact or contract-equivalent state.",
                )
            )

            # 3. Change Representation (Frequency, Sparse, Low-Rank)
            hypotheses.append(
                CounterfactualHypothesis(
                    target_operation=op.name,
                    counterfactual_type=CounterfactualType.CHANGE_REPRESENTATION,
                    question=f"What happens if we change the mathematical representation of {op.name}?",
                    expected_speedup=1.8,
                    expected_work_reduction=0.45,
                    potential_information_loss=1e-5,
                    mathematical_justification="Operating in spectral, factorized, or compressed basis reduces complexity.",
                )
            )

            # 4. Sparsify
            hypotheses.append(
                CounterfactualHypothesis(
                    target_operation=op.name,
                    counterfactual_type=CounterfactualType.SPARSIFY,
                    question=f"What happens if we sparsify the data in {op.name}?",
                    expected_speedup=1.6,
                    expected_work_reduction=0.35,
                    potential_information_loss=1e-6,
                    mathematical_justification="Near-zero entries contribute negligibly to IEEE-754 output sum.",
                )
            )

            # 5. Delta / Dirty Region
            hypotheses.append(
                CounterfactualHypothesis(
                    target_operation=op.name,
                    counterfactual_type=CounterfactualType.DELTA_DIRTY_REGION,
                    question=f"What happens if we compute only the changed region in {op.name}?",
                    expected_speedup=3.0,
                    expected_work_reduction=0.75,
                    potential_information_loss=0.0,
                    mathematical_justification="F(S + d S) = F(S) + d F; only evaluate delta where d S != 0.",
                )
            )

            # 6. Heterogeneous Placement
            hypotheses.append(
                CounterfactualHypothesis(
                    target_operation=op.name,
                    counterfactual_type=CounterfactualType.CPU_IGPU_COOPERATIVE,
                    question=f"What happens if CPU and iGPU cooperate on {op.name}?",
                    expected_speedup=1.9,
                    expected_work_reduction=0.10,
                    potential_information_loss=0.0,
                    mathematical_justification="Memory-bound portion to UMA cache, compute-bound portion to iGPU execution units.",
                )
            )

        return hypotheses

    @staticmethod
    def test_hypothesis(
        hypothesis: CounterfactualHypothesis,
        baseline_fn: Callable[[], Any],
        candidate_fn: Callable[[], Any],
        contract_validator: Callable[[Any, Any], Tuple[bool, float]],
    ) -> CounterfactualResult:
        """
        Executes the counterfactual hypothesis as an empirical experiment and records the survivor verdict.
        """
        t0 = time.perf_counter()
        base_out = baseline_fn()
        base_time = max(time.perf_counter() - t0, 1e-6)

        t1 = time.perf_counter()
        try:
            cand_out = candidate_fn()
            cand_time = max(time.perf_counter() - t1, 1e-6)
            is_valid, error_val = contract_validator(cand_out, base_out)
        except Exception as e:
            return CounterfactualResult(
                hypothesis_id=hypothesis.hypothesis_id,
                counterfactual_type=hypothesis.counterfactual_type,
                is_valid=False,
                measured_speedup=0.0,
                measured_work_reduction=0.0,
                error_introduced=float("inf"),
                verification_passed=False,
                survivor_verdict="REJECTED_RUNTIME_ERROR",
                notes=f"Exception during counterfactual candidate execution: {str(e)}",
            )

        speedup = base_time / cand_time
        work_red = max(0.0, min(1.0, 1.0 - (cand_time / base_time)))

        verdict = "SURVIVED_AND_VERIFIED" if is_valid else "REJECTED_CONTRACT_VIOLATION"

        return CounterfactualResult(
            hypothesis_id=hypothesis.hypothesis_id,
            counterfactual_type=hypothesis.counterfactual_type,
            is_valid=is_valid,
            measured_speedup=round(speedup, 3),
            measured_work_reduction=round(work_red, 3),
            error_introduced=error_val,
            verification_passed=is_valid,
            survivor_verdict=verdict,
            notes=f"Execution completed in {cand_time*1000.0:.2f}ms vs baseline {base_time*1000.0:.2f}ms.",
        )
