"""
tests/benchmark.py
Validation script: simulates usage to measure real inference avoidance.
"""
import sys
import os
import asyncio
import time

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.orchestrator import hyper_engine
from backend.analytics.metrics import global_metrics

async def run_benchmark():
    print(" Starting HYPER Benchmark Validations...")
    print("-" * 50)
    
    queries = [
        # 1. New complex query -> Full LLM + RAG + Shadow Precompute
        "What is the advantage of using vector databases with sentence transformers?",
        
        # 2. Exact same query -> Exact Cache (Delta Engine FULL_MATCH)
        "What is the advantage of using vector databases with sentence transformers?",
        
        # 3. Similar query -> Semantic Delta (PARTIAL_MATCH)
        "What are the steps to implement vector databases with sentence transformers?",
        
        # 4. Shadow prediction hit -> Should hit SHADOW_STORE
        "how to deploy sentence transformers", # (Likely predicted by shadow worker from previous)
        
        # 5. Micro Model Routing -> Math
        "Calculate the percentage of 50 out of 200",
        
        # 6. Micro Model Routing -> Code
        "Write a python function to add two numbers",
        
        # 7. Exact cache on code
        "Write a python function to add two numbers",
    ]
    
    for i, q in enumerate(queries):
        print(f"\n[Query {i+1}] {q}")
        start = time.time()
        res = await hyper_engine.process(q, request_id=f"bench_user1_{i}", tenant_id="tenant_bench")
        elapsed = (time.time() - start) * 1000
        print(f"   Mode: {res.get('mode', 'N/A')}")
        print(f"   Latency: {elapsed:.1f}ms")
        print(f"   Result snippet: {str(res.get('result', ''))[:80]}...")
        # Small delay to let background shadow worker finish
        await asyncio.sleep(1.0)
        
    print("\n" + "=" * 50)
    print(" REAL INFERENCE METRICS")
    print("=" * 50)
    metrics = global_metrics.get_metrics()
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"{k.ljust(20)} : {v*100:.1f}%" if "pct" in k or "rate" in k else f"{k.ljust(20)} : {v}")
        else:
            print(f"{k.ljust(20)} : {v}")
            
    if metrics["avoidance_rate"] >= 0.8:
        print("\n SUCCESS: Hyper-Scale Inference Avoidance achieved!")
    else:
        print("\n FAILED: Did not reach avoidance threshold.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())