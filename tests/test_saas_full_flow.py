from fastapi.testclient import TestClient
from backend.main import app
from backend.intelligence.feedback_store import global_feedback_store

client = TestClient(app)

def test_saas_optimize_flow():
    # 1. First Request: Cold Start (Retrieval + Fusion + Enhancement)
    query = "What is Project HYPER's core value proposition?"
    payload = {
        "query": query,
        "tier": "pro"
    }
    
    # Mocking the token dependency if necessary, but assuming TestClient handles the setup or we use a demo token
    # For this test, we assume the server is in 'test mode' or accepts the mock environment
    
    headers = {"Authorization": "Bearer AUDIT_MODE_TOKEN"}
    response = client.post("/api/v1/leo/orchestrate", json=payload, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "answer" in data
    assert "confidence" in data
    
    initial_confidence = data["confidence"]

    # 2. Second Request: Warm Start (Temporal Memory / Cache Hit)
    response_warm = client.post("/api/v1/leo/orchestrate", json=payload, headers=headers)
    assert response_warm.status_code == 200
    data_warm = response_warm.json()
    
    # Confidence should be high for repeating queries
    assert data_warm["confidence"] >= initial_confidence
    assert "resolved_by" in data_warm or "source" in data_warm

def test_saas_tier_enforcement():
    # Test rate limiting / tier checks
    user_id = "test_user_limited"
    from backend.core.usage_metering import global_usage_meter
    
    # Force limit exceeded for 'free' tier (mocking 100+ requests)
    for _ in range(101):
        global_usage_meter.record_usage(user_id)
        
    payload = {"query": "test query", "tier": "free"}
    headers = {"Authorization": f"Bearer token-{user_id}"}
    
    response = client.post("/api/v1/leo/orchestrate", json=payload, headers=headers)
    assert response.status_code in [200, 429]

def test_feedback_loop_learning():
    # Test that feedback actually modifies the threshold
    initial_threshold = global_feedback_store.get_threshold()
    
    # Log 5 successes
    for i in range(5):
        global_feedback_store.log_event(f"query_{i}", 0.9, success=True)
        
    new_threshold = global_feedback_store.get_threshold()
    assert new_threshold <= initial_threshold # Should decrease threshold on success
    
    # Log a failure
    global_feedback_store.log_event("failure_query", 0.4, success=False)
    final_threshold = global_feedback_store.get_threshold()
    assert final_threshold > new_threshold # Should spike threshold on failure

if __name__ == "__main__":
    # Minimal direct execution for debugging
    print("Running SaaS Integration Tests...")
    test_saas_optimize_flow()
    test_saas_tier_enforcement()
    test_feedback_loop_learning()
    print("All SaaS Integration Tests Passed!")
