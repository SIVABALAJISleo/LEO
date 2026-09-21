"""
hyper/escape_engine/workloads/matrix_multiplication.py
======================================================
VAEE Initial Research Workload: Matrix Multiplication.

Implements:
- Ground-truth reference implementation (standard verified BLAS FP32)
- Explicit ComputationalContract (exact or numerically tolerant)
- Alternative candidates (Strassen, Blocked Tiling, Sparse CSR, Low-Rank SVD)
- Full adaptive search, multi-strategy verification (including Freivalds), and Pareto frontier ranking
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Tuple

import numpy as np

from ..contracts.schema import ComputationalContract
from ..contracts.extractor import ContractExtractor
from ..contracts.information_boundary import InformationBoundaryAnalyzer
from ..pathways.schema import ComputationalPathway
from ..pathways.composition import PathwayComposer
from ..pathways.generator import PathwayGenerator
from ..pathways.registry import PathwayRegistry
from ..search.adaptive_search import AdaptiveSearchEngine
from ..search.search_budget import SearchBudget
from ..verification.verifier import MasterVerifier
from ..analysis.cost_model import CostAnalyzer
from ..ranking.pareto import ParetoFrontier, ParetoPoint
from ..barriers.barrier_detector import BarrierDetector
from ..reporting.result_schema import (
    BenchmarkResult,
    VerificationResultRecord,
    ExecutionResultRecord,
    SearchResultRecord,
)
from ..reporting.audit_log import ScientificAuditLogger
from ..reporting.experiment import ExperimentManager


class MatrixMultiplicationResearchWorkload:
    """Benchmark and adaptive pathway search harness for Matrix Multiplication."""

    def __init__(self, M: int = 128, K: int = 128, N: int = 128, seed: int = 42) -> None:
        self.M, self.K, self.N = M, K, N
        self.seed = seed
        self.rng = np.random.default_rng(seed)

        # Generate inputs
        self.A = self.rng.standard_normal((M, K)).astype(np.float32)
        self.B = self.rng.standard_normal((K, N)).astype(np.float32)

        # Ground-truth reference execution
        self.ref_C = self.A @ self.B

        # Contract extraction
        self.contract = ContractExtractor.extract_from_tensor_op(
            name="gemm_exact",
            input_sample=self.A,
            reference_fn=lambda a: a @ self.B,
            tolerance=1e-4,
            relative_tolerance=1e-3,
            correctness="NUMERICAL",
            verification_method="FREIVALDS",
        )

        # Information boundary profiling
        self.profile = InformationBoundaryAnalyzer.analyze(self.contract, self.A)

        # Subsystems
        self.registry = PathwayRegistry()
        self.generator = PathwayGenerator(seed=seed)
        self.search_engine = AdaptiveSearchEngine(registry=self.registry, generator=self.generator)
        self.verifier = MasterVerifier()
        self.audit_logger = ScientificAuditLogger()
        self.frontier = ParetoFrontier()

    def run_experiment(self, max_candidates: int = 10) -> Dict[str, Any]:
        experiment_id = f"EXP-GEMM-{int(time.time()*1000)%1000000:06d}"
        manifest = ExperimentManager.create_manifest(experiment_id, self.A, seed=self.seed)

        # Measure baseline
        _, base_cost = CostAnalyzer.measure_execution(lambda: self.A @ self.B, trials=5)
        baseline_ms = base_cost.wall_clock_ms

        def evaluate_candidate(pathway: ComputationalPathway) -> Tuple[bool, str, float, float]:
            # Bind executable function
            run_fn = PathwayComposer.compose_matrix_multiplication(pathway, self.B)
            pathway.run_fn = run_fn

            # Execute & measure
            out, cost = CostAnalyzer.measure_execution(lambda: run_fn(self.A), trials=3)

            # Independent verification
            v_res = self.verifier.verify_candidate(
                candidate_output=out,
                reference_output=self.ref_C,
                contract=self.contract,
                extra_inputs=(self.A, self.B),
            )

            # Update Pareto frontier if verified
            if v_res.is_valid:
                speedup = baseline_ms / max(1e-6, cost.wall_clock_ms)
                point = ParetoPoint(
                    pathway=pathway,
                    latency_ms=cost.wall_clock_ms,
                    memory_mb=cost.peak_memory_mb,
                    energy_mj=cost.energy_estimate_mj,
                    confidence=v_res.confidence_score,
                    speedup_vs_baseline=speedup,
                )
                self.frontier.update(point)

            # Audit log entry
            self.audit_logger.log_decision(
                experiment_id=experiment_id,
                workload_name="matrix_multiplication",
                baseline_latency_ms=baseline_ms,
                candidate_pathway_id=pathway.pathway_id,
                transformations=pathway.transformation_chain,
                verification_method=v_res.method,
                verification_status=v_res.trust_level,
                candidate_latency_ms=cost.wall_clock_ms,
                verified_speedup=baseline_ms / max(1e-6, cost.wall_clock_ms),
                classification="SUCCESS" if v_res.is_valid else "FAILURE",
            )

            return v_res.is_valid, v_res.trust_level, cost.wall_clock_ms, cost.peak_memory_mb

        # Execute adaptive search
        budget = SearchBudget(max_candidates=max_candidates, max_time_seconds=20.0)
        search_state = self.search_engine.search(
            contract=self.contract,
            profile=self.profile,
            evaluate_fn=evaluate_candidate,
            budget=budget,
        )

        # Detect barriers
        barrier_verdict = BarrierDetector.detect_barriers(self.contract, self.profile)

        # Compile results
        best_speedup = (baseline_ms / max(1e-6, search_state.best_latency_ms)) if search_state.best_latency_ms < float("inf") else 1.0

        return {
            "experiment_id": experiment_id,
            "manifest": manifest.to_dict(),
            "workload": f"GEMM_{self.M}x{self.K}x{self.N}",
            "contract": self.contract.to_dict(),
            "baseline_latency_ms": baseline_ms,
            "best_latency_ms": search_state.best_latency_ms if search_state.best_latency_ms < float("inf") else baseline_ms,
            "verified_speedup": round(best_speedup, 2),
            "search_statistics": {
                "total_evaluated": search_state.total_evaluated,
                "total_verified": search_state.total_verified,
                "total_failed": search_state.total_failed,
                "diversity": self.registry.get_diversity_stats(),
                "saturation_detected": search_state.saturation_detected,
                "saturation_reason": search_state.saturation_reason,
            },
            "outcome": search_state.outcome,
            "barrier_verdict": barrier_verdict.to_dict(),
            "pareto_frontier": self.frontier.to_list(),
        }


if __name__ == "__main__":
    workload = MatrixMultiplicationResearchWorkload(M=128, K=128, N=128)
    res = workload.run_experiment(max_candidates=6)
    import json
    print(json.dumps(res, indent=2))
