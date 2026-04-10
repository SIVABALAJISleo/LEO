"""
Inference Reduction Benchmark
Tests the 10-layer inference avoidance pipeline at scale.
Measures: avoidance ratio, latency, layer hit distribution, cost savings.
"""
import asyncio
import time
import random
import argparse
from collections import Counter

QUERY_TEMPLATES = {
    "simple_definitions": [
        "What is RAG?", "What is LLM?", "What is AI?", "What is ML?",
        "What is API?", "What is KV?", "What is GPU?", "What is PPE?",
    ],
    "math": [
        "Calculate 123 * 456", "What is 999 + 1", "Compute 2048 / 4",
        "What is 7 * 8?", "Calculate 100 - 37",
    ],
    "medium": [
        "How to optimize LLM latency?",
        "What is RAG compared to fine-tuning?",
        "Explain speculative decoding advantages.",
        "How does semantic caching work?",
        "What is the difference between RAG and fine-tuning?",
    ],
    "complex": [
        "Analyze the architectural tradeoffs between RAG and finetuning for enterprise AI applications.",
        "Design a comprehensive multi-tenant AI inference optimization system with caching layers.",
        "Compare the advantages and disadvantages of different model compression techniques.",
        "Explain the step-by-step process for implementing a predictive precomputation engine.",
    ],
}

# Pre-warm distribution: 40% simple, 30% medium, 20% math, 10% complex
QUERY_WEIGHTS = [0.40, 0.30, 0.20, 0.10]
QUERY_POOLS = [
    QUERY_TEMPLATES["simple_definitions"],
    QUERY_TEMPLATES["medium"],
    QUERY_TEMPLATES["math"],
    QUERY_TEMPLATES["complex"],
]


def pick_query() -> str:
    pool = random.choices(QUERY_POOLS, weights=QUERY_WEIGHTS)[0]
    return random.choice(pool)


async def run_benchmark(num_queries: int = 1000):
    from backend.core.database import init_db
    init_db()

    from backend.core.orchestrator import hyper_engine
    await hyper_engine.start()

    tenant_id = "bench_nextgen"
    workspace_id = "ws_nextgen_v2"

    print(f"\nStarting Inference Reduction Benchmark: {num_queries} queries")
    print(f"{'Layer':<25} {'Count':>8} {'%':>6}")
    print("-" * 45)

    modes = []
    latencies = []
    start_bench = time.time()

    for i in range(num_queries):
        query = pick_query()
        req_id = f"bench_{i}_user{i % 50}"

        t0 = time.time()
        try:
            result = await hyper_engine.process(query, req_id, tenant_id=tenant_id, workspace_id=workspace_id)
            mode = result.get("mode", "UNKNOWN") if isinstance(result, dict) else "UNKNOWN"
        except Exception:
            mode = "ERROR"
        latency = (time.time() - t0) * 1000

        modes.append(mode)
        latencies.append(latency)

        # Progress
        if num_queries >= 1000 and i > 0 and i % (num_queries // 10) == 0:
            done = i / num_queries
            cur_avoid = 1.0 - modes.count("FULL_CALC") / len(modes)
            print(f"  Progress: {done:.0%} | Avoidance so far: {cur_avoid:.1%}")

    duration = time.time() - start_bench
    counts = Counter(modes)
    total = len(modes)
    full_calc = counts.get("FULL_CALC", 0) + counts.get("ERROR", 0)
    avoidance = 1.0 - full_calc / total
    avg_lat = sum(latencies) / total
    p95_lat = sorted(latencies)[int(0.95 * total)]

    print("\n" + "=" * 50)
    print("BENCHMARK RESULTS")
    print("=" * 50)
    print(f"Total Queries:        {total}")
    print(f"Duration:             {duration:.2f}s")
    print(f"Avg Latency:          {avg_lat:.1f}ms")
    print(f"P95 Latency:          {p95_lat:.1f}ms")
    print(f"Inference Avoidance:  {avoidance:.1%}")
    print("\nLayer Distribution:")

    for mode, count in sorted(counts.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        print(f"  {mode:<25} {count:>6}  ({pct:.1f}%)")

    # Cost estimate (proxy: $0.002 per avoided FULL_CALC)
    avoided = total - full_calc
    cost_saved = avoided * 0.002
    print(f"\nEstimated Cost Saved: ${cost_saved:.2f} (@ $0.002/inference)")
    print("=" * 50)

    return avoidance


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HYPER Inference Reduction Benchmark")
    parser.add_argument("--queries", type=int, default=1000, help="Number of queries (1000/5000/10000)")
    args = parser.parse_args()
    asyncio.run(run_benchmark(args.queries))
