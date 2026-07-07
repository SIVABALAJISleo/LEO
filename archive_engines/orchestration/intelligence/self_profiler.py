import time
import json
import logging
import os

logger = logging.getLogger(__name__)

class SelfProfilingOptimizer:
    """
    Measures latency and memory during runtime.
    Automatically reconfigures pipeline paths for the next run.
    """
    def __init__(self, profile_path: str = "config/profile_history.json"):
        self.profile_path = profile_path
        self.history = self._load()

    def _load(self):
        if os.path.exists(self.profile_path):
            with open(self.profile_path, 'r') as f:
                return json.load(f)
        return {"tasks": {}}

    def record_run(self, task_name: str, duration: float, memory_mb: float):
        """Logs telemetry for a specific execution path."""
        if task_name not in self.history["tasks"]:
            self.history["tasks"][task_name] = []
        
        self.history["tasks"][task_name].append({
            "ts": time.time(),
            "duration": duration,
            "mem": memory_mb
        })
        
        # Cap history
        if len(self.history["tasks"][task_name]) > 50:
            self.history["tasks"][task_name].pop(0)
            
        self._save()

    def get_suggested_path(self, task_name: str, target_latency: float) -> str:
        """
        Suggests whether to use 'full' or 'approx' based on history.
        """
        task_data = self.history["tasks"].get(task_name)
        if not task_data:
            return "exploratory_full"
            
        avg_latency = sum(r['duration'] for r in task_data) / len(task_data)
        
        if avg_latency > target_latency * 1.5:
            logger.info(f"Profiling Suggestion: {task_name} is slow ({avg_latency:.2f}s). Recommending APPROX.")
            return "approximate"
        return "full"

    def _save(self):
        os.makedirs(os.path.dirname(self.profile_path), exist_ok=True)
        with open(self.profile_path, 'w') as f:
            json.dump(self.history, f)

if __name__ == "__main__":
    spo = SelfProfilingOptimizer(profile_path="temp_profile.json")
    spo.record_run("raymarch", 0.5, 100)
    print(f"Path Suggestion: {spo.get_suggested_path('raymarch', 0.1)}")
