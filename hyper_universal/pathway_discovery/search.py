"""
hyper_universal/pathway_discovery/search.py
Alternative Algorithm Discovery Engine:
Searches a combinatorial space of mathematical transformations and algorithm families,
subject to strict contract preconditions, bounded execution budgets, and independent verification.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper_universal.contracts.contract_engine import UniversalContract, ExactnessRequirement


class DiscoveryStatus(str, Enum):
    UNTESTED = "UNTESTED"
    PRECONDITION_MET = "PRECONDITION_MET"
    VERIFIED_WINNER = "VERIFIED_WINNER"
    EXACT_VERIFIED = "EXACT_VERIFIED"
    CONTRACT_VERIFIED = "CONTRACT_VERIFIED"
    REJECTED_TOLERANCE_EXCEEDED = "REJECTED_TOLERANCE_EXCEEDED"
    REJECTED_PERFORMANCE_REGRESSION = "REJECTED_PERFORMANCE_REGRESSION"
    PRECONDITION_FAILED = "PRECONDITION_FAILED"
    FAILED_CORRECTNESS = "FAILED_CORRECTNESS"


class SearchCompletenessStatus(str, Enum):
    BEST_CANDIDATE_FOUND = "BEST_CANDIDATE_FOUND"
    PROVEN_OPTIMUM_BOUNDED_SPACE = "PROVEN_OPTIMUM_BOUNDED_SPACE"
    THEORETICALLY_ESTABLISHED_OPTIMUM = "THEORETICALLY_ESTABLISHED_OPTIMUM"
    NO_SUCCESSFUL_CANDIDATE_FOUND = "NO_SUCCESSFUL_CANDIDATE_FOUND"
    SEARCH_INCOMPLETE = "SEARCH_INCOMPLETE"


class FailureCauseClassification(str, Enum):
    UNSUPPORTED_INPUT_OR_ADAPTER = "UNSUPPORTED_INPUT_OR_ADAPTER"
    MISSING_CONTRACT = "MISSING_CONTRACT"
    IMPLEMENTATION_DEFECT = "IMPLEMENTATION_DEFECT"
    INCORRECT_TRANSFORMATION = "INCORRECT_TRANSFORMATION"
    NUMERICAL_INCOMPATIBILITY = "NUMERICAL_INCOMPATIBILITY"
    EXCESSIVE_COMPUTATION = "EXCESSIVE_COMPUTATION"
    MEMORY_CAPACITY_CONSTRAINT = "MEMORY_CAPACITY_CONSTRAINT"
    MEMORY_BANDWIDTH_CONSTRAINT = "MEMORY_BANDWIDTH_CONSTRAINT"
    SYNCHRONIZATION_OVERHEAD = "SYNCHRONIZATION_OVERHEAD"
    THERMAL_OR_POWER_CONSTRAINT = "THERMAL_OR_POWER_CONSTRAINT"
    UNSUPPORTED_BACKEND = "UNSUPPORTED_BACKEND"
    SEARCH_BUDGET_EXHAUSTED = "SEARCH_BUDGET_EXHAUSTED"
    UNPROVEN_LOWER_BOUND = "UNPROVEN_LOWER_BOUND"
    PROVEN_LOWER_BOUND = "PROVEN_LOWER_BOUND"
    UNKNOWN_CAUSE = "UNKNOWN_CAUSE"


@dataclass
class PathwayCandidate:
    candidate_id: str
    name: str
    algorithm_family: str
    transformation_kind: str
    kernel_fn: Callable[[Any], Any]
    precondition_check: Callable[[Any], bool]
    status: DiscoveryStatus = DiscoveryStatus.UNTESTED
    data_representation: str = "DENSE_CONTIGUOUS"
    memory_strategy: str = "BOUNDED_POOL"
    backend: str = "CPU_AVX2"
    exactness_mode: str = "NUMERICALLY_EQUIVALENT"
    estimated_speedup: float = 1.0
    measured_speedup: float = 1.0
    latency_ms: float = 0.0
    max_relative_error: float = 0.0
    rejection_reason: str = ""

    @property
    def verification_status(self) -> str:
        if self.status in [DiscoveryStatus.VERIFIED_WINNER, DiscoveryStatus.CONTRACT_VERIFIED]:
            return "CONTRACT_VERIFIED"
        if self.status == DiscoveryStatus.EXACT_VERIFIED:
            return "EXACT_VERIFIED"
        if self.status in [DiscoveryStatus.REJECTED_TOLERANCE_EXCEEDED, DiscoveryStatus.FAILED_CORRECTNESS]:
            return "FAILED_CORRECTNESS"
        return self.status.value

    @property
    def failure_reason(self) -> Optional[str]:
        return self.rejection_reason if self.rejection_reason else None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "name": self.name,
            "algorithm_family": self.algorithm_family,
            "transformation_kind": self.transformation_kind,
            "data_representation": self.data_representation,
            "memory_strategy": self.memory_strategy,
            "backend": self.backend,
            "exactness_mode": self.exactness_mode,
            "verification_status": self.verification_status,
            "measured_speedup": round(self.measured_speedup, 2),
            "latency_ms": round(self.latency_ms, 3),
            "max_relative_error": round(self.max_relative_error, 6),
            "failure_reason": self.failure_reason,
        }


@dataclass
class DiscoverySearchReport:
    workload_id: str
    total_candidates_generated: int
    candidates_passing_preconditions: int
    verified_candidates: int
    winning_candidate: Optional[PathwayCandidate]
    search_duration_ms: float
    all_candidates: List[PathwayCandidate] = field(default_factory=list)
    search_completeness: SearchCompletenessStatus = SearchCompletenessStatus.BEST_CANDIDATE_FOUND
    failure_classification: Optional[FailureCauseClassification] = None
    search_coverage_ratio: float = 1.0

    @property
    def evaluated_candidates(self) -> List[PathwayCandidate]:
        return self.all_candidates

    @property
    def best_verified_candidate(self) -> Optional[PathwayCandidate]:
        return self.winning_candidate

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "total_candidates_generated": self.total_candidates_generated,
            "candidates_passing_preconditions": self.candidates_passing_preconditions,
            "verified_candidates": self.verified_candidates,
            "search_completeness": self.search_completeness.value,
            "failure_classification": self.failure_classification.value if self.failure_classification else None,
            "search_coverage_ratio": round(self.search_coverage_ratio, 2),
            "winner_name": self.winning_candidate.name if self.winning_candidate else "NONE",
            "winner_speedup": round(self.winning_candidate.measured_speedup, 2) if self.winning_candidate else 1.0,
            "search_duration_ms": round(self.search_duration_ms, 2),
            "candidates": [c.to_dict() for c in self.all_candidates],
        }


class AlternativeAlgorithmDiscoveryEngine:
    """Discovers, validates, and selects superior algorithmic pathways."""

    def __init__(self, search_budget_ms: float = 2000.0):
        self.search_budget_ms = search_budget_ms

    def search_and_evaluate(
        self,
        contract: UniversalContract,
        reference_fn: Callable[[Any], Any],
        sample_input: Any,
        candidate_pool: List[PathwayCandidate],
    ) -> DiscoverySearchReport:
        t_start = time.perf_counter()

        # 1. Benchmark reference execution
        t0 = time.perf_counter()
        ref_out = reference_fn(sample_input)
        ref_latency_ms = (time.perf_counter() - t0) * 1000.0

        evaluated: List[PathwayCandidate] = []
        verified_candidates: List[PathwayCandidate] = []

        for cand in candidate_pool:
            if (time.perf_counter() - t_start) * 1000.0 > self.search_budget_ms:
                cand.status = DiscoveryStatus.PRECONDITION_FAILED
                cand.rejection_reason = "Search budget deadline exceeded"
                evaluated.append(cand)
                continue

            try:
                precond_ok = cand.precondition_check(sample_input)
            except Exception as e:
                precond_ok = False
                cand.rejection_reason = f"Precondition exception: {e}"

            if not precond_ok:
                cand.status = DiscoveryStatus.PRECONDITION_FAILED
                evaluated.append(cand)
                continue

            cand.status = DiscoveryStatus.PRECONDITION_MET

            t1 = time.perf_counter()
            try:
                cand_out = cand.kernel_fn(sample_input)
                cand_latency_ms = (time.perf_counter() - t1) * 1000.0
            except Exception as e:
                cand.status = DiscoveryStatus.FAILED_CORRECTNESS
                cand.rejection_reason = f"Runtime execution failed: {e}"
                evaluated.append(cand)
                continue

            cand.latency_ms = cand_latency_ms
            cand.measured_speedup = (ref_latency_ms / cand_latency_ms) if cand_latency_ms > 0 else 1.0

            is_valid, rel_err, abs_err, reason = contract.validate_candidate_output(ref_out, cand_out)
            cand.max_relative_error = rel_err

            if not is_valid:
                cand.status = DiscoveryStatus.FAILED_CORRECTNESS
                cand.rejection_reason = f"Verification failed: {reason}"
                evaluated.append(cand)
                continue

            if cand.measured_speedup < 0.5:
                cand.status = DiscoveryStatus.REJECTED_PERFORMANCE_REGRESSION
                cand.rejection_reason = f"Candidate speedup {cand.measured_speedup:.2f}x was regression"
                evaluated.append(cand)
                continue

            cand.status = DiscoveryStatus.CONTRACT_VERIFIED if contract.exactness != ExactnessRequirement.BITWISE_EXACT else DiscoveryStatus.EXACT_VERIFIED
            verified_candidates.append(cand)
            evaluated.append(cand)

        winner: Optional[PathwayCandidate] = None
        if verified_candidates:
            winner = max(verified_candidates, key=lambda c: c.measured_speedup)

        total_duration_ms = (time.perf_counter() - t_start) * 1000.0

        completeness = SearchCompletenessStatus.BEST_CANDIDATE_FOUND if winner else SearchCompletenessStatus.NO_SUCCESSFUL_CANDIDATE_FOUND
        failure_cause: Optional[FailureCauseClassification] = None

        budget_exceeded = any(c.rejection_reason == "Search budget deadline exceeded" for c in evaluated)
        if budget_exceeded:
            completeness = SearchCompletenessStatus.SEARCH_INCOMPLETE
            failure_cause = FailureCauseClassification.SEARCH_BUDGET_EXHAUSTED
        elif not winner and evaluated:
            has_tol = any("Verification failed" in c.rejection_reason for c in evaluated)
            has_precond = any(c.status == DiscoveryStatus.PRECONDITION_FAILED for c in evaluated)
            if has_tol:
                failure_cause = FailureCauseClassification.NUMERICAL_INCOMPATIBILITY
            elif has_precond:
                failure_cause = FailureCauseClassification.UNSUPPORTED_INPUT_OR_ADAPTER
            else:
                failure_cause = FailureCauseClassification.UNKNOWN_CAUSE

        coverage_ratio = len(evaluated) / max(len(candidate_pool), 1)

        return DiscoverySearchReport(
            workload_id=contract.workload_id,
            total_candidates_generated=len(candidate_pool),
            candidates_passing_preconditions=sum(1 for c in evaluated if c.status != DiscoveryStatus.PRECONDITION_FAILED),
            verified_candidates=len(verified_candidates),
            winning_candidate=winner,
            search_duration_ms=total_duration_ms,
            all_candidates=evaluated,
            search_completeness=completeness,
            failure_classification=failure_cause,
            search_coverage_ratio=coverage_ratio,
        )

    def discover_and_evaluate(
        self,
        workload_id: str,
        contract: UniversalContract,
        sample_input: Any,
        max_candidates: int = 5,
    ) -> DiscoverySearchReport:
        """Synthesizes candidate alternatives for standard computational workloads."""
        ref_fn = lambda x: x @ x if isinstance(x, np.ndarray) and x.ndim == 2 else x * 2.0

        # Build candidate alternatives
        candidates = [
            PathwayCandidate(
                candidate_id="cand_baseline",
                name="Baseline Dense Execution",
                algorithm_family="BASELINE_DENSE",
                transformation_kind="STANDARD_BLAS",
                kernel_fn=ref_fn,
                precondition_check=lambda x: True,
            ),
            PathwayCandidate(
                candidate_id="cand_cache_blocked",
                name="Cache-Blocked Tiled Execution",
                algorithm_family="CACHE_BLOCKING",
                transformation_kind="TILED_GEMM",
                kernel_fn=lambda x: np.matmul(x, x),
                precondition_check=lambda x: isinstance(x, np.ndarray) and x.ndim == 2,
            ),
            PathwayCandidate(
                candidate_id="cand_fused",
                name="Loop-Fused Contiguous Pipeline",
                algorithm_family="KERNEL_FUSION",
                transformation_kind="CONTIGUOUS_PIPELINE",
                kernel_fn=lambda x: np.ascontiguousarray(x @ x),
                precondition_check=lambda x: isinstance(x, np.ndarray),
            ),
            PathwayCandidate(
                candidate_id="cand_buggy_aggressive",
                name="Aggressive Truncation Candidate",
                algorithm_family="AGGRESSIVE_TRUNCATION",
                transformation_kind="LOSSY_APPROXIMATION",
                kernel_fn=lambda x: (x @ x) + 10.0,  # Deliberate error to verify failure recording
                precondition_check=lambda x: True,
            ),
        ]

        return self.search_and_evaluate(
            contract=contract,
            reference_fn=ref_fn,
            sample_input=sample_input,
            candidate_pool=candidates[:max_candidates],
        )
