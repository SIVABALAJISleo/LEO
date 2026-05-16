import time
import json
import logging
from .replay_runtime import SemanticReplayRuntime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')

def run_comprehensive_benchmark():
    print("===================================================================")
    print("       HYPERCORE RUNTIME — MODULE 1 BENCHMARK & TELEMETRY          ")
    print("===================================================================")
    
    # Initialize runtime with aggressive thresholds for demonstration
    runtime = SemanticReplayRuntime(
        threshold=0.85,
        verification_threshold=0.94,
        force_fallback=False, # Will use SentenceTransformer if available, else TF-IDF+SVD
        max_cache_size=5,     # Small size to demonstrate LRU/Entropy eviction
        ttl_seconds=10.0      # Short TTL to demonstrate age invalidation
    )

    test_queries = [
        # 1. Initial Miss -> Populates cache
        ("What is the capital of France?", "Expected Miss (Initial query)"),
        
        # 2. Exact Fingerprint Hit
        ("What is the capital of France?", "Expected Exact Fingerprint Hit"),
        
        # 3. High-confidence Semantic Replay Hit (ANN/LSH)
        ("Tell me what the capital of France is.", "Expected Semantic Replay Hit (High confidence)"),
        
        # 4. Borderline match -> Triggers Exact Verification Fallback
        ("What is the main capital city of France?", "Expected Borderline Match -> Exact Verification Fallback"),
        
        # 5. Completely novel query -> Replay Miss -> Compute Backend
        ("Explain the principles of quantum entanglement in qubits.", "Expected Replay Miss -> Compute Backend"),
        
        # 6. Another novel query to trigger max_size eviction (max_size=5)
        ("How does Backpropagation work in deep neural networks?", "Expected Replay Miss -> Compute Backend (Fills cache)"),
        ("What is the architectural advantage of Mamba SSM over Attention?", "Expected Replay Miss -> Triggers Eviction (Max size overflow)"),
    ]

    print("\n[Executing Query Workload Workstream]")
    print("-------------------------------------------------------------------")
    
    total_compute_time_saved = 0.0

    for idx, (query, expectation) in enumerate(test_queries, 1):
        print(f"\nQuery #{idx}: '{query}'")
        print(f"--> Expectation: {expectation}")
        
        res = runtime.execute(query)
        
        print(f"    Source:      {res['source'].upper()}")
        print(f"    Match Type:  {res['match_type']}")
        print(f"    Confidence:  {res['confidence']:.4f}")
        print(f"    Latency:     {res['total_latency_sec']:.6f}s (Search: {res['search_latency_sec']:.6f}s)")
        print(f"    Response:    {res['response']}")

        if res['replayed']:
            # Assuming average compute backend latency of ~0.35s avoided
            total_compute_time_saved += 0.35

    print("\n[Testing TTL Expiration Invalidation Policy]")
    print("-------------------------------------------------------------------")
    print("Sleeping for 11 seconds to let cache TTL expire (ttl=10s)...")
    time.sleep(11)
    
    # Query again -> Should be a miss due to TTL expiration
    query_ttl = "What is the capital of France?"
    print(f"\nQuery after TTL: '{query_ttl}'")
    res_ttl = runtime.execute(query_ttl)
    print(f"    Source:      {res_ttl['source'].upper()} (Expected COMPUTE_BACKEND due to TTL eviction)")
    print(f"    Match Type:  {res_ttl['match_type']}")
    print(f"    Latency:     {res_ttl['total_latency_sec']:.6f}s")

    print("\n===================================================================")
    print("                   FINAL SYSTEM TELEMETRY & METRICS                ")
    print("===================================================================")
    metrics = runtime.get_system_metrics()
    metrics["estimated_compute_time_saved_sec"] = round(total_compute_time_saved, 4)
    print(json.dumps(metrics, indent=2))
    print("===================================================================")

if __name__ == "__main__":
    run_comprehensive_benchmark()
