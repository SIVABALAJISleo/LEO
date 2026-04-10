import asyncio
import time
import random
import logging
import uuid
from collections import Counter
from backend.core.orchestrator import hyper_engine
from backend.predictive.answer_store import global_predictive_store
from backend.shadow.shadow_store import global_shadow_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_optimization_benchmark(num_queries=100):
    print(f"Starting AI Inference Optimization Benchmark: {num_queries} Queries")
    
    tenant_id = "bench_optimized"
    workspace_id = "ws_optimization"
    
    # 1. PRE-FILL KNOWLEDGE BASE (Patterns)
    knowledge_patterns = [
        "What is RAG vs fine-tuning?",
        "How to optimize LLM latency?",
        "Explain speculative decoding advantages.",
        "Calculate the ROI of GPU savings.",
        "Summarize the project HYPER architecture.",
        "Write a python function for vector search."
    ]
    
    # Simulate historical learning (Continuous Learning)
    for q in knowledge_patterns:
        from backend.learning.answer_store import global_learning_engine
        await global_learning_engine.learn(q, f"Optimized answer for {q}", 0.99, tenant_id, workspace_id)

    print("\n--- BENCHMARK RESULTS ---")
    # 2. BENCHMARK EXECUTION
    modes = []
    latencies = []
    
    start_bench = time.time()
    for i in range(num_queries):
        # Distribution: 
        # 40% Predictive/Shadow hits
        # 20% Cache hits
        # 20% Micro-model / Planner
        # 20% Full Inference fallback
        
        r = random.random()
        if r < 0.4:
            query = random.choice(knowledge_patterns)
        elif r < 0.6:
            query = f"Unique query variation {i % 100}" # High cache hit probability
        elif r < 0.7:
             query = "Calculate 123 * 456" # Math Micro-model
        elif r < 0.8:
             query = "What is RAG compared to fine-tuning?" # Planner (Comparative)
        else:
            query = f"Deep research query for token {uuid.uuid4().hex[:4]}" # Fallback
            
        start_req = time.time()
        result = await hyper_engine.process(query, f"bench_{i}", tenant_id=tenant_id, workspace_id=workspace_id)
        latency = (time.time() - start_req) * 1000
        
        modes.append(result["mode"])
        latencies.append(latency)
        
        if i % 1000 == 0 and i > 0:
            print(f"  Processed {i}/{num_queries} queries... (Current Avoidance: {1.0 - modes.count('FULL_CALC')/len(modes):.2%})")

    duration = time.time() - start_bench
    avg_latency = sum(latencies) / len(latencies)
    counts = Counter(modes)
    avoidance_ratio = 1.0 - counts.get("FULL_CALC", 0) / num_queries
    
    print("\nBenchmark Complete!")
    print(f"Total Duration: {duration:.2f}s")
    print(f"Average Latency: {avg_latency:.2f}ms")
    print(f"Inference Avoidance Ratio: {avoidance_ratio:.2%}")
    print("\nLayer Distribution:")
    for mode, count in counts.items():
        print(f"  {mode}: {count} ({count/num_queries*100:.1f}%)")

import uuid
if __name__ == "__main__":
    from backend.core.database import init_db
    init_db()
    
    async def run():
        from backend.core.orchestrator import hyper_engine
        await hyper_engine.start()
        await run_optimization_benchmark()
        
    asyncio.run(run())
