"""
tests/benchmark_complete_zero.py
Final Validation for ZERO-RUNTIME-COMPUTE CONTROL LAYER.
"""
import sys
import os
import asyncio
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.orchestrator import hyper_engine
from backend.analytics.metrics import global_metrics

async def run_benchmark():
    print("Starting FINAL Zero-Runtime-Compute Validation...")
    print("-" * 60)
    
    await hyper_engine.start()
    
    # TEST 1: Absolute Blocker (Brand New Query)
    query1 = "What are the specific benefits of holographic storage for AI workloads?"
    print(f"\n[Test 1] Mandatory Blocker: '{query1}'")
    start = time.time()
    res1 = await hyper_engine.process(query1, request_id="comp_001")
    elapsed1 = (time.time() - start) * 1000
    
    print(f"  -- Mode: {res1.get('mode')}")
    print(f"  -- result: {res1.get('result')[:50]}...")
    print(f"  -- Latency: {elapsed1:.2f}ms")
    
    assert res1.get('mode') == "ENQUEUED_MANDATORY", "FAILED: Should have blocked and enqueued."
    assert elapsed1 < 300, f"FAILED: Cold-start latency too high ({elapsed1:.2f}ms)" # Allowing 300ms for first-ever hit (Redis timeouts + Model load)

    # TEST 2: Background Resolve & Expansion
    print("\n[Test 2] Waiting for Background Resolve & 20-Query Expansion...")
    # Give it time to generate and resolve
    await asyncio.sleep(8)
    
    # TEST 3: Predictive Cache Hit (Variation)
    # The predictor should have generated something related to "holographic storage benefits"
    query2 = "holographic storage AI workload benefits" # A semantic variant
    print(f"\n[Test 3] Predictive Hit: '{query2}'")
    start = time.time()
    res2 = await hyper_engine.process(query2, request_id="comp_002")
    elapsed2 = (time.time() - start) * 1000
    
    print(f"  -- Mode: {res2.get('mode')}")
    print(f"  -- Latency: {elapsed2:.2f}ms")
    
    # We expect SHADOW_STORE or CACHE_EXACT/DELTA if synchronized correctly
    assert res2.get('compute_cost_avoided') is True, "FAILED: Computation happened at runtime."
    
    # TEST 4: Massive Micro-Batching
    print("\n[Test 4] Parallel Micro-Batching (10 simultaneous identical hits)")
    start = time.time()
    tasks = [hyper_engine.process("explain holographic sharding", request_id=f"batch_{i}") for i in range(10)]
    results4 = await asyncio.gather(*tasks)
    elapsed4 = (time.time() - start) * 1000
    
    print(f"  -- Batch Latency (10 queries): {elapsed4:.2f}ms")
    assert all(r.get('mode') == "ENQUEUED_MANDATORY" for r in results4), "FAILED: All should be batched to enqueue."

    print("\n" + "=" * 60)
    print("FINAL ZERO-RUNTIME CONTROL LAYER METRICS")
    print("=" * 60)
    
    metrics = global_metrics.get_metrics()
    print(f"{'avoidance_rate'.ljust(35)} : {metrics['avoidance_rate']*100:.1f}%")
    print(f"{'avg_latency_ms'.ljust(35)} : {metrics['avg_latency_ms']:.2f}ms")
    
    if metrics['avoidance_rate'] >= 0.99 and metrics['avg_latency_ms'] < 50:
         print("\n🏆 HYPERSCALER STATUS ACHIEVED: Zero-Runtime-Compute Control Layer passing all checks.")
    else:
         print("\n⚠️  MARGINAL: Check latency/hit rates. Some overhead detected.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
