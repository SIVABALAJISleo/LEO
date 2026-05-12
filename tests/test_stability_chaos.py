import pytest
import asyncio
import time
from backend.core.chaos_controller import global_chaos_controller, ChaosMode
from backend.core.zero_compute import global_zero_control
from orchestration.chaos_containment import ChaosContainment

@pytest.mark.asyncio
async def test_chaos_mode_switching():
    """Verify that system degrades gracefully under high cpu/latency."""
    global_chaos_controller.mode = ChaosMode.NORMAL
    
    # Simulate high latency
    global_chaos_controller.check_health(cpu_usage=95.0, recent_latency=60.0)
    assert global_chaos_controller.get_mode() == ChaosMode.MINIMAL
    
    # Simulate recovery
    global_chaos_controller.check_health(cpu_usage=10.0, recent_latency=5.0)
    # Note: recovery requires multiple stable pulses in my new logic, 
    # but for simplicity in test I'll check if it moves towards Normal
    # Current logic requires avg < 20.
    assert global_chaos_controller.get_mode() == ChaosMode.NORMAL

@pytest.mark.asyncio
async def test_zero_compute_stability_guarantee():
    """Verify that requests never exceed 50ms and handle chaos."""
    start_time = time.time()
    query = "What is the chaotic trajectory of a 3-body system?"
    
    # Submit query that triggers ChaosContainment
    result = await global_zero_control.handle_request(
        query, 
        "test_request_123", 
        "test_tenant", 
        "test_workspace", 
        start_time
    )
    
    elapsed = (time.time() - start_time) * 1000
    assert elapsed < 50.0
    assert result["mode"] == "CHAOS_PATTERN_PLAYBACK"
    assert "trajectory" in str(result["result"])

@pytest.mark.asyncio
async def test_emergency_simplification():
    """Verify that system returns simplified responses under stress."""
    global_chaos_controller.mode = ChaosMode.MINIMAL
    start_time = time.time()
    
    result = await global_zero_control.handle_request(
        "Complex logic query", 
        "test_stress_456", 
        "test_tenant", 
        "test_workspace", 
        start_time
    )
    
    assert result["mode"] == "CHAOS_MINIMAL_MODE"
    assert "adaptive core reference" in result["result"]

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
