"""
tests/benchmark_unknown.py
Validation script for Unknown Query Handling Engine.
"""
import sys
import os
import asyncio
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.orchestrator import hyper_engine
from backend.analytics.metrics import global_metrics

async def run_benchmark():
    print("Starting Unknown Query Pipeline Benchmark...")
    print("-" * 50)
    
    queries = [
        # 1. Unknown but decomposable standard query
        "What is the definition of hyper-threading and what are its advantages?",
        
        # 2. Creative simulation query
        "Imagine a synergy between quantum computing and biological neural networks.",
        
        # 3. Completely novel concept (should trigger domain expansion)
        "Explain Xylophony acoustics applied to space travel.",
        
        # 4. Another creative variation
        "Create a design pattern that fuses microservices with monolithic architecture.",
        
        # 5. A repeat of the novel concept to prove it expanded and cached
        "Explain Xylophony acoustics applied to space travel."
    ]
    
    for i, q in enumerate(queries):
        print(f"\n[Query {i+1}] {q}")
        start = time.time()
        res = await hyper_engine.process(q, request_id=f"bench_unknown_{i}", tenant_id="tenant_unknown")
        elapsed = (time.time() - start) * 1000
        print(f"  -- Mode: {res.get('mode', 'N/A')}")
        print(f"  -- Latency: {elapsed:.1f}ms")
        
        snip = str(res.get('result', ''))[:80].replace("\n", " ")
        print(f"  -- Snippet: {snip}...")
        
        # Give background tasks (like Domain Expander) a second to finish
        await asyncio.sleep(1.5)
        
    print("\n" + "=" * 50)
    print("UNKNOWN QUERY METRICS")
    print("=" * 50)
    
    metrics = global_metrics.get_metrics()
    for k, v in metrics["unknown_handling"].items():
        if isinstance(v, float):
            print(f"{k.ljust(35)} : {v*100:.1f}%")
        else:
            print(f"{k.ljust(35)} : {v}")
            
    # Also print standard avoidance
    print(f"{'general_avoidance_rate'.ljust(35)} : {metrics['avoidance_rate']*100:.1f}%")
            
    if metrics["unknown_handling"]["composition_success_rate"] >= 0.6:
        print("\nSUCCESS: Unknown handling compute reduction achieved (>= 60%)!")
    else:
        print("\nFAILED: Missed unknown query avoidance threshold.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
