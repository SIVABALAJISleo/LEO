"""
tests/test_hyper_mvc_dar_api.py
Integration tests for HYPER MVC-DAR FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_api_hyper_hardware(client):
    res = client.get("/hyper/hardware")
    assert res.status_code == 200
    data = res.json()
    assert "target_model" in data
    assert "logical_threads" in data
    assert "measured_memory_bandwidth_gb_s" in data


def test_api_hyper_audit(client):
    res = client.get("/hyper/audit")
    assert res.status_code == 200
    data = res.json()
    assert data["audit_file_present"] is True
    assert data["all_tests_passing"] is True


def test_api_hyper_ledger(client):
    res = client.get("/hyper/ledger")
    assert res.status_code == 200
    data = res.json()
    assert "total_workloads_recorded" in data


def test_api_hyper_analyze(client):
    res = client.post("/hyper/analyze", json={"workload_id": "w01_dense_gemm"})
    assert res.status_code == 200
    data = res.json()
    assert data["workload_id"] == "w01_dense_gemm"
    assert data["contract_satisfied"] is True


def test_api_hyper_optimize(client):
    res = client.post("/hyper/optimize", json={"workload_id": "w03_sparse_fft", "track": "TRACK_B_CONTRACT"})
    assert res.status_code == 200
    data = res.json()
    assert data["speedup_factor"] > 1.0


def test_api_hyper_verify(client):
    res = client.post("/hyper/verify", json={"workload_id": "w01_dense_gemm"})
    assert res.status_code == 200
    data = res.json()
    assert data["verification_status"] == "PASS"


def test_api_hyper_discover(client):
    res = client.post("/hyper/discover", json={"workload_id": "w01_dense_gemm", "generations": 2})
    assert res.status_code == 200
    data = res.json()
    assert data["generations_completed"] == 2
    assert "evolution_history" in data


def test_api_hyper_research(client):
    res = client.post("/hyper/research", json={"workload_id": "w12_n_body"})
    assert res.status_code == 200
    data = res.json()
    assert "measured_speedup" in data
    assert data["verification"] == "PASS"
