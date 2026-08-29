"""
hyper_ares/engine.py
=============================================================================
HYPER-ARES: Adaptive Representation & Elimination Search Master Engine
=============================================================================
Orchestrates the 20-step adaptive discovery and elimination loop.
"""

import time
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass

from hyper_ares.structure_detector import StructureDetector, StructuralProfile
from hyper_ares.representation_searcher import RepresentationSearcher, CandidateRepresentation
from hyper_ares.predictive_residual import PredictiveResidualEngine
from hyper_x.heterogeneous_orchestrator import HeterogeneousOrchestrator
from hyper_x.independent_verifier import IndependentVerifier, VerificationResult

@dataclass
class AresExecutionResult:
    output: np.ndarray
    winning_representation: str
    structural_profile: StructuralProfile
    work_elimination_ratio: float
    total_latency_ms: float
    verification: VerificationResult
    candidate_benchmarks: List[Dict[str, Any]]

class HyperAresEngine:
    """Master engine executing Adaptive Representation & Elimination Search."""

    def __init__(self):
        self.detector = StructureDetector()
        self.searcher = RepresentationSearcher()
        self.residual_engine = PredictiveResidualEngine(rank=32)
        self.orchestrator = HeterogeneousOrchestrator(pool_size_mb=64)
        self.verifier = IndependentVerifier()

    def execute_matrix_multiplication(
        self,
        A: np.ndarray,
        B: np.ndarray,
        contract: Optional[Dict[str, Any]] = None
    ) -> AresExecutionResult:
        """Executes full 20-step ARES discovery loop on matrix multiplication."""
        t_start = time.perf_counter()
        contract = contract or {"epsilon": 0.01, "max_latency_ms": 150.0}
        eps = contract.get("epsilon", 0.01)
        slo_ms = contract.get("max_latency_ms", 150.0)

        # Step 1-9: Invariant Structure Detection
        profile = self.detector.analyze_matrix(A)

        # Step 10-14: Candidate Representation Synthesis
        candidates = self.searcher.search_matrix_representations(A, B, profile, tolerance_epsilon=eps)

        # Step 15-18: Multi-Candidate Benchmark & Independent Verification
        benchmarks = []
        winning_candidate = None
        best_latency = float("inf")
        best_output = None
        best_ver = None

        # Precompute reference probe for verification
        N = B.shape[1]
        x_probe = np.random.randn(N, 1).astype(np.float32)
        rhs_probe = A @ (B @ x_probe)
        rhs_norm = float(np.linalg.norm(rhs_probe) + 1e-8)

        for cand in candidates:
            out, meta = cand.execute_fn()
            cand_lat = meta["latency_ms"]
            
            # Fast verification probe
            lhs_probe = out @ x_probe
            err = float(np.linalg.norm(lhs_probe - rhs_probe) / rhs_norm)
            is_valid = (err <= eps) and (cand_lat <= slo_ms)

            bench_record = {
                "name": cand.name,
                "category": cand.category,
                "latency_ms": round(cand_lat, 2),
                "error": round(err, 6),
                "cer": meta.get("cer", 0.0),
                "is_valid": is_valid
            }
            benchmarks.append(bench_record)

            if is_valid and cand_lat < best_latency:
                best_latency = cand_lat
                best_output = out
                winning_candidate = cand.name

        # If no reduced representation passed, fallback to exact Dense AVX2
        if best_output is None:
            best_output = A @ B
            winning_candidate = "DENSE_AVX2"
            best_latency = (time.perf_counter() - t_start) * 1000.0

        t_end = time.perf_counter()
        total_lat_ms = (t_end - t_start) * 1000.0

        # Step 19-20: Independent Verification against contract
        Y_ref_sample = A @ B
        cer_val = max([b["cer"] for b in benchmarks if b["name"] == winning_candidate], default=0.0)
        ver_result = self.verifier.verify_matrix_workload(
            Y_ref=Y_ref_sample,
            Y_hyper=best_output,
            T_ref_ms=benchmarks[0]["latency_ms"] if benchmarks else 10.0,
            T_hyper_ms=best_latency,
            tolerance_epsilon=eps,
            latency_slo_ms=slo_ms,
            nominal_reference_flops=2.0 * A.shape[0] * A.shape[1] * B.shape[1],
            actual_hyper_flops=(2.0 * A.shape[0] * A.shape[1] * B.shape[1]) * (1.0 - cer_val),
            exactness_class="PREDICTIVE_RESIDUAL" if "RESIDUAL" in winning_candidate else "REDUCED_WORK"
        )

        return AresExecutionResult(
            output=best_output,
            winning_representation=winning_candidate,
            structural_profile=profile,
            work_elimination_ratio=ver_result.work_elimination_ratio,
            total_latency_ms=round(best_latency, 3),
            verification=ver_result,
            candidate_benchmarks=benchmarks
        )
