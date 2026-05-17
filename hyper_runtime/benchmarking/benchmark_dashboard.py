import time
import psutil
import os
import sys

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hyper_runtime.benchmarking.telemetry_tracker import TelemetryTracker
from hyper_runtime.benchmarking.flop_estimator import FLOPsEstimator

def run_benchmark():
    print("=" * 70)
    print("  HYPERCORE RUNTIME — MODULE 6: TELEMETRY & BENCHMARKING")
    print("=" * 70)
    
    tracker = TelemetryTracker()
    flop_estimator = FLOPsEstimator(hidden_dim=4096, total_layers=32)
    process = psutil.Process(os.getpid())
    
    # Simulated execution workload
    queries = [
        {"id": "q1", "desc": "Cached Query (Exact Match)", "tier": "replay_retrieval", "sparsity": (0, 0, 0), "exit": 0, "lat": 0.005},
        {"id": "q2", "desc": "Similar Query (Semantic Hit)", "tier": "replay_retrieval", "sparsity": (0, 0, 0), "exit": 0, "lat": 0.012},
        {"id": "q3", "desc": "Novel Query (Sparse Route)", "tier": "sparse_execution", "sparsity": (0.2, 0.4, 0.75), "exit": 16, "lat": 0.450},
        {"id": "q4", "desc": "Novel Query (Sparse Route)", "tier": "sparse_execution", "sparsity": (0.1, 0.2, 0.75), "exit": 24, "lat": 0.620},
        {"id": "q5", "desc": "Highly Complex (Dense Route)", "tier": "dense_execution", "sparsity": (0.0, 0.0, 0.0), "exit": 32, "lat": 1.200},
        {"id": "q6", "desc": "Cached Query (Exact Match)", "tier": "replay_retrieval", "sparsity": (0, 0, 0), "exit": 0, "lat": 0.005},
    ]
    
    print("\n[Processing Simulated Workload]")
    print("-" * 70)
    
    for q in queries:
        print(f"Processing {q['id']} ({q['desc']})...")
        time.sleep(0.1) # Simulating processing time for the dashboard
        
        is_replay = q['tier'] == "replay_retrieval"
        flop_data = flop_estimator.calculate_savings(
            is_replay_hit=is_replay,
            tome_sparsity=q['sparsity'][0],
            gating_sparsity=q['sparsity'][1],
            moe_sparsity=q['sparsity'][2],
            exit_layer=q['exit']
        )
        
        cpu_usage = process.cpu_percent()
        mem_usage = process.memory_info().rss / (1024 * 1024) # MB
        
        tracker.record_query(q['id'], q['tier'], q['lat'], flop_data, cpu_usage, mem_usage)
        print(f"  -> FLOP Savings: {flop_data['savings_ratio']*100:.1f}% | Latency: {q['lat']}s")

    print("\n[Exporting Telemetry Data]")
    tracker.export_csv()
    tracker.export_json()
    print("  -> CSV and JSON reports saved to .hyper_cache/telemetry/")
    
    print("\n" + "=" * 70)
    print("  TELEMETRY DASHBOARD REPORT")
    print("=" * 70)
    
    report = tracker.generate_report()
    for k, v in report.items():
        print(f"{k.replace('_', ' ').title():<35}: {v}")

if __name__ == "__main__":
    run_benchmark()
