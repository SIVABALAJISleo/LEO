"""
hyper_x/wormhole_compiler/llm_hypothesis_engine.py
=============================================================================
LLM Hypothesis Generator & Untrusted Idea Incubator (Phase 14)
=============================================================================
CRITICAL PRINCIPLE:
LLM-generated hypotheses are treated strictly as:
    UNTRUSTED IDEAS
Never as facts.

An LLM is NEVER permitted to declare a candidate:
    PASS, VERIFIED, or CORRECT.

Hierarchy of Authority:
  LLM Output           → HYPOTHESIS
  Compiler             → CANDIDATE PROGRAM
  Multi-Verifier Stack → EMPIRICAL EVIDENCE
  Scientific Auditor   → CERTIFIED CLAIM

Works offline/locally with deterministic pattern seeds; optionally connects
to local Ollama or lightweight models if available, but core optimization
never depends on external or paid APIs.
"""

from __future__ import annotations
import time
import hashlib
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

from hyper_x.wormhole_compiler.contract_ir import UniversalWorkloadContract


@dataclass
class TransformationHypothesis:
    hypothesis_id: str
    target_operation: str
    suggested_transformation: str
    mathematical_rationale: str
    expected_work_reduction_ratio: float
    expected_speedup: float
    applicability_conditions: List[str]
    verification_method_required: str
    is_tested: bool = False
    verification_survived: bool = False
    audit_notes: str = ""
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "target_operation": self.target_operation,
            "suggested_transformation": self.suggested_transformation,
            "mathematical_rationale": self.mathematical_rationale,
            "expected_work_reduction_ratio": round(self.expected_work_reduction_ratio, 4),
            "expected_speedup": round(self.expected_speedup, 2),
            "applicability_conditions": self.applicability_conditions,
            "verification_method_required": self.verification_method_required,
            "is_tested": self.is_tested,
            "verification_survived": self.verification_survived,
            "audit_notes": self.audit_notes,
        }


class LLMHypothesisEngine:
    """
    Synthesizes untrusted candidate optimization hypotheses for evaluation by the verifier stack.
    """

    def __init__(self):
        self.hypothesis_archive: Dict[str, TransformationHypothesis] = {}

    def generate_hypotheses(
        self,
        operation_id: str,
        workload_traits: Dict[str, Any],
        contract: UniversalWorkloadContract,
    ) -> List[TransformationHypothesis]:
        """Generates domain-aware mathematical hypotheses without relying on paid APIs."""
        candidates = []

        rank_ratio = workload_traits.get("rank_ratio", 1.0)
        sparsity = workload_traits.get("sparsity", 0.0)
        is_vector = workload_traits.get("is_vector_projection", False)
        is_exact = contract.is_exact()

        # 1. Associative Output Projection
        if is_vector:
            candidates.append(TransformationHypothesis(
                hypothesis_id=f"HYP_ASSOC_PROJ_{operation_id}",
                target_operation=operation_id,
                suggested_transformation="A @ (B @ x) via Associativity",
                mathematical_rationale="Associativity of matrix multiplication allows O(N^2) instead of O(N^3) materialization.",
                expected_work_reduction_ratio=0.98,
                expected_speedup=12.0,
                applicability_conditions=["downstream_observable_is_vector"],
                verification_method_required="EXACT_ALGEBRAIC_FREIVALDS",
            ))

        # 2. Low-Rank Subspace Projection
        if rank_ratio < 0.50 and contract.allows_approximation():
            candidates.append(TransformationHypothesis(
                hypothesis_id=f"HYP_LOW_RANK_{operation_id}",
                target_operation=operation_id,
                suggested_transformation="Truncated SVD Subspace Projection",
                mathematical_rationale=f"Singular value decay indicates effective rank ratio {rank_ratio:.2f} << 1.0.",
                expected_work_reduction_ratio=0.75,
                expected_speedup=3.2,
                applicability_conditions=["spectral_energy_gt_0.95_at_target_rank"],
                verification_method_required="RELATIVE_FROBENIUS_NORM",
            ))

        # 3. Dynamic Sparsity Coordinate Skipping
        if sparsity > 0.30:
            candidates.append(TransformationHypothesis(
                hypothesis_id=f"HYP_SPARSE_CSR_{operation_id}",
                target_operation=operation_id,
                suggested_transformation="Active Row CSR Coordinate Skipping",
                mathematical_rationale=f"Observed sparsity of {sparsity*100:.1f}% allows bypassing zero-valued multiply-accumulates.",
                expected_work_reduction_ratio=sparsity,
                expected_speedup=1.0 / max(0.1, 1.0 - sparsity),
                applicability_conditions=["coordinate_sparsity_gt_0.30"],
                verification_method_required="EXACT_ELEMENTWISE" if is_exact else "NUMERICAL_TOLERANCE",
            ))

        # 4. Temporal Coherence State Delta
        if contract.cache_policy.value == "WARM":
            candidates.append(TransformationHypothesis(
                hypothesis_id=f"HYP_DELTA_UPDATE_{operation_id}",
                target_operation=operation_id,
                suggested_transformation="Incremental State Delta Update",
                mathematical_rationale="Repeated evaluation under warm cache indicates temporal coherence across consecutive calls.",
                expected_work_reduction_ratio=0.85,
                expected_speedup=5.0,
                applicability_conditions=["temporal_similarity_gt_0.80"],
                verification_method_required="CHECKPOINT_DRIFT_AUDIT",
            ))

        for h in candidates:
            self.hypothesis_archive[h.hypothesis_id] = h

        return candidates
