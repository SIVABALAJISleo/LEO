import asyncio
import time
import uuid
import json
import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from backend.core.orchestrator import hyper_engine
from backend.core.stability_layer import global_stability_layer
from backend.analytics.metrics import global_metrics

async def run_benchmark():
    # Clear logs for a clean run
    if os.path.exists("metrics.jsonl"):
        os.remove("metrics.jsonl")
        
    print("Starting MISSION CRITICAL Benchmark (150 Queries)...")
    print("-" * 50)
    
    # 1. NEW QUERIES (50)
    print("Phase 1: 50 New Queries (Model + Predictive BG Enqueue)...")
    results_new = []
    for i in range(50):
        q = f"Detail the implementation of intelligence module {i} in HYPER."
        start = time.time()
        res = await global_stability_layer.secure_invoke(q, f"BENCH_NEW_{i}", "default", "default")
        latency = (time.time() - start) * 1000
        results_new.append(latency)
        if i % 10 == 0:
            print(f"[{i}/50] New Query Latency: {latency:.2f}ms Path: {res['mode']}")

    # 2. IDENTICAL QUERIES (50)
    print("\nPhase 2: 50 Identical Queries (Exact Cache - Target < 10ms)...")
    q_id = "What is the mission of Project HYPER?"
    results_identical = []
    # Warm up cache
    await global_stability_layer.secure_invoke(q_id, "WARMUP", "default", "default")
    
    for i in range(50):
        start = time.time()
        res = await global_stability_layer.secure_invoke(q_id, f"BENCH_ID_{i}", "default", "default")
        latency = (time.time() - start) * 1000
        results_identical.append(latency)
        if i % 10 == 0:
            print(f"[{i}/50] Identical Latency: {latency:.2f}ms Path: {res['mode']}")

    # 3. PARAPHRASED QUERIES (50)
    print("\nPhase 3: 50 Paraphrased Queries (Semantic Cache - Target < 50ms)...")
    variations = [
        "Explain the HYPER project goals",
        "What is the objective of HYPER?",
        "Tell me about the HYPER mission",
        "What does the HYPER platform do?",
        "Project HYPER core purpose"
    ] * 10 # 50 variations
    
    results_para = []
    for i, q in enumerate(variations):
        start = time.time()
        res = await global_stability_layer.secure_invoke(q, f"BENCH_PARA_{i}", "default", "default")
        latency = (time.time() - start) * 1000
        results_para.append(latency)
        if i % 10 == 0:
            print(f"[{i}/50] Paraphased Latency: {latency:.2f}ms Path: {res['mode']}")

    # FINAL REPORT
    print("\n" + "="*70)
    print("FINAL BENCHMARK RESULTS (98% DOMINANCE MISSION)")
    print("="*70)
    
    def stats(l):
        return sum(l)/len(l), min(l), max(l)

    avg_new, min_new, max_new = stats(results_new)
    avg_id, min_id, max_id = stats(results_identical)
    avg_para, min_para, max_para = stats(results_para)

    metrics = global_metrics.get_metrics()
    
    print(f"{'Category':<20} | {'Avg Latency':<12} | {'Min':<8} | {'Max':<8}")
    print("-" * 70)
    print(f"{'New Queries (50)':<20} | {avg_new:>10.2f}ms | {min_new:>6.2f}ms | {max_new:>6.2f}ms")
    print(f"{'Identical (50)':<20} | {avg_id:>10.2f}ms | {min_id:>6.2f}ms | {max_id:>6.2f}ms")
    print(f"{'Paraphrased (50)':<20} | {avg_para:>10.2f}ms | {min_para:>6.2f}ms | {max_para:>6.2f}ms")
    print("-" * 70)
    print(f"Total Requests:      {metrics['total_requests']}")
    print(f"Avoidance Rate:      {metrics['avoidance_rate'] * 100:.2f}%")
    print(f"Reuse Rate:          {metrics['reuse_rate'] * 100:.2f}%")
    print(f"Prediction Hit Rate: {metrics['prediction_hit_rate'] * 100:.2f}%")
    print(f"Failure Recovery:    {metrics['failure_recovery_rate'] * 100:.2f}%")
    print(f"Model Calls:         {metrics['model_calls']}")
    print("="*70)

    # Save summary
    with open("benchmark_summary.json", "w") as f:
        json.dump({
            "new": {"avg": avg_new, "min": min_new, "max": max_new},
            "identical": {"avg": avg_id, "min": min_id, "max": max_id},
            "paraphrased": {"avg": avg_para, "min": min_para, "max": max_para},
            "overall": metrics
        }, f, indent=4)

if __name__ == "__main__":
    asyncio.run(run_benchmark())
