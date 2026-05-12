import time
from replay_runtime import SemanticReplayRuntime

def run_benchmark():
    runtime = SemanticReplayRuntime(threshold=0.90)
    
    queries = [
        "What is the capital of France?",
        "Tell me about quantum computing.",
        "What is the capital of France?", # Exact repeat
        "What's the capital of France?", # Semantic repeat (mocked)
        "Explain quantum computing basics." 
    ]
    
    print("Running Semantic Replay Benchmark...")
    total_compute_avoided = 0.0
    
    for q in queries:
        res = runtime.execute(q)
        print(f"Q: {q}")
        print(f"  Source: {res['source']} | Latency: {res['latency_sec']:.4f}s | Score: {res['confidence']:.3f}")
        if res['source'] == 'replay':
            total_compute_avoided += 0.5 # Based on mock backend latency
            
    metrics = runtime.cache.get_metrics()
    print("\n--- Benchmark Results ---")
    print(f"Hit Rate: {metrics['hit_rate']*100:.1f}%")
    print(f"Compute Time Saved: {total_compute_avoided:.2f}s")

if __name__ == "__main__":
    run_benchmark()
