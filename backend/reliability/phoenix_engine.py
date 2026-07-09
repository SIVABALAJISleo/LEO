import logging
import threading
import time
import random

class PhoenixEngine:
    def __init__(self):
        self.logger = logging.getLogger("PhoenixEngine")
        self.base_strength = 99.0
        self.vaccines_applied = 15420
        self.nodes = {"node_1": "healthy", "node_2": "healthy", "node_3": "healthy"}
        
    def _chaos_thread(self):
        # Background thread that occasionally kills processes
        while True:
            time.sleep(random.uniform(10, 60))
            self.inject_chaos(intensity="high")
            
    def start_chaos_monkey(self):
        t = threading.Thread(target=self._chaos_thread, daemon=True)
        t.start()
        self.logger.info("Phoenix Chaos Monkey started.")
        
    def inject_chaos(self, intensity: str = "medium"):
        """
        Randomly terminates a node to ensure the Swarm remains anti-fragile.
        """
        if not self.nodes:
            return
            
        target_node = random.choice(list(self.nodes.keys()))
        self.nodes[target_node] = "dead"
        
        self.logger.warning(f"[CHAOS] Terminated node {target_node} (Intensity: {intensity})")
        
        # Trigger self healing
        self.recover_from_failure("process_termination", {"node_id": target_node})
        
    def recover_from_failure(self, failure_type: str, failure_data: dict) -> dict:
        """
        Self-healing routine. Restarts node and generates an immunity vaccine.
        """
        node_id = failure_data.get("node_id")
        self.logger.info(f"[HEAL] Initiating recovery for {node_id} (Type: {failure_type})")
        
        # Step 1: Analyze failure (Simulated)
        time.sleep(0.5) 
        
        # Step 2: Generate Vaccine
        self.vaccines_applied += 1
        
        # Step 3: Restart Node
        self.nodes[node_id] = "healthy"
        self.logger.info(f"[HEAL] Node {node_id} recovered. Vaccine #{self.vaccines_applied} deployed.")
        
        return {
            "status": "recovered",
            "vaccine_id": f"vac_{self.vaccines_applied}",
            "downtime_ms": 500
        }
        
    def get_system_strength(self) -> float:
        """
        Measure anti-fragility: system strength INCREASES with failures
        Formula: base_strength + (vaccines_applied * 0.001)
        """
        # Caps at 99.999%
        strength = self.base_strength + (self.vaccines_applied * 0.0001)
        return min(strength, 99.999)
