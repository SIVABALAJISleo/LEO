import time
import json
import psutil

class TelemetrySystem:
    def __init__(self):
        self.metrics = []
        
    def record_inference(self, tokens_generated, latency_sec, source="compute"):
        cpu_util = psutil.cpu_percent()
        ram_util = psutil.virtual_memory().percent
        
        metric = {
            "timestamp": time.time(),
            "tokens": tokens_generated,
            "latency": latency_sec,
            "tps": tokens_generated / latency_sec if latency_sec > 0 else 0,
            "source": source,
            "cpu_util": cpu_util,
            "ram_util": ram_util
        }
        self.metrics.append(metric)
        
    def export(self, filepath="metrics.jsonl"):
        with open(filepath, "a") as f:
            for m in self.metrics:
                f.write(json.dumps(m) + "\n")
        self.metrics = []
