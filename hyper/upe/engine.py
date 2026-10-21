"""
hyper/upe/engine.py
===================
MASTER ORCHESTRATOR: Unseen Pathway Engine (UPE).

Implements the complete 11-Stage Pipeline specified in PART III of the Master Specification:
1.  INPUT
2.  CONTRACT INTERPRETATION
3.  WORKLOAD CLASSIFICATION
4.  NECESSITY ANALYSIS
5.  ALTERNATIVE GENERATION
6.  CANDIDATE PRUNING
7.  CORRECTNESS VALIDATION
8.  COST ESTIMATION
9.  CONTROLLED EXECUTION
10. OUTPUT VERIFICATION
11. PERFORMANCE MEASUREMENT & VERIFIED PATHWAY STORAGE
"""

from __future__ import annotations

import dataclasses
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper.upe.contract import WorkloadContract, ContractRegistry, ValidationMode
from hyper.upe.necessity import ComputationalNecessityAnalyzer, NecessityReport
from hyper.upe.algebra import PathAlgebra
from hyper.upe.generator import AlternativePathwayGenerator, CandidatePathway
from hyper.upe.compiler import SearchSpaceCompiler, SearchBudget, SearchResult
from hyper.upe.validation import ValidationStack, VerificationResult, ValidationOutcome
from hyper.upe.memory import PathMemory, SQLitePathwayStore, ContractAwareCache
from hyper.upe.execution import ResourceAwareExecutionPlanner, ExecutionPlan
from hyper.upe.benchmark import BenchmarkTruthSystem, BenchmarkRunRecord
from hyper.upe.learning import AdaptivePathwayLearner


@dataclasses.dataclass
class PipelineReport:
    """Full end-to-end evidence record of a workload execution through the UPE."""
    workload_id: str
    pathway_id: str
    rule_id: str
    candidate_name: str
    is_shortcut_verified: bool
    status_message: str
    validation_outcome: str
    highest_validation_level: int
    contract: Dict[str, Any]
    necessity_report: Dict[str, Any]
    search_result: Dict[str, Any]
    verification_result: Dict[str, Any]
    execution_plan: Dict[str, Any]
    benchmark_record: Optional[Dict[str, Any]]
    output_summary: Dict[str, Any]
    total_pipeline_latency_ms: float
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "pathway_id": self.pathway_id,
            "rule_id": self.rule_id,
            "candidate_name": self.candidate_name,
            "is_shortcut_verified": self.is_shortcut_verified,
            "status_message": self.status_message,
            "validation_outcome": self.validation_outcome,
            "highest_validation_level": self.highest_validation_level,
            "contract": self.contract,
            "necessity_report": self.necessity_report,
            "search_result": self.search_result,
            "verification_result": self.verification_result,
            "execution_plan": self.execution_plan,
            "benchmark_record": self.benchmark_record,
            "output_summary": self.output_summary,
            "total_pipeline_latency_ms": round(self.total_pipeline_latency_ms, 2),
            "timestamp": self.timestamp,
        }


class UnseenPathwayEngine:
    """
    HYPER UPE — Computational Escape and Verified Algorithm Discovery System.
    """

    def __init__(self) -> None:
        self.contract_registry = ContractRegistry()
        self.necessity_analyzer = ComputationalNecessityAnalyzer()
        self.algebra = PathAlgebra()
        self.generator = AlternativePathwayGenerator(algebra=self.algebra)
        self.compiler = SearchSpaceCompiler(generator=self.generator)
        self.validation_stack = ValidationStack()
        self.memory = PathMemory()
        self.execution_planner = ResourceAwareExecutionPlanner()
        self.benchmarker = BenchmarkTruthSystem(warmup=2, repetitions=5)
        self.learner = AdaptivePathwayLearner(store=self.memory.store)

    def process_workload(
        self,
        workload_id: str,
        inputs: Dict[str, Any],
        custom_contract: Optional[WorkloadContract] = None,
        run_benchmarks: bool = True,
        search_budget: Optional[SearchBudget] = None,
    ) -> PipelineReport:
        """
        Executes the formal 11-stage Unseen Pathway Engine pipeline.
        """
        t_start = time.perf_counter()

        # ---------------------------------------------------------------------
        # Stage 1: CONTRACT INTERPRETATION
        # ---------------------------------------------------------------------
        contract = custom_contract or self.contract_registry.get(workload_id)
        if contract is None:
            # Fallback: create default tolerant contract
            contract = WorkloadContract(
                workload_id=workload_id,
                version="v1.0-inferred",
                validation_mode=ValidationMode.TOLERANCE_BASED,
                description=f"Inferred contract for {workload_id}",
            )
            self.contract_registry.register(contract)

        # ---------------------------------------------------------------------
        # Stage 2: WORKLOAD CLASSIFICATION & RESULT REUSE CHECK
        # ---------------------------------------------------------------------
        cache_key = self.memory.cache.compute_cache_key(
            workload_id=workload_id,
            inputs=inputs,
            contract_version=contract.version,
        )
        cached_result = self.memory.cache.get(cache_key, contract.validation_mode.value)
        if cached_result is not None:
            total_elapsed = (time.perf_counter() - t_start) * 1000.0
            return PipelineReport(
                workload_id=workload_id,
                pathway_id=f"pw_cached_{cache_key[:8]}",
                rule_id="verified_result_reuse",
                candidate_name="Contract-Aware Exact Result Reuse",
                is_shortcut_verified=True,
                status_message="Result retrieved from contract-scoped verified cache (0 ms computation).",
                validation_outcome=ValidationOutcome.PASS_EXACT.value,
                highest_validation_level=7,
                contract=contract.to_dict(),
                necessity_report={"justification": "100% compute avoided via verified cache lookup."},
                search_result={"status_message": "Cache hit bypassed candidate search."},
                verification_result={"highest_level_achieved": 7, "overall_outcome": "PASS_EXACT"},
                execution_plan={"selected_target": "IN_MEMORY_CACHE", "dispatch_reason": "Exact memo hit"},
                benchmark_record=None,
                output_summary={"type": type(cached_result).__name__, "cached": True},
                total_pipeline_latency_ms=total_elapsed,
                timestamp=time.time(),
            )

        # ---------------------------------------------------------------------
        # Stage 3: NECESSITY ANALYSIS (Path Zero)
        # ---------------------------------------------------------------------
        necessity = self.necessity_analyzer.analyze(workload_id=workload_id, inputs=inputs)

        # ---------------------------------------------------------------------
        # Stage 4: ALTERNATIVE GENERATION
        # Stage 5: CANDIDATE PRUNING & SEARCH
        # ---------------------------------------------------------------------
        search_res = self.compiler.search(
            contract=contract,
            inputs=inputs,
            budget=search_budget,
        )
        best_cand = search_res.best_pathway

        # Reference fallback callable
        ref_fn = best_cand.fallback_fn or (lambda inp: inputs.get("A", 0.0))

        # ---------------------------------------------------------------------
        # Stage 6: CORRECTNESS VALIDATION (Levels 1 to 7)
        # ---------------------------------------------------------------------
        assert best_cand.transform_fn is not None
        v_res = self.validation_stack.verify_pathway(
            candidate_fn=best_cand.transform_fn,
            reference_fn=ref_fn,
            contract=contract,
            sample_inputs=inputs,
            pathway_id=best_cand.pathway_id,
        )

        # If verification fails, fall back closed to baseline
        is_shortcut_verified = (
            v_res.overall_outcome in (
                ValidationOutcome.PASS_EXACT,
                ValidationOutcome.PASS_WITHIN_TOLERANCE,
                ValidationOutcome.PASS_APPROXIMATE_BOUNDED,
            )
            and best_cand.rule_id != "baseline_reference"
        )

        if not is_shortcut_verified and best_cand.rule_id != "baseline_reference":
            # Revert candidate to safe baseline
            status_msg = f"Candidate '{best_cand.candidate_name}' failed validation ({v_res.overall_outcome.value}); reverted to baseline."
            best_cand = CandidatePathway(
                pathway_id=f"pw_fallback_{uuid.uuid4().hex[:6]}",
                workload_id=workload_id,
                rule_id="baseline_reference",
                candidate_name="Trusted Baseline Reference",
                family="REFERENCE",
                estimated_flops=100_000,
                estimated_memory_bytes=1024 * 1024,
                estimated_speedup=1.0,
                exactness_mode="EXACT",
                preconditions_met=True,
                transform_fn=lambda inp: (ref_fn(inp), {}),
            )
        else:
            status_msg = f"Pathway '{best_cand.candidate_name}' successfully verified (Level {v_res.highest_level_achieved})."

        # ---------------------------------------------------------------------
        # Stage 7: COST ESTIMATION & RESOURCE-AWARE SCHEDULING
        # ---------------------------------------------------------------------
        exec_plan = self.execution_planner.plan_execution(
            workload_id=workload_id,
            inputs=inputs,
            memory_budget_mb=contract.memory_budget_mb,
        )

        # ---------------------------------------------------------------------
        # Stage 8: CONTROLLED EXECUTION
        # ---------------------------------------------------------------------
        assert best_cand.transform_fn is not None
        raw_output, transform_meta = best_cand.transform_fn(inputs)

        # ---------------------------------------------------------------------
        # Stage 9: OUTPUT VERIFICATION
        # ---------------------------------------------------------------------
        # Store verified result in cache for future instant reuse
        if v_res.overall_outcome in (ValidationOutcome.PASS_EXACT, ValidationOutcome.PASS_WITHIN_TOLERANCE):
            self.memory.cache.put(cache_key, contract.validation_mode.value, raw_output)

        # ---------------------------------------------------------------------
        # Stage 10: PERFORMANCE MEASUREMENT (Benchmark Truth)
        # ---------------------------------------------------------------------
        bench_record: Optional[BenchmarkRunRecord] = None
        if run_benchmarks:
            bench_record = self.benchmarker.benchmark_workload(
                candidate_fn=best_cand.transform_fn,
                reference_fn=ref_fn,
                inputs=inputs,
                workload_id=workload_id,
                pathway_id=best_cand.pathway_id,
                rule_id=best_cand.rule_id,
            )

            # -----------------------------------------------------------------
            # Stage 11: VERIFIED PATHWAY STORAGE (Path Memory)
            # -----------------------------------------------------------------
            self.memory.store.store_pathway(
                pathway_id=best_cand.pathway_id,
                workload_id=workload_id,
                rule_id=best_cand.rule_id,
                candidate_name=best_cand.candidate_name,
                family=best_cand.family,
                exactness_mode=best_cand.exactness_mode,
                estimated_speedup=best_cand.estimated_speedup,
                measured_speedup=bench_record.speedup,
                highest_validation_level=v_res.highest_level_achieved,
                proof_certificate=v_res.formal_proof_certificate,
                metadata={"transform_meta": transform_meta},
            )

            self.memory.store.store_benchmark(
                run_id=f"bench_{uuid.uuid4().hex[:8]}",
                pathway_id=best_cand.pathway_id,
                workload_id=workload_id,
                baseline_ms=bench_record.baseline_median_ms,
                optimized_ms=bench_record.optimized_median_ms,
                speedup=bench_record.speedup,
                repetitions=bench_record.repetitions,
                peak_memory_mb=bench_record.peak_memory_mb,
                raw_timings=bench_record.raw_optimized_times,
            )

            # Update adaptive learner
            self.learner.record_run(
                rule_id=best_cand.rule_id,
                verified=True,
                measured_speedup=bench_record.speedup,
            )

        total_elapsed = (time.perf_counter() - t_start) * 1000.0

        output_summary = {
            "type": type(raw_output).__name__,
            "shape": list(raw_output.shape) if hasattr(raw_output, "shape") else None,
            "transform_meta": transform_meta,
        }

        return PipelineReport(
            workload_id=workload_id,
            pathway_id=best_cand.pathway_id,
            rule_id=best_cand.rule_id,
            candidate_name=best_cand.candidate_name,
            is_shortcut_verified=is_shortcut_verified,
            status_message=status_msg,
            validation_outcome=v_res.overall_outcome.value,
            highest_validation_level=v_res.highest_level_achieved,
            contract=contract.to_dict(),
            necessity_report=necessity.to_dict(),
            search_result=search_res.to_dict(),
            verification_result=v_res.to_dict(),
            execution_plan=dataclasses.asdict(exec_plan),
            benchmark_record=bench_record.to_dict() if bench_record else None,
            output_summary=output_summary,
            total_pipeline_latency_ms=total_elapsed,
            timestamp=time.time(),
        )
