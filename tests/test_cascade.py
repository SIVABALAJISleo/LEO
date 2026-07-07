"""
tests/test_cascade.py
Unit tests for Layer 5 Cascade Router complexity classification and model escalation.
"""

import pytest
from backend.inference.cascade_router import ModelCascadeRouter


def test_complexity_classification():
    router = ModelCascadeRouter()
    
    # 1. Simple empty query
    assert router.classify_complexity("") == 0.0
    
    # 2. Basic chat query
    score_low = router.classify_complexity("hello")
    assert score_low < 0.3
    
    # 3. Technical reasoning queries (contain complex keywords)
    score_high = router.classify_complexity("Explain how to design and optimize a parallel neural gradient matrix calculation")
    assert score_high >= 0.7


def test_routing_tiers():
    router = ModelCascadeRouter()
    
    # Verify tier thresholds mapping
    assert router.route_tier(0.15)[0] == "Tier-1 (0.5B)"
    assert router.route_tier(0.50)[0] == "Tier-2 (3B)"
    assert router.route_tier(0.80)[0] == "Tier-3 (8B)"
    assert router.route_tier(0.95)[0] == "Tier-4 (Cloud)"


@pytest.mark.asyncio
async def test_execute_cascade_flow():
    router = ModelCascadeRouter(db_path="test_cascade_temp.db")
    
    # 1. Simple query (should resolve directly to Tier-1)
    res_low = await router.execute_cascade("hi there")
    assert res_low["status"] == "success"
    assert "Tier-1" in res_low["resolved_tier"]
    assert res_low["escalated"] is False

    # 2. Complex query (triggers low confidence and escalates)
    res_high = await router.execute_cascade("design optimize trade-off details of distributed matrices")
    assert res_high["status"] == "success"
    # Should be escalated since confidence was low
    assert res_high["escalated"] is True
    assert "Tier-3" in res_high["resolved_tier"] or "Tier-4" in res_high["resolved_tier"]

    # Cleanup temp db
    import os
    if os.path.exists("test_cascade_temp.db"):
        os.remove("test_cascade_temp.db")
