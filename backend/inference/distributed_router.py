import logging
import random
import psutil
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DistributedInferenceController:
    """
    Manages and load balances inference jobs across a cluster of workers.
    Monitors node health and resource availability (CPU/GPU).
    """
    def __init__(self):
        # In a real system, this would be a registry of alive workers (e.g., via Redis/Consul)
        self.workers = [
            {"id": "worker_1", "type": "gpu", "utilization": 0.2, "status": "alive"},
            {"id": "worker_2", "type": "gpu", "utilization": 0.8, "status": "alive"},
            {"id": "worker_3", "type": "cpu", "utilization": 0.1, "status": "alive"}
        ]

    def get_optimal_worker(self, requirement: str = "gpu") -> Optional[Dict[str, Any]]:
        """
        Selects the best available worker based on requirement and current load.
        """
        candidates = [w for w in self.workers if w["status"] == "alive" and w["type"] == requirement]
        
        if not candidates:
            # Fallback to any alive worker
            candidates = [w for w in self.workers if w["status"] == "alive"]
            
        if not candidates:
            logger.error("no_worker_available")
            return None
            
        # Select worker with lowest utilization
        selected = min(candidates, key=lambda x: x["utilization"])
        logger.info(f"distributed_routing: selected_worker={selected['id']} type={selected['type']}")
        return selected

    async def route_job(self, task_fn, *args, **kwargs) -> Any:
        """
        High-level wrapper to route a task to the distributed backend.
        """
        worker = self.get_optimal_worker()
        if not worker:
            raise RuntimeError("Inference cluster offline")
            
        # Simulated remote execution (In reality, Redis Queue or gRPC)
        res = await task_fn(*args, **kwargs)
        print(f"DEBUG route_job: ret type={type(res)}, val={res}")
        return res

global_inference_controller = DistributedInferenceController()
