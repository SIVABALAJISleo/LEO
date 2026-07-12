"""
Standalone integration test runner for V42 — no pytest overhead.
Runs every test case from test_v42_integration.py and prints PASS/FAIL.
"""
import sys
import traceback
sys.path.insert(0, '.')

print("=" * 60)
print("LEO AI V42 — Integration Test Suite")
print("=" * 60)

failures = []

# ── Test 1: Orchestrator direct ──────────────────────────────
try:
    from backend.layers.v42_ultimate_orchestrator import V42UltimateOrchestrator
    orchestrator = V42UltimateOrchestrator()
    res = orchestrator.execute_semantic_workflow(
        "How does LEO AI optimize CPU+iGPU performance?", {}
    )
    assert res["compute_avoided"] is True, f"compute_avoided={res['compute_avoided']}"
    assert "answer" in res, "No 'answer' key"
    assert res["latency_ms"] > 0, f"latency={res['latency_ms']}"
    assert len(res["layer_trace"]) >= 5, f"trace_len={len(res['layer_trace'])}"
    print("[PASS] test_v42_orchestrator_direct")
except Exception as e:
    print(f"[FAIL] test_v42_orchestrator_direct: {e}")
    traceback.print_exc()
    failures.append("test_v42_orchestrator_direct")

# ── Test 2: Multilingual Dravidian ───────────────────────────
try:
    orchestrator2 = V42UltimateOrchestrator()

    # Telugu: హలో ఎలా ఉన్నారు
    te_res = orchestrator2.execute_semantic_workflow("హలో ఎలా ఉన్నారు", {})
    assert te_res["compute_avoided"] is True, f"te compute_avoided={te_res['compute_avoided']}"
    assert "Telugu" in te_res["answer"], f"Telugu not in answer: {te_res['answer']!r}"
    print("[PASS] test_v42_multilingual_dravidian (Telugu)")

    # Kannada: ಹಲೋ ನೀವು ಹೇಗಿದ್ದೀರಿ
    kn_res = orchestrator2.execute_semantic_workflow("ಹಲೋ ನೀವು ಹೇಗಿದ್ದೀರಿ", {})
    assert kn_res["compute_avoided"] is True, f"kn compute_avoided={kn_res['compute_avoided']}"
    assert "Kannada" in kn_res["answer"], f"Kannada not in answer: {kn_res['answer']!r}"
    print("[PASS] test_v42_multilingual_dravidian (Kannada)")

    # Malayalam: ഹലോ സുഖമാണോ
    ml_res = orchestrator2.execute_semantic_workflow("ഹലോ സുഖമാണോ", {})
    assert ml_res["compute_avoided"] is True, f"ml compute_avoided={ml_res['compute_avoided']}"
    assert "Malayalam" in ml_res["answer"], f"Malayalam not in answer: {ml_res['answer']!r}"
    print("[PASS] test_v42_multilingual_dravidian (Malayalam)")

except Exception as e:
    print(f"[FAIL] test_v42_multilingual_dravidian: {e}")
    traceback.print_exc()
    failures.append("test_v42_multilingual_dravidian")

# ── Test 3: API Endpoints ─────────────────────────────────────
try:
    from fastapi.testclient import TestClient
    from backend.main import app
    client = TestClient(app)

    payload = {
        "query": "హలో ఎలా ఉన్నారు",
        "workspace_id": "test_workspace_v42",
        "quality_hint": "balanced"
    }
    headers = {"Authorization": "Bearer token-admin"}
    response = client.post("/api/v1/leo/v42/orchestrate", json=payload, headers=headers)
    assert response.status_code == 200, f"status={response.status_code}, body={response.text[:200]}"
    data = response.json()
    assert "answer" in data, f"No 'answer' in: {data}"
    assert data["compute_avoided"] is True, f"compute_avoided={data['compute_avoided']}"
    assert "Telugu" in data["answer"], f"Telugu not in answer: {data['answer']!r}"
    assert data["entropy_tier"] == "v42_ultimate", f"entropy_tier={data['entropy_tier']}"

    status_response = client.get("/api/v1/leo/status?version=v42")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["layers"] == 12, f"layers={status_data['layers']}"
    assert status_data["system"] == "LEO AI V42 Ultimate Evolution Substrate", f"system={status_data['system']}"
    print("[PASS] test_v42_api_endpoints")

except Exception as e:
    print(f"[FAIL] test_v42_api_endpoints: {e}")
    traceback.print_exc()
    failures.append("test_v42_api_endpoints")

# ── Summary ───────────────────────────────────────────────────
print()
print("=" * 60)
if failures:
    print(f"RESULT: {len(failures)} FAILURE(S): {failures}")
    sys.exit(1)
else:
    print("RESULT: ALL TESTS PASSED [OK]")
    sys.exit(0)
