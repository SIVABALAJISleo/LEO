"""
tests/test_breakthrough_dashboard_api.py
=============================================================================
Tests the Breakthrough Dashboard API endpoints and verifies live execution
of all 15 Counterexample Breakthrough Solutions.
=============================================================================
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_breakthrough_overview_endpoint():
    """Verifies the core breakthrough engine overview, philosophy, and parity levels."""
    res = client.get("/api/v1/breakthrough/overview")
    assert res.status_code == 200
    data = res.json()
    
    assert "philosophy" in data
    assert "Leaf-to-Petrol" in data["philosophy"]["name"]
    
    assert "pipeline_stages" in data
    assert len(data["pipeline_stages"]) == 8
    
    assert "parity_levels" in data
    assert len(data["parity_levels"]) == 4
    
    assert "host_hardware" in data
    assert "Intel Core i5-12450H" in data["host_hardware"]["cpu"]


def test_list_all_15_counterexamples():
    """Verifies that all 15 counterexamples are registered with full metadata."""
    res = client.get("/api/v1/breakthrough/counterexamples")
    assert res.status_code == 200
    data = res.json()
    
    assert "counterexamples" in data
    ces = data["counterexamples"]
    assert len(ces) == 15
    
    ids = [c["id"] for c in ces]
    assert ids == list(range(1, 16))
    
    # Check domain categorizations
    domains = set(c["domain"] for c in ces)
    assert domains == {"DENSE_COMPUTE", "AI_ML", "GRAPHICS_RAYTRACING", "MEDIA_SCIENTIFIC"}


@pytest.mark.parametrize("cid", list(range(1, 16)))
def test_run_counterexample_live(cid: int):
    """Executes live benchmark measurement for each counterexample from 1 to 15."""
    res = client.post("/api/v1/breakthrough/run-counterexample", json={"counterexample_id": cid})
    assert res.status_code == 200
    data = res.json()
    
    assert data["counterexample_id"] == cid
    assert data["contract_status"] == "PASS"
    assert "metrics" in data
    assert data["metrics"]["measured_hyper_latency_ms"] >= 0.0
    assert data["metrics"]["reference_baseline_latency_ms"] >= 0.0
    assert "details" in data
