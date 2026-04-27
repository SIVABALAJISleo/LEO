import random
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class AdaptiveFeedbackStore:
    """
    STEP 16: FEEDBACK LOOP
    Records latency, cost, and quality to update router weights.
    """
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        self.weights = {
            "LOCAL_CPU": 1.0,
            "LOCAL_IGPU": 1.2,
            "CLOUD_API": 0.8
        }

    def record(self, route: str, latency: float, cost: float, quality: float):
        self.history.append({
            "route": route,
            "latency": latency,
            "cost": cost,
            "quality": quality
        })
        # Basic weight update: higher quality and lower latency/cost increases weight
        score = (quality) / (latency + cost + 0.1)
        self.weights[route] = (self.weights[route] * 0.9) + (score * 0.1)

class AdaptiveRouter:
    """
    STEP 5: SELF-OPTIMIZING ROUTER (WITH EXPLORATION)
    Implements the 90/10 exploitation/exploration rule.
    """
    def __init__(self, feedback_store: AdaptiveFeedbackStore):
        self.store = feedback_store

    def decide_route(self, task_type: str, hw_profile: Dict[str, Any]) -> str:
        # 10% Exploration (Step 5)
        if random.random() < 0.10:
            routes = ["LOCAL_CPU", "LOCAL_IGPU", "CLOUD_API"]
            choice = random.choice(routes)
            logger.info(f"Router EXPLORATION mode: Selected {choice}")
            return choice
        
        # 90% Exploitation
        # Filter routes based on hardware capability
        viable_routes = ["LOCAL_CPU"]
        if hw_profile["has_igpu"]: viable_routes.append("LOCAL_IGPU")
        viable_routes.append("CLOUD_API")
        
        # Select highest weighted viable route
        best_route = max(viable_routes, key=lambda r: self.store.weights.get(r, 0))
        logger.info(f"Router EXPLOITATION mode: Selected {best_route}")
        return best_route
