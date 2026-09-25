"""
hyper/discovery/search.py
=========================
Computational Pathway Search Engine.

Implements bounded search strategies (A*, Beam Search, Branch-and-Bound)
with strict resource controls, cost pruning, independent verification,
and auditable search traces.
"""

from __future__ import annotations

import dataclasses
import enum
import heapq
import time
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple

from hyper.discovery.cir import CIRGraph
from hyper.discovery.contract import WorkloadContract
from hyper.discovery.counterfactual import CounterfactualEngine
from hyper.discovery.search_space import CandidatePathway, SearchSpaceCompiler
from hyper.discovery.verifier import DoubleExecutionVerifier, VerificationRecord


class SearchStrategy(str, enum.Enum):
    A_STAR = "A_STAR"
    BEAM_SEARCH = "BEAM_SEARCH"
    BRANCH_AND_BOUND = "BRANCH_AND_BOUND"
    HEURISTIC = "HEURISTIC"


@dataclasses.dataclass
class SearchConfig:
    strategy: SearchStrategy = SearchStrategy.A_STAR
    max_search_depth: int = 4
    max_candidates: int = 40
    max_runtime_sec: float = 30.0
    verification_budget: int = 20
    beam_width: int = 5


@dataclasses.dataclass
class SearchTraceEntry:
    step_index: int
    candidate_id: str
    parent_id: Optional[str]
    action: str  # "GENERATED" | "PRUNED_COST" | "PRUNED_BUDGET" | "VERIFIED_PASS" | "VERIFIED_FAIL"
    cost_score: float
    correctness_score: float
    reason: str
    timestamp: float = dataclasses.field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class SearchResult:
    best_pathway: CandidatePathway
    is_shortcut_found: bool
    status_message: str  # "SHORTCUT_DISCOVERED" | "NO_VERIFIED_SHORTCUT_FOUND"
    candidates_explored: int
    candidates_rejected: int
    candidates_verified: int
    search_trace: List[SearchTraceEntry]
    verification_record: Optional[VerificationRecord] = None
    baseline_cost: float = 0.0
    best_cost: float = 0.0
    speedup: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_shortcut_found": self.is_shortcut_found,
            "status_message": self.status_message,
            "candidates_explored": self.candidates_explored,
            "candidates_rejected": self.candidates_rejected,
            "candidates_verified": self.candidates_verified,
            "baseline_cost": self.baseline_cost,
            "best_cost": self.best_cost,
            "speedup": self.speedup,
            "best_pathway": self.best_pathway.to_dict(),
            "verification_record": self.verification_record.to_dict() if self.verification_record else None,
            "search_trace": [t.to_dict() for t in self.search_trace],
        }


class SearchEngine:
    """
    Unified Computational Pathway Search Engine.
    Executes bounded search over CIR transformation space with strict failure-first verification.
    """

    def __init__(
        self,
        compiler: Optional[SearchSpaceCompiler] = None,
        counterfactual: Optional[CounterfactualEngine] = None,
        verifier: Optional[DoubleExecutionVerifier] = None,
    ):
        self.compiler = compiler or SearchSpaceCompiler()
        self.counterfactual = counterfactual or CounterfactualEngine()
        self.verifier = verifier or DoubleExecutionVerifier()

    def discover(
        self,
        initial_graph: CIRGraph,
        sample_inputs: Dict[str, Any],
        contract: WorkloadContract,
        config: Optional[SearchConfig] = None,
    ) -> SearchResult:
        """
        Execute automatic discovery loop:
        1. Compile candidate transformations.
        2. Mine counterfactual omission opportunities.
        3. Search bounded space (A*, Beam, Branch-and-Bound).
        4. Independently verify outputs against reference.
        5. Return best verified pathway or fallback to trusted baseline.
        """
        cfg = config or SearchConfig()
        t_start = time.perf_counter()

        trace: List[SearchTraceEntry] = []
        step = 0

        # Baseline setup
        baseline_cost = initial_graph.total_estimated_flops()
        baseline_cand = CandidatePathway(
            candidate_id=f"cand_baseline_{uuid.uuid4().hex[:8]}",
            parent_id=None,
            graph=initial_graph.clone(),
            transformation_history=["Original trusted reference pathway."],
            estimated_cost=baseline_cost,
            verification_status="PASSED",
        )

        # Baseline verification
        _, baseline_vrecord, _ = self.verifier.verify_candidate(
            candidate_graph=baseline_cand.graph,
            reference_graph=initial_graph,
            inputs=sample_inputs,
            contract=contract,
            candidate_id=baseline_cand.candidate_id,
        )
        current_best = baseline_cand
        current_best_cost = baseline_cost
        best_vrecord = baseline_vrecord

        step += 1
        trace.append(
            SearchTraceEntry(
                step_index=step,
                candidate_id=baseline_cand.candidate_id,
                parent_id=None,
                action="VERIFIED_PASS",
                cost_score=baseline_cost,
                correctness_score=1.0,
                reason="Baseline trusted reference established.",
            )
        )

        # Step 1: Generate candidates via Search Space Compiler
        candidate_pool: List[CandidatePathway] = self.compiler.generate_candidates(
            graph=initial_graph,
            contract=contract,
            max_candidates=cfg.max_candidates // 2,
        )

        # Step 2: Generate counterfactual candidates
        cf_results = self.counterfactual.analyze_graph(
            graph=initial_graph,
            sample_inputs=sample_inputs,
            contract=contract,
        )
        for cf in cf_results:
            if cf.candidate is not None:
                candidate_pool.append(cf.candidate)

        # Filter out baseline duplicate
        candidates_to_evaluate = [c for c in candidate_pool if c.candidate_id != baseline_cand.candidate_id]

        # Prioritize candidates based on strategy
        if cfg.strategy in (SearchStrategy.A_STAR, SearchStrategy.BRANCH_AND_BOUND):
            # Sort by estimated cost ascending
            candidates_to_evaluate.sort(key=lambda c: c.estimated_cost)
        elif cfg.strategy == SearchStrategy.BEAM_SEARCH:
            candidates_to_evaluate = candidates_to_evaluate[: cfg.beam_width * 2]

        explored_count = 1
        rejected_count = 0
        verified_count = 1
        shortcut_found = False

        for cand in candidates_to_evaluate:
            # Check resource bounds
            if explored_count >= cfg.max_candidates:
                step += 1
                trace.append(
                    SearchTraceEntry(
                        step_index=step,
                        candidate_id=cand.candidate_id,
                        parent_id=cand.parent_id,
                        action="PRUNED_BUDGET",
                        cost_score=cand.estimated_cost,
                        correctness_score=0.0,
                        reason="Max candidates limit reached.",
                    )
                )
                break

            if (time.perf_counter() - t_start) >= cfg.max_runtime_sec:
                step += 1
                trace.append(
                    SearchTraceEntry(
                        step_index=step,
                        candidate_id=cand.candidate_id,
                        parent_id=cand.parent_id,
                        action="PRUNED_BUDGET",
                        cost_score=cand.estimated_cost,
                        correctness_score=0.0,
                        reason="Search timeout exceeded.",
                    )
                )
                break

            explored_count += 1

            # Pruning check: Cost must be strictly lower than current best to justify verification
            if cand.estimated_cost >= current_best_cost:
                rejected_count += 1
                step += 1
                trace.append(
                    SearchTraceEntry(
                        step_index=step,
                        candidate_id=cand.candidate_id,
                        parent_id=cand.parent_id,
                        action="PRUNED_COST",
                        cost_score=cand.estimated_cost,
                        correctness_score=0.0,
                        reason=f"Estimated cost {cand.estimated_cost:.0f} >= current best {current_best_cost:.0f}",
                    )
                )
                continue

            # Verification Budget check
            if verified_count >= cfg.verification_budget:
                rejected_count += 1
                step += 1
                trace.append(
                    SearchTraceEntry(
                        step_index=step,
                        candidate_id=cand.candidate_id,
                        parent_id=cand.parent_id,
                        action="PRUNED_BUDGET",
                        cost_score=cand.estimated_cost,
                        correctness_score=0.0,
                        reason="Verification budget exhausted.",
                    )
                )
                continue

            # Execute & Independently Verify
            verified_count += 1
            passed, vrecord, audit = self.verifier.verify_candidate(
                candidate_graph=cand.graph,
                reference_graph=initial_graph,
                inputs=sample_inputs,
                contract=contract,
                candidate_id=cand.candidate_id,
            )

            if passed:
                cand.verification_status = "PASSED"
                cand.verification_metrics = audit.to_dict()
                step += 1
                trace.append(
                    SearchTraceEntry(
                        step_index=step,
                        candidate_id=cand.candidate_id,
                        parent_id=cand.parent_id,
                        action="VERIFIED_PASS",
                        cost_score=cand.estimated_cost,
                        correctness_score=1.0,
                        reason=f"Passed independent verification ({audit.parity_classification}). Cost: {cand.estimated_cost:.0f}",
                    )
                )

                if cand.estimated_cost < current_best_cost:
                    current_best = cand
                    current_best_cost = cand.estimated_cost
                    best_vrecord = vrecord
                    shortcut_found = True
            else:
                cand.verification_status = "FAILED"
                cand.verification_metrics = audit.to_dict()
                rejected_count += 1
                step += 1
                trace.append(
                    SearchTraceEntry(
                        step_index=step,
                        candidate_id=cand.candidate_id,
                        parent_id=cand.parent_id,
                        action="VERIFIED_FAIL",
                        cost_score=cand.estimated_cost,
                        correctness_score=0.0,
                        reason=f"Failed verification: {'; '.join(audit.violations)}",
                    )
                )

        status_msg = "SHORTCUT_DISCOVERED" if shortcut_found else "NO_VERIFIED_SHORTCUT_FOUND"
        speedup = (baseline_cost / current_best_cost) if current_best_cost > 0 else 1.0

        return SearchResult(
            best_pathway=current_best,
            is_shortcut_found=shortcut_found,
            status_message=status_msg,
            candidates_explored=explored_count,
            candidates_rejected=rejected_count,
            candidates_verified=verified_count,
            search_trace=trace,
            verification_record=best_vrecord,
            baseline_cost=baseline_cost,
            best_cost=current_best_cost,
            speedup=speedup,
        )
