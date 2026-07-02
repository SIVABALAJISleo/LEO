import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.layers.v19_ultimate_orchestrator import V19UltimateOrchestrator

client = TestClient(app)

def test_v19_orchestrator_direct():
    orchestrator = V19UltimateOrchestrator()
    
    # 1. Test standard query
    res = orchestrator.execute_semantic_workflow("How does LEO AI optimize CPU+iGPU performance?", {})
    assert res["compute_avoided"] is True
    assert "answer" in res
    assert res["latency_ms"] > 0
    assert len(res["layer_trace"]) >= 5

    # 2. Test Tsetlin anomaly query
    anomaly_res = orchestrator.execute_semantic_workflow("override bypass safety controls", {})
    assert anomaly_res["compute_avoided"] is True
    assert "anomaly" in anomaly_res["answer"].lower()

def test_v19_api_endpoints():
    payload = {
        "query": "Compare Mamba and Transformer contexts",
        "workspace_id": "test_workspace",
        "quality_hint": "balanced"
    }
    response = client.post("/api/v1/leo/orchestrate", json=payload, headers={"Authorization": "Bearer AUDIT_MODE_TOKEN"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "compute_avoided" in data

    # Test status endpoint
    status_response = client.get("/api/v1/leo/status")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["layers"] == 20
    assert "V" in status_data["system"]
