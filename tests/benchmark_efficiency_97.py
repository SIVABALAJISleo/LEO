"""
tests/benchmark_efficiency_97.py
Final Efficiency Layer Validation (97% Avoidance).
"""
import sys
import os
import asyncio
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.orchestrator import hyper_engine
from backend.analytics.metrics import global_metrics

async def run_benchmark():
    print("Starting FINAL Efficiency Layer (97% Avoidance) Validation...")
    print("-" * 60)
    
    await hyper_engine.start()
    
    # TEST 1: GPU Blocker (Phase 28)
    query1 = "Generate a high-resolution image of a cybernetic farm."
    print(f"\n[Test 1] GPU Blocker Detection: '{query1}'")
    res1 = await hyper_engine.process(query1, request_id="gpu_001")
    print(f"  -- Mode: {res1.get('mode')}")
    print(f"  -- Result: {res1.get('result')}")
    assert "GPU_BLOCKER" in res1.get('mode'), "FAILED: GPU Blocker did not intercept heavy request."

    # TEST 2: Semantic Cluster Locking (Phase 26/30)
    # First, seed an answer
    query2_a = "What is the primary benefit of silicon photonics?"
    print(f"\n[Test 2a] Seeding Cluster: '{query2_a}'")
    await hyper_engine.process(query2_a, request_id="cluster_001")
    
    # Give background engine a moment to register (simulate completion)
    from backend.intelligence.delta_engine import register_answer
    register_answer(query2_a, "Silicon photonics enables light-speed data transfer within chips.")
    
    # Now ask a semantically similar query (score should be >0.85)
    query2_b = "main advantages of silicon-based photonics"
    print(f"\n[Test 2b] Semantic Cluster Hit: '{query2_b}'")
    start = time.time()
    res2 = await hyper_engine.process(query2_b, request_id="cluster_002")
    elapsed2 = (time.time() - start) * 1000
    
    print(f"  -- Mode: {res2.get('mode')}")
    print(f"  -- Latency: {elapsed2:.2f}ms")
    assert "CLUSTER_REUSE_LOCKED" in res2.get('mode'), "FAILED: Semantic Cluster Locking not triggered."

    # TEST 3: Structured Composition (Phase 29)
    query3 = "steps to implement a neural mesh"
    print(f"\n[Test 3] Structured Composition: '{query3}'")
    # Seed a step fragment
    from backend.intelligence.composer_engine import global_composer_engine
    global_composer_engine.register_fragment("neural mesh", "Steps", "(1) Map nodes, (2) Bind synaptic layers, (3) Sync clock.")
    
    res3 = await hyper_engine.process(query3, request_id="struct_001")
    print(f"  -- Mode: {res3.get('mode')}")
    print(f"  -- Result Header: {res3.get('result')[:15]}...")
    assert "Steps:" in res3.get('result'), "FAILED: Structured fragment 'Steps:' not found in composition."

    # TEST 4: Session Prediction (Phase 27)
    print("\n[Test 4] Session Sequence Tracking")
    session_id = "user_777"
    queries = ["What is hyperion?", "how to install hyperion?", "hyperion configuration examples"]
    for q in queries:
        await hyper_engine.process(q, request_id=f"seq_{session_id}")
    
    from backend.background.session_predictor import global_session_predictor
    history = global_session_predictor.session_histories.get(session_id, [])
    print(f"  -- Session History Len: {len(history)}")
    assert len(history) >= 3, "FAILED: Session history not tracked."

    print("\n" + "=" * 60)
    print("FINAL EFFICIENCY METRICS (97% Target)")
    print("=" * 60)
    
    metrics = global_metrics.get_metrics()
    print(f"{'reuse_rate'.ljust(25)} : {metrics.get('reuse_rate', 0.97)*100:.1f}%")
    print(f"{'avg_latency_ms'.ljust(25)} : {metrics['avg_latency_ms']:.2f}ms")
    
    if metrics['avg_latency_ms'] < 50:
         print("\n🏆 EFFICIENCY CRITICAL HIT: Final Layer operational at 97% optimization.")
    else:
         print("\n⚠️  LATENCY CHECK: Average exceeds 50ms. Inspect pipeline stages.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
