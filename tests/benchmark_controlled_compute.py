"""
tests/benchmark_controlled_compute.py
Controlled Compute Layer Validation (Safe Sync).
"""
import sys
import os
import asyncio
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.orchestrator import hyper_engine
from backend.optimization.compute_budget import global_compute_budget

async def run_benchmark():
    print("Starting CONTROLLED COMPUTE (Safe Sync) Validation...")
    print("-" * 60)
    
    await hyper_engine.start()
    
    # 1. High-Priority Case: Should trigger Micro-Compute
    query1 = "What are the steps to deploy a neural mesh?"
    print(f"\n[Test 1] High-Priority Sync Compute: '{query1}'")
    start1 = time.time()
    res1 = await hyper_engine.process(query1, request_id="sync_001")
    elapsed1 = (time.time() - start1) * 1000
    
    print(f"  -- Mode: {res1.get('mode')}")
    print(f"  -- Latency: {elapsed1:.2f}ms")
    print(f"  -- Result: {res1.get('result')[:60]}...")
    assert "CONTROLLED_COMPUTE_SYNC" in res1.get('mode'), "FAILED: High-priority query did not trigger sync compute."

    # 2. Low-Priority Case: Should NOT trigger sync compute (Approx only)
    query2 = "Tell me a random story about space."
    print(f"\n[Test 2] Low-Priority Approximation: '{query2}'")
    res2 = await hyper_engine.process(query2, request_id="sync_002")
    print(f"  -- Mode: {res2.get('mode')}")
    assert "CONTROLLED_COMPUTE_SYNC" not in res2.get('mode'), "FAILED: Low-priority query triggered sync compute."

    # 3. Budget Exhaustion Case
    print("\n[Test 3] Budget Exhaustion Fallback")
    # Manually exhaust budget for next request
    global_compute_budget.start_tracking("sync_003_exhaust")
    for _ in range(51): 
        try:
            global_compute_budget.consume_unit("sync_003_exhaust")
        except TimeoutError:
            break
            
    # Now try a high-priority request with the same ID (simulating mid-request exhaustion)
    # Actually, we'll just check if it fails safely.
    from backend.optimization.micro_compute import global_micro_compute
    res3 = await global_micro_compute.execute("test", "steps", "test_topic")
    print(f"  -- Sync Result after exhaustion: {res3}")
    assert res3 is None, "FAILED: Sync compute did not stop after budget exhaustion."

    # 4. CPU Throttling (Phase 39)
    print("\n[Test 4] CPU Throttling Check")
    # Simulate high load
    from unittest.mock import patch
    with patch('psutil.cpu_percent', return_value=85.0):
        capacity = global_compute_budget.has_capacity()
        print(f"  -- Capacity at 85% CPU: {capacity}")
        assert capacity is False, "FAILED: Throttling did not engage at high CPU."

    print("\n" + "=" * 60)
    print("CONTROLLED COMPUTE SUCCESS: Safety limits verified.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_benchmark())
