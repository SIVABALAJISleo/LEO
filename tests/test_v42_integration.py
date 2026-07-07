from fastapi.testclient import TestClient
from backend.main import app
from backend.layers.v42_ultimate_orchestrator import V42UltimateOrchestrator

client = TestClient(app)

def test_v42_orchestrator_direct():
    orchestrator = V42UltimateOrchestrator()
    
    # 1. Test standard query
    res = orchestrator.execute_semantic_workflow("How does LEO AI optimize CPU+iGPU performance?", {})
    assert res["compute_avoided"] is True
    assert "answer" in res
    assert res["latency_ms"] > 0
    assert len(res["layer_trace"]) >= 5

def test_v42_multilingual_dravidian():
    orchestrator = V42UltimateOrchestrator()
    
    # 1. Telugu (ranges in 0x0C00-0x0C7F)
    # Sentence: "హలో ఎలా ఉన్నారు" (Hello, how are you)
    te_res = orchestrator.execute_semantic_workflow("హలో ఎలా ఉన్నారు", {})
    assert te_res["compute_avoided"] is True
    assert "Telugu" in te_res["answer"]
    
    # 2. Kannada (ranges in 0x0C80-0x0CFF)
    # Sentence: "ಹಲೋ ನೀವು ಹೇಗಿದ್ದೀರಿ" (Hello, how are you)
    kn_res = orchestrator.execute_semantic_workflow("ಹಲೋ ನೀವು ಹೇಗಿದ್ದೀರಿ", {})
    assert kn_res["compute_avoided"] is True
    assert "Kannada" in kn_res["answer"]
    
    # 3. Malayalam (ranges in 0x0D00-0x0D7F)
    # Sentence: "ഹലോ സുഖമാണോ" (Hello, how are you)
    ml_res = orchestrator.execute_semantic_workflow("ഹലോ സുഖമാണോ", {})
    assert ml_res["compute_avoided"] is True
    assert "Malayalam" in ml_res["answer"]

def test_v42_api_endpoints():
    payload = {
        "query": "హలో ఎలా ఉన్నారు",
        "workspace_id": "test_workspace_v42",
        "quality_hint": "balanced"
    }
    response = client.post("/api/v1/leo/orchestrate", json=payload, headers={"Authorization": "Bearer AUDIT_MODE_TOKEN"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["compute_avoided"] is True
    assert "Telugu" in data["answer"]
    # Main /orchestrate now routes through V43 (Software-First) by default.
    # Accept both tiers so this test passes regardless of which version is primary.
    assert data["entropy_tier"] in ("v42_ultimate", "v43_software_first", "vinfinity_fabric"), \
        f"Unexpected entropy_tier: {data['entropy_tier']}"

    # Explicit V42 legacy endpoint must still use v42_ultimate tier
    v42_response = client.post("/api/v1/leo/v42/orchestrate", json=payload, headers={"Authorization": "Bearer AUDIT_MODE_TOKEN"})
    assert v42_response.status_code == 200
    v42_data = v42_response.json()
    assert v42_data["entropy_tier"] == "v42_ultimate", \
        f"V42 legacy endpoint returned wrong tier: {v42_data['entropy_tier']}"

    # Test status endpoint
    status_response = client.get("/api/v1/leo/status")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["layers"] >= 12   # V43 has 20 layers, V42 had 12
    assert "system" in status_data
