"""
hyper/escape_engine/__init__.py
===============================
HYPER VERIFIED ALGORITHMIC ESCAPE ENGINE (VAEE)
Verified Adaptive Algorithmic Escape Engine for LEO / HYPER.

Transforms problem solving into:
Problem -> Contract -> Representation -> Transformation -> Candidate -> Execution -> Independent Verification -> Measurement -> Search Update.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from .contracts import (
    ComputationalContract,
    ContractExtractor,
    InformationBoundaryAnalyzer,
    InformationBoundaryProfile,
)
from .pathways import (
    ComputationalPathway,
    PathwayRegistry,
    PathwayGenerator,
    PathwayComposer,
    CANONICAL_TRANSFORMATIONS,
)
from .search import (
    AdaptiveSearchEngine,
    SearchBudget,
    SearchState,
    CandidateEvaluation,
    DiversityEngine,
)
from .execution import (
    ExecutionSandbox,
    CPUExecutor,
    iGPUExecutor,
    UnifiedExecutor,
)
from .verification import (
    MasterVerifier,
    VerificationOutcome,
    VerificationTrustLevel,
    ExactVerifier,
    DifferentialVerifier,
    InvariantVerifier,
    ChecksumVerifier,
)
from .analysis import (
    CostAnalyzer,
    MeasuredCost,
    TheoreticalCost,
    ComplexityAnalyzer,
    MemoryModel,
)
from .ranking import (
    ParetoPoint,
    ParetoFrontier,
    CandidateRanker,
)
from .learning import (
    PathwayHistoryRecord,
    PathwayHistoryStore,
    TransformationStatistics,
    StrategySelector,
)
from .barriers import (
    BarrierDetector,
    BarrierVerdict,
    BarrierClassification,
)
from .reporting import (
    BenchmarkResult,
    ScientificAuditLogger,
    ExperimentManager,
)


class VerifiedAdaptiveEscapeEngine:
    """Master orchestrator for the Verified Adaptive Algorithmic Escape Engine (VAEE)."""

    def __init__(self, seed: int = 42) -> None:
        self.registry = PathwayRegistry()
        self.generator = PathwayGenerator(seed=seed)
        self.search_engine = AdaptiveSearchEngine(registry=self.registry, generator=self.generator)
        self.executor = UnifiedExecutor()
        self.verifier = MasterVerifier()
        self.audit_logger = ScientificAuditLogger()
        self.history_store = PathwayHistoryStore()
        self.stats = TransformationStatistics()
        self.strategy_selector = StrategySelector(self.stats, seed=seed)
        self.frontier = ParetoFrontier()

    def search_pathway(
        self,
        contract: ComputationalContract,
        input_sample: Any,
        reference_fn: Callable[[Any], Any],
        max_candidates: int = 15,
        max_time_seconds: float = 30.0,
    ) -> Dict[str, Any]:
        """
        Full end-to-end adaptive pathway discovery:
        1. Probe information boundary
        2. Establish ground-truth baseline
        3. Search diverse candidate transformations
        4. Independently verify correctness
        5. Measure real execution cost on local hardware
        6. Update Pareto frontier & detect saturation/barriers
        """
        experiment_id = f"EXP-VAEE-{int(time.time()*1000)%1000000:06d}"
        manifest = ExperimentManager.create_manifest(experiment_id, input_sample)

        # 1. Information boundary analysis
        profile = InformationBoundaryAnalyzer.analyze(contract, input_sample)

        # 2. Establish trusted ground-truth reference baseline
        ref_out, base_cost = CostAnalyzer.measure_execution(lambda: reference_fn(input_sample), trials=3)
        baseline_ms = base_cost.wall_clock_ms

        def evaluate_candidate(pathway: ComputationalPathway) -> Tuple[bool, str, float, float]:
            # Bind callable if needed
            if pathway.run_fn is None and contract.input_type == "matrix":
                # Check if input is matrix
                B = np.eye(contract.output_shape[-1], dtype=np.float32) if hasattr(contract, "output_shape") else None
                if B is not None:
                    pathway.run_fn = PathwayComposer.compose_matrix_multiplication(pathway, B)
                else:
                    return False, VerificationTrustLevel.FAILED, 0.0, 0.0
            elif pathway.run_fn is None:
                # Anti-Cheating Rule: Candidate must NOT delegate to reference_fn!
                return False, VerificationTrustLevel.FAILED, 0.0, 0.0

            # Sandboxed execution
            success, out, exec_ms, err = self.executor.execute_pathway(pathway, input_sample)
            if not success or out is None:
                return False, VerificationTrustLevel.FAILED, exec_ms, 0.0

            # Independent verification
            v_res = self.verifier.verify_candidate(
                candidate_output=out,
                reference_output=ref_out,
                contract=contract,
                extra_inputs=input_sample if isinstance(input_sample, tuple) else None,
            )

            # Update Pareto frontier if verified
            if v_res.is_valid:
                speedup = baseline_ms / max(1e-6, exec_ms)
                point = ParetoPoint(
                    pathway=pathway,
                    latency_ms=exec_ms,
                    memory_mb=0.1,
                    energy_mj=35.0 * (exec_ms / 1000.0) * 1000.0,
                    confidence=v_res.confidence_score,
                    speedup_vs_baseline=speedup,
                )
                self.frontier.update(point)

            # Log audit record
            self.audit_logger.log_decision(
                experiment_id=experiment_id,
                workload_name=contract.input_type,
                baseline_latency_ms=baseline_ms,
                candidate_pathway_id=pathway.pathway_id,
                transformations=pathway.transformation_chain,
                verification_method=v_res.method,
                verification_status=v_res.trust_level,
                candidate_latency_ms=exec_ms,
                verified_speedup=baseline_ms / max(1e-6, exec_ms),
                classification="SUCCESS" if v_res.is_valid else "FAILURE",
            )

            # Save in history store
            rec = PathwayHistoryRecord(
                experiment_id=experiment_id,
                workload_type=contract.input_type,
                contract_id=contract.contract_id,
                pathway_id=pathway.pathway_id,
                parent_id=pathway.parent_id,
                transformation_chain=pathway.transformation_chain,
                structural_hash=pathway.structural_hash,
                hardware="Intel Core i5-12450H + Intel UHD 48EU",
                runtime_ms=exec_ms,
                verification_status=v_res.trust_level,
                speedup_vs_baseline=baseline_ms / max(1e-6, exec_ms),
                outcome="SUCCESS" if v_res.is_valid else "FAILURE",
            )
            self.history_store.record(rec)

            return v_res.is_valid, v_res.trust_level, exec_ms, 0.1

        # 3. Adaptive search loop
        budget = SearchBudget(max_candidates=max_candidates, max_time_seconds=max_time_seconds)
        state = self.search_engine.search(
            contract=contract,
            profile=profile,
            evaluate_fn=evaluate_candidate,
            budget=budget,
        )

        # 4. Barrier detection
        barrier_verdict = BarrierDetector.detect_barriers(contract, profile)

        best_speedup = (baseline_ms / max(1e-6, state.best_latency_ms)) if state.best_latency_ms < float("inf") else 1.0

        return {
            "experiment_id": experiment_id,
            "manifest": manifest.to_dict(),
            "contract": contract.to_dict(),
            "information_boundary": profile.to_dict(),
            "baseline_latency_ms": round(baseline_ms, 4),
            "best_latency_ms": round(state.best_latency_ms if state.best_latency_ms < float("inf") else baseline_ms, 4),
            "verified_speedup": round(best_speedup, 2),
            "outcome": state.outcome,
            "barrier_verdict": barrier_verdict.to_dict(),
            "search_statistics": {
                "candidates_evaluated": state.total_evaluated,
                "verified_candidates": state.total_verified,
                "failed_candidates": state.total_failed,
                "diversity_stats": self.registry.get_diversity_stats(),
                "saturation_detected": state.saturation_detected,
                "saturation_reason": state.saturation_reason,
            },
            "best_verified_pathway": state.best_pathway.to_dict() if state.best_pathway else None,
            "pareto_frontier": self.frontier.to_list(),
        }


__all__ = [
    "VerifiedAdaptiveEscapeEngine",
    "ComputationalContract",
    "ContractExtractor",
    "InformationBoundaryAnalyzer",
    "InformationBoundaryProfile",
    "ComputationalPathway",
    "PathwayRegistry",
    "PathwayGenerator",
    "PathwayComposer",
    "AdaptiveSearchEngine",
    "SearchBudget",
    "SearchState",
    "CandidateEvaluation",
    "DiversityEngine",
    "ExecutionSandbox",
    "CPUExecutor",
    "iGPUExecutor",
    "UnifiedExecutor",
    "MasterVerifier",
    "VerificationOutcome",
    "VerificationTrustLevel",
    "ExactVerifier",
    "DifferentialVerifier",
    "InvariantVerifier",
    "ChecksumVerifier",
    "CostAnalyzer",
    "MeasuredCost",
    "TheoreticalCost",
    "ComplexityAnalyzer",
    "MemoryModel",
    "ParetoPoint",
    "ParetoFrontier",
    "CandidateRanker",
    "BarrierDetector",
    "BarrierVerdict",
    "BarrierClassification",
    "ScientificAuditLogger",
    "ExperimentManager",
]
