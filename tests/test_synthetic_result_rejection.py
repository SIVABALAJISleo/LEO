"""
tests/test_synthetic_result_rejection.py
========================================
Tests Phase 16 & 18 rejection of synthetic results and unverified claims.
Ensures verified=True cannot be reported without genuine verification.
"""

import pytest
from hyper.candidate import CandidateResult, PathClass
from hyper.contracts.contract import Contract
from hyper.parity import compute_contract_parity


def test_reject_unverified_candidate_claiming_parity():
    contract = Contract(
        name="StrictContract",
        exact_required=True,
        max_abs_error=0.0,
        max_relative_error=0.0,
        max_rmse=0.0,
        min_psnr=None,
        min_ssim=None,
        min_accuracy=None,
        min_recall=None,
        max_latency_ms=10.0,
        min_throughput=None,
        max_memory_bytes=None,
        allow_cache=False,
        allow_prediction=False,
        allow_approximation=False,
        allow_perceptual_difference=False,
    )

    # Candidate with unverified error and synthetic assertion
    unverified_candidate = CandidateResult(
        value=None,
        path_class=PathClass.PREDICTIVE.value,  # not exact
        backend="CPU_AVX2",
        latency_ms=5.0,
        work_units=100,
        memory_bytes=1024,
        max_abs_error=0.05,  # violates exact_required
        relative_error=0.05,
        rmse=0.02,
        verification_status="UNVERIFIED",
    )

    parity = compute_contract_parity(contract, unverified_candidate)
    assert parity["passed"] is False
    assert parity["parity_pct"] == 0.0
    assert len(parity["reasons_failed"]) > 0
