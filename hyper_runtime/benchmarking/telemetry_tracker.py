import time
import psutil
import json
import csv
import os
from typing import Dict, Any

class TelemetryTracker:
    """
    Centralized telemetry and metric tracker for HyperCore Runtime.
    Logs system usage, compute savings, latencies, and hit rates.
    """
    def __init__(self, log_dir: str = ".hyper_cache/telemetry"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.metrics_log = []
        
        # Aggregated Metrics
        self.total_queries = 0
        self.replay_hits = 0
        self.total_dense_flops = 0.0
        self.total_actual_flops = 0.0
        self.total_latency_sec = 0.0
        
        # CPU/Mem tracking start
        self.process = psutil.Process(os.getpid())
        self.start_time = time.time()
        
    def record_query(self, query_id: str, routing_tier: str, latency_sec: float, flop_data: dict, cpu_usage: float, mem_usage_mb: float):
        """Records a single query execution."""
        self.total_queries += 1
        if routing_tier == "replay_retrieval":
            self.replay_hits += 1
            
        self.total_dense_flops += flop_data.get("dense_flops", 0.0)
        self.total_actual_flops += flop_data.get("actual_flops", 0.0)
        self.total_latency_sec += latency_sec
        
        entry = {
            "query_id": query_id,
            "timestamp": time.time(),
            "routing_tier": routing_tier,
            "latency_sec": round(latency_sec, 4),
            "savings_ratio": round(flop_data.get("savings_ratio", 0.0), 4),
            "cpu_percent": round(cpu_usage, 2),
            "mem_mb": round(mem_usage_mb, 2)
        }
        self.metrics_log.append(entry)

    def generate_report(self) -> Dict[str, Any]:
        """Generates the aggregated telemetry report."""
        replay_rate = self.replay_hits / max(1, self.total_queries)
        compute_reduction = 1.0 - (self.total_actual_flops / max(1.0, self.total_dense_flops))
        avg_latency = self.total_latency_sec / max(1, self.total_queries)
        
        report = {
            "uptime_sec": round(time.time() - self.start_time, 2),
            "total_queries": self.total_queries,
            "replay_hit_rate": round(replay_rate, 4),
            "global_compute_reduction_ratio": round(compute_reduction, 4),
            "avg_latency_sec": round(avg_latency, 4),
            "total_dense_tflops": round(self.total_dense_flops / 1e12, 4),
            "total_actual_tflops": round(self.total_actual_flops / 1e12, 4)
        }
        return report
        
    def export_csv(self):
        """Exports log to CSV."""
        if not self.metrics_log:
            return
        keys = self.metrics_log[0].keys()
        path = os.path.join(self.log_dir, "telemetry.csv")
        with open(path, 'w', newline='') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.metrics_log)
            
    def export_json(self):
        """Exports aggregated report to JSON."""
        path = os.path.join(self.log_dir, "telemetry_report.json")
        with open(path, 'w') as f:
            json.dump(self.generate_report(), f, indent=2)
