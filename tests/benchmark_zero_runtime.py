"""
tests/benchmark_zero_runtime.py
Validation script for Zero Runtime Compute AI Platform.
"""
import sys
import os
import asyncio
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.orchestrator import hyper_engine
from backend.analytics.metrics import global_metrics

async def run_benchmark():
    print("Starting Zero Runtime Compute Validation Benchmark...")
    print("-" * 50)
    
    # 1. Start the background compute worker
    await hyper_engine.start()
    
    query = "Explain the concept of 'Temporal Sharding' in distributed databases."
    
    # TEST 1: First-time Query (Unknown)
    print(f"\n[Test 1] First-time Query: {query}")
    start = time.time()
    res1 = await hyper_engine.process(query, request_id="zero_001", tenant_id="tenant_zero")
    elapsed1 = (time.time() - start) * 1000
    
    print(f"  -- Mode: {res1.get('mode')}")
    print(f"  -- Latency: {elapsed1:.1f}ms")
    print(f"  -- Result: {res1.get('result')}")
    
    if res1.get('mode') != "ENQUEUED_FOR_BG":
        print("❌ FAILED: Query should have been enqueued for background processing.")
    else:
        print("✅ SUCCESS: Query enqueued correctly (Hard Blocker worked).")

    # 2. Wait for background processing (Decomposition + Prediction + Resolution)
    print("\nWaiting for background compute engine to resolve tasks...")
    await asyncio.sleep(8) 
    
    # TEST 2: Second-time Query (Should be cached/composed)
    print(f"\n[Test 2] Second-time Query: {query}")
    start = time.time()
    res2 = await hyper_engine.process(query, request_id="zero_002", tenant_id="tenant_zero")
    elapsed2 = (time.time() - start) * 1000
    
    print(f"  -- Mode: {res2.get('mode')}")
    print(f"  -- Latency: {elapsed2:.1f}ms")
    
    if "CACHE" in res2.get('mode') or "RUNTIME_COMPOSITION" in res2.get('mode') or "SHADOW" in res2.get('mode'):
        print("✅ SUCCESS: Instant response from precomputed store.")
    else:
        print(f"❌ FAILED: Expected precomputed hit, got {res2.get('mode')}")

    # TEST 3: Predicted Variation (Should be pre-resolved by predictor)
    # The predictor likely generated "What are the benefits of temporal sharding?" or similar
    # We can try a semantic variation
    variation = "What are the advantages of temporal sharding in databases?"
    print(f"\n[Test 3] Predicted Variation Query: {variation}")
    start = time.time()
    res3 = await hyper_engine.process(variation, request_id="zero_003", tenant_id="tenant_zero")
    elapsed3 = (time.time() - start) * 1000
    
    print(f"  -- Mode: {res3.get('mode')}")
    print(f"  -- Latency: {elapsed3:.1f}ms")
    
    if "CACHE" in res3.get('mode') or "RUNTIME_COMPOSITION" in res3.get('mode') or "DELTA" in res3.get('mode'):
        print("✅ SUCCESS: Predictive precomputation worked!")
    else:
        print(f"⚠️  NOTE: Predictive hit missed (this can happen if variation didn't match exactly), Mode={res3.get('mode')}")

    print("\n" + "=" * 50)
    print("FINAL ZERO-COMPUTE METRICS")
    print("=" * 50)
    
    metrics = global_metrics.get_metrics()
    print(f"{'runtime_compute_calls'.ljust(35)} : {metrics['runtime_compute_calls']}")
    print(f"{'background_tasks'.ljust(35)} : {metrics['background_tasks']}")
    print(f"{'avoidance_rate'.ljust(35)} : {metrics['avoidance_rate']*100:.1f}%")

    if metrics['runtime_compute_calls'] == 0:
        print("\n🏆 TARGET ACHIEVED: Zero Runtime Compute Platform Verified.")
    else:
        print("\n❌ FAILED: Runtime compute calls detected.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
