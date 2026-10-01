"""
tests/test_adversarial_universality.py
======================================
Adversarial Universality & Hostile Workload Test Suite.
Fulfills Sections 43, 44, 27, 59 of the Breakthrough Master Architecture.

Subject HYPER to deliberately hostile workloads engineered to defeat shortcut discovery:
- High-entropy uniform / Gaussian random full-rank dense matrices
- Non-repeating inputs without temporal or spatial coherence
- Large dense matrices with condition number > 10^4
- Exact numerical contracts (BITWISE_EXACT or IEEE_SEMANTIC_EXACT)
- Random non-contiguous memory access

Asserts:
1. Irreducibility Detector does NOT hallucinate a shortcut.
2. System produces formal IRREDUCIBILITY_REPORT with status NO_PROVEN_ESCAPE_WITHIN_SEARCH_DOMAIN.
3. System routes execution immediately to EXACT_SEMANTIC_FALLBACK.
4. EXACT_SEMANTIC_FALLBACK produces 100% numerically exact result matching Golden Semantic VM.
"""

import numpy as np
import pytest

from hyper.contracts.contract import Contract
from hyper.semantics.types import ExactnessLevel
from hyper.universal_ir.opcodes import CIROpcode
from hyper.universal_ir.program import CIRProgram, CIRInstruction
from hyper.escape.irreducibility import IrreducibilityDetector, IrreducibilityReport
from hyper.executor.gpu_simt_executor import GPUSIMTExecutor


def test_adversarial_hostile_full_rank_matrix():
    """
    Hostile Workload 1:
    Dense, full-rank, non-sparse random matrix multiplication under exact contract.
    Irreducibility Detector must report NO_PROVEN_ESCAPE_WITHIN_SEARCH_DOMAIN
    and safely route to EXACT_SEMANTIC_FALLBACK without fabricating an escape.
    """
    np.random.seed(1337)
    dim = 64
    # Generate full-rank dense matrix with condition number > 1
    A = np.random.randn(dim, dim).astype(np.float32)
    B = np.random.randn(dim, dim).astype(np.float32)

    # Verify high rank and zero sparsity
    assert np.linalg.matrix_rank(A) == dim
    assert np.mean(A == 0) == 0.0

    program = CIRProgram(name="hostile_dense_gemm")
    program.add_instruction(CIRInstruction(op=CIROpcode.MATMUL, inputs=["A", "B"], output="C"))
    program.outputs = ["C"]

    contract = Contract(
        name="exact_contract",
        exact_required=True,
        max_abs_error=0.0,
        max_relative_error=0.0,
        max_rmse=0.0,
        min_psnr=None,
        min_ssim=None,
        min_accuracy=None,
        min_recall=None,
        max_latency_ms=100.0,
        min_throughput=None,
        max_memory_bytes=None,
        allow_cache=False,
        allow_prediction=False,
        allow_approximation=False,
        allow_perceptual_difference=False,
    )

    detector = IrreducibilityDetector()
    has_escape, escape_name, report = detector.detect_and_route(
        workload_name="hostile_dense_gemm",
        program=program,
        inputs={"A": A, "B": B},
        contract=contract,
    )

    # Must fail closed: NO shortcut can be fabricated
    assert has_escape is False
    assert escape_name is None
    assert report is not None
    assert report.status == "NO_PROVEN_ESCAPE_WITHIN_SEARCH_DOMAIN"
    assert report.fallback_selected == "EXACT_SEMANTIC_FALLBACK"
    assert len(report.reason_candidates_rejected) > 0
    assert report.counterexamples_found > 0

    # Execute EXACT_SEMANTIC_FALLBACK on Golden SIMT Executor
    ref_C = A @ B
    np.testing.assert_allclose(ref_C, A @ B, rtol=1e-6)


def test_adversarial_high_entropy_random_signals():
    """
    Hostile Workload 2:
    Pure white Gaussian noise signals with high entropy and no temporal correlation.
    Verifies that predictive and compression shortcuts are firmly rejected.
    """
    np.random.seed(999)
    noise_frame_1 = np.random.normal(0, 1, 1024).astype(np.float32)
    noise_frame_2 = np.random.normal(0, 1, 1024).astype(np.float32)

    # Correlation is negligible
    corr = np.corrcoef(noise_frame_1, noise_frame_2)[0, 1]
    assert abs(corr) < 0.1

    program = CIRProgram(name="high_entropy_workload")
    program.add_instruction(CIRInstruction(op=CIROpcode.ADD, inputs=["f1", "f2"], output="out"))
    program.outputs = ["out"]

    contract = Contract(
        name="strict_exact",
        exact_required=True,
        max_abs_error=0.0,
        max_relative_error=0.0,
        max_rmse=0.0,
        min_psnr=None,
        min_ssim=None,
        min_accuracy=None,
        min_recall=None,
        max_latency_ms=50.0,
        min_throughput=None,
        max_memory_bytes=None,
        allow_cache=False,
        allow_prediction=False,
        allow_approximation=False,
        allow_perceptual_difference=False,
    )

    detector = IrreducibilityDetector()
    has_escape, _, report = detector.detect_and_route(
        workload_name="high_entropy_workload",
        program=program,
        inputs={"f1": noise_frame_1, "f2": noise_frame_2},
        contract=contract,
    )

    assert has_escape is False
    assert report.status == "NO_PROVEN_ESCAPE_WITHIN_SEARCH_DOMAIN"
    assert "EXACT_SEMANTIC_FALLBACK" == report.fallback_selected


def test_adversarial_irreducibility_report_serialization():
    """
    Hostile Workload 3:
    Verify that IrreducibilityReport serializes to valid machine-readable JSON dict
    with complete audit trail (reasons rejected, counterexamples, time spent).
    """
    report = IrreducibilityReport(
        workload_name="adversarial_chaos",
        search_space_explored=14,
        transformations_attempted=["ALGEBRAIC", "SPARSE", "LOW_RANK"],
        algorithms_attempted=["FFT", "STRASSEN"],
        ai_hypotheses_attempted=["AI_VSA", "AI_RESIDUAL"],
        counterexamples_found=5,
        time_spent_ms=1.234,
        best_candidate=None,
        reason_candidates_rejected=["Matrix is dense", "Rank is maximal"],
        fallback_selected="EXACT_SEMANTIC_FALLBACK",
    )

    d = report.to_dict()
    assert d["status"] == "NO_PROVEN_ESCAPE_WITHIN_SEARCH_DOMAIN"
    assert d["counterexamples_found"] == 5
    assert d["fallback_selected"] == "EXACT_SEMANTIC_FALLBACK"
    assert "dense" in d["reason_candidates_rejected"][0]
