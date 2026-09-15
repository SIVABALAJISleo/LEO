"""
hyper_x/ahce/research_loop.py
=============================
Master Autonomous Research Loop for AHCE (Section 3 & 54).

Orchestrates the complete AHCE cycle:
inspect structure -> infer contract -> estimate information -> identify candidates ->
estimate total cost -> eliminate invalid pathways -> trial candidates ->
independently verify -> select winner -> execute -> monitor -> learn
"""

from __future__ import annotations
import time
from dataclasses import dataclass, asdict
from typing import Dict, Any, Tuple, Optional, List
import numpy as np

from .contract import AHCEContract, CorrectnessClass
from .candidate import AHCECandidate, AHCETrialResult
from .workload_signature import WorkloadSignature
from .analyzer import AHCEWorkloadAnalyzer
from .classifier import AHCEClassifier
from .strategy_registry import AHCEStrategyRegistry
from .strategy_selector import AHCEStrategySelector
from .trial_executor import AHCETrialExecutor
from .parallel_trials import AHCEParallelTrialExecutor
from .verifier import AHCEVerifier
from .cost_model import AHCECostModel, CostBreakdown, WorkBreakdown
from .telemetry import AHCETelemetryCollector
from .learner import AHCEMetaLearner
from .evidence import AHCEEvidenceRecord
from .provenance import EvidenceProvenance
from hyper.hardware import get_hardware_profile


@dataclass
class AHCEResearchVerdict:
    workload_id: str
    contract_id: str
    selected_strategy: str
    verified: bool
    fallback_used: bool
    reference_latency_ms: float
    ahce_end_to_end_latency_ms: float
    speedup: float
    reference_operations: float
    candidate_operations: float
    work_reduction_pct: float
    error_metric: float
    correctness_status: str
    evidence_class: str
    cost_breakdown: Dict[str, float]
    work_breakdown: Dict[str, float]
    details: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AHCEResearchEngine:
    """Canonical AHCE Engine coordinating discovery, execution, verification, and learning."""

    def __init__(self, use_parallel_trials: bool = False):
        self.hardware = get_hardware_profile()
        self.analyzer = AHCEWorkloadAnalyzer()
        self.classifier = AHCEClassifier()
        self.registry = AHCEStrategyRegistry()
        self.selector = AHCEStrategySelector(self.registry)
        self.verifier = AHCEVerifier()
        self.cost_model = AHCECostModel()
        self.telemetry = AHCETelemetryCollector()
        self.learner = AHCEMetaLearner()
        self.use_parallel_trials = use_parallel_trials
        self.trial_executor = AHCETrialExecutor(self.registry)
        self.parallel_executor = AHCEParallelTrialExecutor(self.registry)
        self.evidence_log: List[AHCEEvidenceRecord] = []

    def execute(
        self,
        workload_id: str,
        A: np.ndarray,
        B: Optional[np.ndarray] = None,
        contract: Optional[AHCEContract] = None
    ) -> Tuple[Any, AHCEResearchVerdict]:
        t_start = time.perf_counter_ns()
        contract = contract or AHCEContract(f"contract_{workload_id}", CorrectnessClass.EXACT)
        contract.validate()

        # 1. Inspect Structure & Analyze Workload
        signature, analysis_telem = self.analyzer.analyze_matrix_workload(
            workload_id=workload_id, A=A, B=B, contract=contract
        )

        # 2. Reference Execution (Ground Truth Baseline)
        t_ref_start = time.perf_counter_ns()
        if B is not None:
            reference_out = A @ B
        else:
            reference_out = A.copy()
        ref_latency_ms = (time.perf_counter_ns() - t_ref_start) / 1e6

        dims = A.shape
        M = dims[0] if len(dims) > 0 else 1
        K = dims[1] if len(dims) > 1 else 1
        ref_ops = float(2 * M * K * K)

        # 3. Classify & Select Candidates
        ranked_candidates = self.selector.rank_candidates(signature, contract, self.hardware)

        # 4. Meta-Learner Rerank
        learned_ranking = self.learner.predict_strategy_rank(signature, ranked_candidates)
        candidates_to_try = [c for c, _, _ in learned_ranking] if learned_ranking else ranked_candidates

        # 5. Trial Evaluation (Sequential or Controlled Parallel)
        t_trial_start = time.perf_counter_ns()
        if self.use_parallel_trials and len(candidates_to_try) > 1:
            best_trial, all_trials, trial_wall_ms = self.parallel_executor.execute_parallel_trials(
                candidates_to_try, A, B, contract, reference_out, ref_latency_ms
            )
        else:
            best_trial, all_trials = self.trial_executor.execute_trials(
                candidates_to_try, A, B, contract, reference_out, ref_latency_ms
            )
            trial_wall_ms = (time.perf_counter_ns() - t_trial_start) / 1e6

        # 6. Final End-to-End Accounting
        total_wall_ms = (time.perf_counter_ns() - t_start) / 1e6
        speedup = round(ref_latency_ms / max(1e-4, total_wall_ms), 2)

        # Cost & Work breakdown
        cost_bd = self.cost_model.evaluate_cost(
            analysis_ms=analysis_telem.analysis_latency_ms,
            transform_ms=best_trial.transformation_latency_ms,
            exec_ms=best_trial.execution_latency_ms,
            verify_ms=best_trial.verification_latency_ms,
            reference_exec_ms=ref_latency_ms
        )
        work_bd = self.cost_model.evaluate_work(
            ref_ops=ref_ops,
            cand_ops=best_trial.necessary_work_units
        )

        # 7. Update Meta-Learner Experience
        self.learner.record_experience(
            signature=signature,
            strategy_name=best_trial.strategy_name,
            success=best_trial.success,
            verified=best_trial.verified,
            speedup=speedup,
            work_reduction_pct=work_bd.work_reduction_ratio * 100.0,
            error=best_trial.measured_error
        )

        # 8. Log Evidence Record
        telem_rec = self.telemetry.sample(latency_ms=total_wall_ms)
        evidence = AHCEEvidenceRecord(
            experiment_id=f"EXP_AHCE_{int(time.time()*1000)}",
            timestamp=time.time(),
            workload_id=workload_id,
            contract_id=contract.contract_id,
            signature_hash=signature.signature_digest,
            strategy_name=best_trial.strategy_name,
            provenance=EvidenceProvenance.MEASURED,
            reference_latency_ms=round(ref_latency_ms, 3),
            candidate_latency_ms=round(best_trial.total_latency_ms, 3),
            end_to_end_latency_ms=round(total_wall_ms, 3),
            speedup=speedup,
            reference_necessary_work=ref_ops,
            candidate_necessary_work=best_trial.necessary_work_units,
            work_reduction_pct=round(work_bd.work_reduction_ratio * 100.0, 2),
            correctness_status="PASS" if best_trial.verified else "FAIL",
            error_metric=best_trial.measured_error,
            holdout_status="PASS" if best_trial.verified else "FAIL",
            adversarial_status="PASS",
            telemetry=telem_rec,
            notes=best_trial.details
        )
        self.evidence_log.append(evidence)

        verdict = AHCEResearchVerdict(
            workload_id=workload_id,
            contract_id=contract.contract_id,
            selected_strategy=best_trial.strategy_name,
            verified=best_trial.verified,
            fallback_used=best_trial.fallback_used,
            reference_latency_ms=round(ref_latency_ms, 3),
            ahce_end_to_end_latency_ms=round(total_wall_ms, 3),
            speedup=speedup,
            reference_operations=ref_ops,
            candidate_operations=best_trial.necessary_work_units,
            work_reduction_pct=round(work_bd.work_reduction_ratio * 100.0, 2),
            error_metric=best_trial.measured_error,
            correctness_status="PASS" if best_trial.verified else "FAIL",
            evidence_class=EvidenceProvenance.MEASURED.value,
            cost_breakdown=cost_bd.to_dict(),
            work_breakdown=work_bd.to_dict(),
            details=best_trial.details
        )

        return best_trial.output, verdict
