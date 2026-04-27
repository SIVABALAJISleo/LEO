import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class ComputeRouter:
    """
    STEP 3: ROUTING DECISION
    Optimizes for Quality, Latency, and Cost.
    """
    def decide_route(self, task_type: str, hw_profile: Dict[str, Any], query: str) -> Tuple[str, str]:
        # Logic: 
        # 1. Prefer Local iGPU for standard LLM if available.
        # 2. Prefer Local CPU for simple text/data.
        # 3. Escalate to Cloud API only if complex or HW limited.
        
        if task_type == "LLM":
            if hw_profile["has_igpu"] and hw_profile["ram_gb"] > 8:
                return "LOCAL_IGPU", "High-RAM iGPU detected; optimal for local inference."
            if hw_profile["cpu_cores"] >= 4:
                return "LOCAL_CPU", "Multi-core CPU available for llama.cpp."
            return "CLOUD_API", "Hardware constraints require cloud escalation."
            
        if task_type == "IMAGE":
            return "CLOUD_API", "Local image generation avoided per safety rules."
            
        return "LOCAL_CPU", "Defaulting to local CPU for generic tasks."

    def estimate_cost(self, route: str) -> str:
        costs = {
            "LOCAL_CPU": "$0.00 (Local Compute)",
            "LOCAL_IGPU": "$0.00 (Local Compute)",
            "CLOUD_API": "$0.01 - $0.05 (Estimated API cost)"
        }
        return costs.get(route, "Unknown")
