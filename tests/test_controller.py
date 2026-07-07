from backend.intelligence.controller import AdaptiveController
from backend.intelligence.policy_store import PolicyStore

def test_decision_engine_routing():
    controller = AdaptiveController()
    controller.policy_store = PolicyStore()
    
    # 1. Perfect feature match should SKIP_MODEL
    high_features = {
        "quality": 1.0,
        "confidence": 0.9,
        "cache_hit": 1
    }
    assert controller.route(high_features) == "SKIP_MODEL"

    # 2. Borderline should ENHANCE
    mid_features = {
        "quality": 0.6,
        "confidence": 0.6,
        "cache_hit": 0
    }
    assert controller.route(mid_features) == "ESCALATE"

    # 3. Garbage should ESCALATE
    low_features = {
        "quality": 0.1,
        "confidence": 0.2,
        "cache_hit": 0
    }
    assert controller.route(low_features) == "ESCALATE"

def test_learning_engine_feedback():
    controller = AdaptiveController()
    controller.policy_store = PolicyStore()
    initial_policy = controller.policy_store.get()
    
    # 1. Simulate a successful bypass (should lower skip threshold slightly)
    controller.process_feedback("query", "answer", success=True, fallback_triggered=False)
    new_policy = controller.policy_store.get()
    assert new_policy["skip_threshold"] < initial_policy["skip_threshold"]
    
    # 2. Simulate a failed bypass (should heavily increase skip threshold)
    failed_policy_start = new_policy["skip_threshold"]
    controller.process_feedback("query", "failure", success=False, fallback_triggered=True)
    post_fail_policy = controller.policy_store.get()
    
    assert post_fail_policy["skip_threshold"] > failed_policy_start
