import time
from telemetry import TelemetrySystem

def run_suite():
    telemetry = TelemetrySystem()
    print("Starting Benchmark Suite...")
    
    for i in range(5):
        start = time.time()
        time.sleep(0.1) 
        latency = time.time() - start
        
        source = "semantic_cache" if i % 3 == 0 else "compute"
        tokens = 50 
        
        telemetry.record_inference(tokens, latency, source=source)
        
    telemetry.export("benchmark_results.jsonl")
    print("Benchmark completed. Metrics exported.")

if __name__ == "__main__":
    run_suite()
