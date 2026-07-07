import asyncio
import time
import random
import logging
from collections import Counter
from backend.core.orchestrator import hyper_engine
from backend.predictive.answer_store import global_predictive_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_product_benchmark(num_queries=1000):
    print(f"🚀 Starting Startup Product Benchmark: {num_queries} Queries")
    
    tenant_id = "startup_test"
    workspace_id = "ws_benchmark"
    
    # 1. Warm up with some predictive data
    patterns = ["How do I configure billing?", "What is the GPU cost savings?", "How does RAG work?"]
    for p in patterns:
        global_predictive_store.save_answer(p, f"Answer for {p}", 0.99, tenant_id=tenant_id, workspace_id=workspace_id)

    # 2. Simulate high-concurrency requests
    modes = []
    latencies = []
    
    start_bench = time.time()
    for i in range(num_queries):
        # Weighted distribution to test bypass layers
        r = random.random()
        if r < 0.4:
            query = random.choice(patterns) # Predictive Hit
        elif r < 0.6:
            query = f"Unique Query {i}" # Full Calc / Retrieval
        else:
            query = random.choice(patterns) # Another hit chance
            
        start_req = time.time()
        result = await hyper_engine.process(query, f"req_{i}", tenant_id=tenant_id, workspace_id=workspace_id)
        latency = (time.time() - start_req) * 1000
        
        modes.append(result["mode"])
        latencies.append(latency)
        
        if i % 100 == 0:
            print(f"  Processed {i}/{num_queries} queries...")

    duration = time.time() - start_bench
    avg_latency = sum(latencies) / len(latencies)
    counts = Counter(modes)
    
    print("\n✅ Benchmark Complete!")
    print(f"Total Duration: {duration:.2f}s")
    print(f"Average Latency: {avg_latency:.2f}ms")
    print("\nHit Distribution:")
    for mode, count in counts.items():
        print(f"  {mode}: {count} ({count/num_queries*100:.1f}%)")

if __name__ == "__main__":
    from backend.core.database import init_db
    init_db()
    asyncio.run(run_product_benchmark())
