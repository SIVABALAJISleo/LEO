"""
scripts/bench_crystallizer.py
Benchmark hit-rates and p50 match latency for the Layer 4 Semantic Crystallizer Cache.
"""

import os
import sys
import time
import numpy as np

sys.path.append(os.getcwd())

from backend.crystallization.crystallizer import SemanticCrystallizer


def run_cryst_bench():
    print("=" * 60)
    print("  LEO AI Layer 4 Semantic Crystallizer Benchmark")
    print("=" * 60)

    db_path = "bench_cryst_temp.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    crystallizer = SemanticCrystallizer(db_path=db_path)

    # 1. Populate/Warming Cache with baseline domain questions
    knowledge_base = [
        ("What is the battery life of LEO hardware?", "LEO hardware lasts up to 18 hours under typical workloads."),
        ("How do I partition the swarm layers?", "Mesh nodes divide model layers sequentially based on resource scoring."),
        ("Is BitNet multiplication-free?", "Yes, BitNet uses ternary weights (-1, 0, 1) and bypasses matrix multiplication."),
        ("Explain prompt-lookup decoding.", "Prompt-lookup copies n-grams directly from the context block to save draft steps."),
        ("What is the cost of H100 cloud instances?", "H100 instances cost approximately $2.50 to $4.70 per hour."),
    ]

    for idx, (q, a) in enumerate(knowledge_base):
        crystallizer.record_trace(
            trace_id=f"kb_trace_{idx}",
            query=q,
            response=a,
            w_class="benchmark"
        )

    # 2. Benchmark Queries
    test_queries = [
        # Exact hits
        ("What is the battery life of LEO hardware?", True),
        ("Is BitNet multiplication-free?", True),
        # Paraphrased hits (Fuzzy semantic matching)
        ("Can LEO hardware run for 18 hours on battery?", True),
        ("Does BitNet require float multiplication?", True),
        ("Explain how prompt-lookup decoding works.", True),
        ("What are the costs for H100 cloud VMs?", True),
        # Unrelated misses
        ("What is the weather like today?", False),
        ("Who won the last soccer world cup?", False),
        ("How to boil an egg?", False),
    ]

    print(f"Running {len(test_queries)} queries against the Crystallizer Cache...")

    hit_count = 0
    miss_count = 0
    hit_latencies = []

    for query, expected_hit in test_queries:
        t0 = time.perf_counter()
        match = crystallizer.match_shortcut(query)
        latency = (time.perf_counter() - t0) * 1000  # in ms

        if match:
            hit_count += 1
            hit_latencies.append(latency)
            print(f"[HIT]  '{query}' -> '{match['shortcut_id']}' (Sim: {match['similarity']:.3f}, Latency: {latency:.2f}ms)")
        else:
            miss_count += 1
            print(f"[MISS] '{query}' (Latency: {latency:.2f}ms)")

    # 3. Calculate Stats
    total = len(test_queries)
    measured_hit_rate = (hit_count / total) * 100 if total > 0 else 0.0
    p50_latency = np.median(hit_latencies) if hit_latencies else 0.0

    print("-" * 60)
    print("BENCHMARK SUMMARY:")
    print(f"Total Queries Evaluated: {total}")
    print(f"Measured Hit Rate:       {measured_hit_rate:.2f}%")
    print(f"p50 Hit Match Latency:   {p50_latency:.3f} ms")
    print("=" * 60)

    if os.path.exists(db_path):
        os.remove(db_path)


if __name__ == "__main__":
    run_cryst_bench()
