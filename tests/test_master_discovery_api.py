"""
tests/test_master_discovery_api.py
==================================
Tests for FastAPI endpoints exposing the Master Architecture discovery engines:
- Workload extraction & contract formalization
- Necessary-work analysis & DAG reduction
- Theorem formal proof (0-1 sorting lemma & polynomial Horner)
- Computational barrier analysis
- Universality Gate audit & 16-state transitions
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_api_extract_canonical_workload():
    """Test POST /api/v1/discovery/workloads/extract."""
    payload = {
        "name": "QuickSort_Int32",
        "domain": "SORTING",
        "force_exact": True,
    }
    resp = client.post("/api/v1/discovery/workloads/extract", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "QuickSort_Int32"
    assert data["contract"]["exactness_type"] == "EXACT"
    assert data["contract"]["absolute_tolerance"] == 0.0


def test_api_analyze_necessary_work():
    """Test POST /api/v1/discovery/necessary-work/analyze."""
    payload = {
        "workload_id": "wl-gemm-pipeline",
        "operations": [
            {"op_id": "op_0", "name": "copy_tensor", "op_type": "CAST", "flops": 10.0},
            {"op_id": "op_1", "name": "matmul_core", "op_type": "GEMM", "flops": 1000.0},
            {"op_id": "op_2", "name": "relu_activation", "op_type": "FUSED_RELU", "flops": 50.0},
            {"op_id": "op_3", "name": "static_ambient_light", "op_type": "CONSTANT", "flops": 100.0},
        ],
        "contract_exactness": "NUMERICALLY_TOLERANT",
    }
    resp = client.post("/api/v1/discovery/necessary-work/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_flops"] == 1160.0
    assert data["necessary_flops"] == 1000.0
    assert data["potential_work_reduction_pct"] > 0.0
    assert data["nodes"]["op_0"]["necessity"] == "REDUNDANT"
    assert data["nodes"]["op_1"]["necessity"] == "NECESSARY"


def test_api_prove_sorting_network_01():
    """Test POST /api/v1/discovery/theorems/prove-01."""
    # Test valid 4-sorter: [(0, 1), (2, 3), (0, 2), (1, 3), (1, 2)]
    payload = {
        "n": 4,
        "network": [[0, 1], [2, 3], [0, 2], [1, 3], [1, 2]],
    }
    resp = client.post("/api/v1/discovery/theorems/prove-01", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "PROVEN"
    assert data["verified_by_formal_checker"] is True
    assert len(data["counterexamples"]) == 0


def test_api_prove_polynomial_horner():
    """Test POST /api/v1/discovery/theorems/prove-horner."""
    payload = {"degree": 4}
    resp = client.post("/api/v1/discovery/theorems/prove-horner", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "PROVEN"
    assert data["verified_by_formal_checker"] is True


def test_api_analyze_barriers():
    """Test POST /api/v1/discovery/barriers/analyze."""
    # Memory bandwidth barrier
    payload_mem = {
        "barrier_type": "MEMORY_BANDWIDTH",
        "workload_name": "AttentionCacheLarge",
        "data_movement_bytes": 100 * 1024 * 1024,
        "target_ms": 0.05,
        "allows_bypass": True,
    }
    resp = client.post("/api/v1/discovery/barriers/analyze", json=payload_mem)
    assert resp.status_code == 200
    data = resp.json()
    assert data["classification"] == "BARRIER_BYPASSABLE_VIA_TRANSFORMATION"
    assert data["theoretical_floor_ms"] > 5.0

    # Sorting Shannon barrier
    payload_sort = {
        "barrier_type": "SORTING_SHANNON",
        "n": 5,
        "target_comparisons": 3,  # Impossible under Shannon lower bound 7
    }
    resp_sort = client.post("/api/v1/discovery/barriers/analyze", json=payload_sort)
    assert resp_sort.status_code == 200
    data_sort = resp_sort.json()
    assert data_sort["classification"] == "PROVABLY_IMPOSSIBLE_UNDER_MODEL"
    assert data_sort["is_provably_impossible"] is True


def test_api_audit_universality_gate():
    """Test POST /api/v1/discovery/universality-gate/audit."""
    # Incomplete checklist -> NOT_PROVEN
    payload_incomplete = {
        "workload_id": "wl-gemm-alpha",
        "pathway_name": "BitNetTernaryAdditiveBypass",
        "current_state": "PROVEN",
        "checklist": {
            "domain_formally_defined": True,
            "contract_formally_defined": True,
            "correctness_established": True,
            # remaining 9 items false
        },
    }
    resp = client.post("/api/v1/discovery/universality-gate/audit", json=payload_incomplete)
    assert resp.status_code == 200
    data = resp.json()
    assert data["verdict"] == "NOT_PROVEN"
    assert data["final_state"] == "PROVEN"

    # Complete checklist -> GUARANTEED
    payload_complete = {
        "workload_id": "wl-gemm-alpha",
        "pathway_name": "BitNetTernaryAdditiveBypass",
        "current_state": "PROVEN",
        "checklist": {
            "domain_formally_defined": True,
            "contract_formally_defined": True,
            "correctness_established": True,
            "independent_verification_passed": True,
            "counterexample_search_conducted": True,
            "generalization_demonstrated": True,
            "reproducibility_guaranteed": True,
            "performance_evidence_measured": True,
            "resource_evidence_verified": True,
            "no_hidden_computation_verified": True,
            "no_unfair_caching_verified": True,
            "proof_or_formal_evidence_passed": True,
        },
    }
    resp_g = client.post("/api/v1/discovery/universality-gate/audit", json=payload_complete)
    assert resp_g.status_code == 200
    data_g = resp_g.json()
    assert data_g["verdict"] == "GUARANTEED"
    assert data_g["final_state"] == "GUARANTEED"
    assert data_g["passed_percentage"] == 100.0
