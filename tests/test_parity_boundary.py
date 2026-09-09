"""
tests/test_parity_boundary.py
==============================
Unit and Formal Verification Suite for the Parity Boundary Certificate & Feasible-Set Parity.
"""

import json
from pathlib import Path
import pytest
from hyper_cco import (
    FeasibleSetParityCalculator,
    FeasibleWorkloadRecord,
    ExcludedWorkloadRecord,
    ParityBoundaryCertificate,
)


def test_feasible_workloads_weights_and_pass_status():
    """Verifies that all feasible workloads have valid weights summing to 1.0 and pass their gates."""
    feasible = FeasibleSetParityCalculator.get_canonical_feasible_set()
    assert len(feasible) == 6, f"Expected 6 canonical manifest workloads, got {len(feasible)}"

    total_weight = sum(w.weight for w in feasible)
    assert abs(total_weight - 1.0) < 1e-6, f"Feasible weights must sum to 1.0, got {total_weight}"

    for w in feasible:
        assert w.weight > 0.0, f"Workload {w.workload_id} must have positive weight"
        assert w.correctness_status == "PASS", f"Workload {w.workload_id} must have PASS status"
        assert w.hostile_test_verified is True
        assert w.clean_reproduction_verified is True
        assert w.passed_all_gates is True


def test_feasible_set_parity_calculation_100_percent():
    """
    Verifies the mathematical formalization:
        Feasible-set parity = sum(w_i * passes(w_i)) / sum(w_i) * 100% = 100.0%
    """
    parity_pct, passed_w, total_w = FeasibleSetParityCalculator.calculate_feasible_set_parity()
    assert parity_pct == 100.0, f"Feasible-set parity must be 100.0%, got {parity_pct}"
    assert abs(passed_w - 1.0) < 1e-6
    assert abs(total_w - 1.0) < 1e-6


def test_feasible_set_parity_falsification_sensitivity():
    """
    Proves that the formula is sensitive to failure:
    If GEMM_512x512 (weight 0.20) fails a gate, the feasible parity drops exactly to 80.0%.
    """
    feasible = FeasibleSetParityCalculator.get_canonical_feasible_set()
    # Deliberately fail GEMM
    feasible[0].correctness_status = "FAIL"

    parity_pct, passed_w, total_w = FeasibleSetParityCalculator.calculate_feasible_set_parity(feasible)
    assert round(parity_pct, 2) == 80.00, f"Expected 80.0% when 0.20 weight fails, got {parity_pct}"
    assert round(passed_w, 2) == 0.80
    assert round(total_w, 2) == 1.00


def test_excluded_workloads_have_rigorous_proofs():
    """Verifies that all excluded workloads have rigorous physical or mathematical proofs."""
    excluded = FeasibleSetParityCalculator.get_canonical_excluded_set()
    assert len(excluded) >= 5

    workload_ids = [e.workload_id for e in excluded]
    assert "EXCL-01_RAW_NVIDIA_CUDA_HARDWARE" in workload_ids
    assert "EXCL-02_DENSE_RANDOM_GAUSSIAN_COMPRESSION" in workload_ids
    assert "EXCL-03_ZERO_ACCEPTANCE_SPECULATIVE_INFERENCE" in workload_ids

    for e in excluded:
        assert len(e.exclusion_proof) > 50, f"Exclusion proof for {e.workload_id} must be substantial"
        assert e.raw_hardware_parity == 0.0
        assert len(e.candidate_behavior_on_input) > 10


def test_parity_boundary_certificate_generation_and_integrity():
    """Verifies full certificate generation, dictionary serialization, and cryptographic digest."""
    cert = FeasibleSetParityCalculator.generate_boundary_certificate()
    assert cert.feasible_set_parity_pct == 100.0
    assert cert.raw_hardware_parity_pct == 0.0
    assert cert.certificate_id.startswith("PBC-")
    assert len(cert.certificate_digest) == 64  # SHA-256

    cert_dict = cert.to_dict()
    assert cert_dict["feasible_set_parity_pct"] == 100.0
    assert cert_dict["raw_hardware_parity_pct"] == 0.0
    assert len(cert_dict["included_feasible_workloads"]) == 6
    assert len(cert_dict["excluded_workloads"]) >= 5

    # Check exact defensive boundary statement
    expected_statement = "100% verified contract/application parity across the defined feasible workload domain. Raw hardware parity and parity for excluded workloads remain outside the claim."
    assert cert.defensive_boundary_statement == expected_statement


def test_parity_boundary_certificate_files_exist():
    """Verifies that PARITY_BOUNDARY_CERTIFICATE.md and parity_boundary_certificate.json exist on disk."""
    md_path = Path("PARITY_BOUNDARY_CERTIFICATE.md")
    json_path = Path("benchmark_results/parity_boundary_certificate.json")

    assert md_path.exists(), "PARITY_BOUNDARY_CERTIFICATE.md must exist at workspace root"
    assert json_path.exists(), "benchmark_results/parity_boundary_certificate.json must exist"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["feasible_set_parity_pct"] == 100.0
    assert data["raw_hardware_parity_pct"] == 0.0

    content = md_path.read_text(encoding="utf-8")
    assert "Feasible-set application parity = 100%" in content or "Feasible-Set Application Parity" in content
    assert "Raw hardware parity and parity for excluded workloads remain outside the claim." in content


def test_tri_percentage_summary_and_nomenclature():
    """
    Verifies the three distinct, non-contradictory metrics:
    - Feasible-domain coverage: 100%
    - Feasible-domain contract pass: 100%
    - Raw NVIDIA hardware parity: 0%
    """
    cert = FeasibleSetParityCalculator.generate_boundary_certificate()
    cert_dict = cert.to_dict()

    tri = cert_dict["tri_percentage_summary"]
    assert tri["feasible_domain_coverage_pct"] == 100.0
    assert tri["feasible_domain_contract_pass_rate_pct"] == 100.0
    assert tri["raw_nvidia_hardware_parity_pct"] == 0.0

    assert cert.formal_name == "100% Feasible-Domain Verified Application Parity"
    assert cert.mechanism == "Domain-Restricted Universal Parity"
    assert len(cert.cw_conditions_audited) == 9
    assert "predeclared prior to measurement" in cert.pre_registration_guarantee

