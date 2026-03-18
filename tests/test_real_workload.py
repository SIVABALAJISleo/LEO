"""
Real Workload Benchmark
Simulates 1000 and 5000 queries across realistic patterns.
Measures: inference avoidance %, latency, cost, all hit rates.
"""
import asyncio
import time
import random
import argparse
from collections import Counter

# Realistic query distribution (pattern-heavy)
PATTERN_QUERIES = [
    "What is RAG?", "What is LLM?", "What is AI?", "What is ML?",
    "What is GPU?", "What is API?", "What is cache?", "What is Redis?",
    "What is Docker?", "What is Kubernetes?", "What is transformer?",
    "Define RAG", "Define LLM", "Define AI", "Explain RAG", "Explain LLM",
    "What is vector database?", "What is embedding?", "What is attention?",
    "What is fine-tuning?", "What is quantization?", "What is inference?",
    "How does RAG work?", "How does LLM work?", "How to use FastAPI?",
    "What is the difference between RAG and fine-tuning?",
]

MEDIUM_QUERIES = [
    "How to optimize LLM inference latency?",
    "Explain semantic caching in AI systems.",
    "What are benefits of using Redis for AI?",
    "How does speculative decoding reduce latency?",
    "What is the role of embeddings in RAG?",
]

COMPLEX_QUERIES = [
    "Design a comprehensive multi-tenant AI inference optimization system.",
    "Compare architectural tradeoffs between RAG and fine-tuning for enterprise applications.",
    "Analyze the advantages and disadvantages of model quantization for production deployment.",
]

def pick_query(mode: str) -> str:
    if mode == "pattern":
        return random.choice(PATTERN_QUERIES)
    elif mode == "medium":
        return random.choice(MEDIUM_QUERIES)
    else:
        pools = [PATTERN_QUERIES] * 60 + [MEDIUM_QUERIES] * 30 + [COMPLEX_QUERIES] * 10
        return random.choice(random.choice(pools))


async def run_benchmark(num_queries: int = 1000, mode: str = "mixed"):
    from backend.core.database import init_db
    init_db()

    from backend.core.orchestrator import hyper_engine
    await hyper_engine.start()

    # Seed canonical store on startup
    from backend.answers.canonical_store import global_canonical_store
    from backend.predictive.precompute_expander import global_precompute_expander
    seed_result = global_precompute_expander.expand(global_canonical_store, limit=500)
    print(f"Seeded: {seed_result['canonical_answers_seeded']} canonical answers")

    tenant_id = "bench_realworld"
    workspace_id = "ws_bench_v3"
    modes: list = []
    latencies: list = []
    start_bench = time.time()

    print(f"\nBenchmark: {num_queries} queries | mode={mode}")
    print("-" * 50)

    for i in range(num_queries):
        query = pick_query(mode)
        req_id = f"rw_{i}_u{i % 100}"

        t0 = time.time()
        try:
            result = await hyper_engine.process(query, req_id, tenant_id=tenant_id, workspace_id=workspace_id)
            hit_mode = result.get("mode", "UNKNOWN") if isinstance(result, dict) else "UNKNOWN"
        except Exception:
            hit_mode = "ERROR"
        lat = (time.time() - t0) * 1000

        modes.append(hit_mode)
        latencies.append(lat)

        if i > 0 and i % (max(num_queries // 5, 1)) == 0:
            cur_avoid = 1.0 - modes.count("FULL_CALC") / len(modes)
            avg_lat = sum(latencies) / len(latencies)
            print(f"  {i}/{num_queries} | avoidance={cur_avoid:.1%} | avg_latency={avg_lat:.1f}ms")

    duration = time.time() - start_bench
    counts = Counter(modes)
    total = len(modes)
    model_calls = counts.get("FULL_CALC", 0) + counts.get("ERROR", 0) + counts.get("LARGE_MODEL", 0)
    avoidance = 1.0 - model_calls / total
    avg_lat = sum(latencies) / total
    p95_lat = sorted(latencies)[int(0.95 * total)]
    cost_saved = (total - model_calls) * 0.002

    print("\n" + "=" * 55)
    print(f"{'REAL WORKLOAD BENCHMARK RESULTS':^55}")
    print("=" * 55)
    print(f"Total Queries:         {total}")
    print(f"Duration:              {duration:.2f}s")
    print(f"Avg Latency:           {avg_lat:.1f}ms")
    print(f"P95 Latency:           {p95_lat:.1f}ms")
    print(f"Inference Avoidance:   {avoidance:.1%}  {'✓ TARGET MET' if avoidance > 0.80 else '⚠ BELOW TARGET'}")
    print(f"Model Calls:           {model_calls} ({model_calls/total:.1%})")
    print(f"Est. Cost Saved:       ${cost_saved:.2f}")
    print("\nLayer Hit Distribution:")
    for mode_name, count in sorted(counts.items(), key=lambda x: -x[1]):
        bar = "█" * int(count / total * 30)
        print(f"  {mode_name:<25} {count:>5}  {bar}")
    print("=" * 55)
    return avoidance


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", type=int, default=1000)
    parser.add_argument("--mode", choices=["pattern", "medium", "mixed"], default="mixed")
    args = parser.parse_args()
    asyncio.run(run_benchmark(args.queries, args.mode))
