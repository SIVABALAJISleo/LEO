import json
import logging
import time
import random
import math
from typing import Dict, Any, List, Tuple, Optional
from intel_core_ai.inference import IntelInferenceEngine

logger = logging.getLogger(__name__)

class SelfLearningRouter:
    """
    [SYSTEM DIRECTIVE — SELF-LEARNING ROUTER + SPEED OPTIMIZATION ENGINE]
    Adaptive decision engine that selects the fastest, cheapest, and most accurate execution path.
    """
    def __init__(self, inference_engine: IntelInferenceEngine, state_path: str = "feedback_state.json"):
        self.engine = inference_engine
        self.state_path = state_path
        self.routes = ["cache", "tiny_model", "main_model", "api_model"]
        self.alpha = 0.2  # Learning rate for moving averages (0.8 old + 0.2 new)
        self.epsilon = 0.1 # 10% Exploration (as per Directive Step [3])
        
        # Initialize or Load State
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        try:
            with open(self.state_path, "r") as f:
                data = json.load(f)
                # Ensure structure for routing_key learning
                if "router_stats" not in data:
                    data["router_stats"] = {}
                if "cache_data" not in data:
                    data["cache_data"] = [] # Simple semantic cache storage
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {"router_stats": {}, "cache_data": [], "threshold": 0.5}

    def _save_state(self):
        try:
            with open(self.state_path, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save router state: {e}")

    def _get_routing_key(self, query: str, task_type: str = "general") -> str:
        """[1] INPUT ANALYSIS: Extract task_type, complexity, length_bucket"""
        length = len(query)
        if length < 50: length_bucket = "short"
        elif length < 200: length_bucket = "medium"
        else: length_bucket = "long"
        
        # Heuristic complexity (can be refined with a tiny model)
        complexity = "low" if length_bucket == "short" else "medium"
        if "?" in query and length_bucket == "long": complexity = "high"
        
        return f"{task_type}:{complexity}:{length_bucket}"

    def _check_cache(self, query: str) -> Optional[Dict[str, Any]]:
        """[2] CACHE FIRST: Similarity >= 0.95"""
        # Placeholder for real semantic similarity. 
        # For now, exact match or simple overlap.
        for entry in self.state.get("cache_data", []):
            if entry["q"].lower().strip() == query.lower().strip():
                return entry
        return None

    def _get_expected_score(self, stats: Dict[str, Any]) -> float:
        """[3] expected_score = success_rate / (latency + cost + risk)"""
        success = stats.get("success", 0)
        fail = stats.get("fail", 0)
        total = success + fail
        
        success_rate = success / total if total > 0 else 0.5 # Default to 0.5 for new routes
        latency = stats.get("latency", 1.0)
        cost = stats.get("cost", 0.1)
        risk = stats.get("risk", 0.05)
        
        return success_rate / (latency + cost + risk)

    def select_route(self, routing_key: str) -> str:
        """[3] ROUTE SELECTION: Epsilon-greedy (Explore 10%, Exploit 90%)"""
        if random.random() < self.epsilon:
            return random.choice(self.routes)
        
        stats_map = self.state["router_stats"].get(routing_key, {})
        best_route = self.routes[0]
        max_score = -1.0
        
        for route in self.routes:
            route_stats = stats_map.get(route, {"success": 1, "fail": 0, "latency": 0.1, "cost": 0.0, "risk": 0.01})
            score = self._get_expected_score(route_stats)
            if score > max_score:
                max_score = score
                best_route = route
        
        return best_route

    async def execute(self, query: str, task_type: str = "general") -> Dict[str, Any]:
        start_time = time.time()
        routing_key = self._get_routing_key(query, task_type)
        
        # 1. Cache Check
        cached = self._check_cache(query)
        if cached:
            return {
                "answer": cached["ans"],
                "calibrated_confidence": 1.0,
                "route_used": "cache"
            }
        
        # 2. Route Selection
        route = self.select_route(routing_key)
        
        # 3. Execution (Simulated logic based on Directive [4])
        # In a real system, these would call different model endpoints
        logger.info(f"Routing query via {route} (key: {routing_key})")
        
        # Placeholder for actual inference logic
        # For now, we use the provided engine as 'main_model'
        system_prompt = f"Execution Route: {route}. Task: {task_type}. Provide a precise answer."
        gen = self.engine.generate_stream(query, system_prompt)
        answer = "".join(list(gen))
        
        # [5] FAST FAIL ESCALATION
        confidence = 0.8 # Placeholder for confidence scoring logic
        if confidence < 0.6 and route != "api_model":
            logger.warning(f"Confidence {confidence} below threshold. Escalating to api_model.")
            route = "api_model"
            gen = self.engine.generate_stream(query, "ESCALATION: Provide maximum accuracy.")
            answer = "".join(list(gen))
            confidence = 0.95

        latency = time.time() - start_time
        
        # [7] FEEDBACK CAPTURE (Simulated success for now)
        success = True if confidence > 0.7 else False
        
        # [8] ROUTER LEARNING UPDATE
        self._update_stats(routing_key, route, success, latency)
        
        # Update cache if success is high
        if success and confidence > 0.9:
            self.state["cache_data"].append({"q": query, "ans": answer})
            if len(self.state["cache_data"]) > 100: self.state["cache_data"].pop(0)
            
        self._save_state()

        return {
            "answer": answer,
            "calibrated_confidence": confidence,
            "route_used": route
        }

    def _update_stats(self, routing_key: str, route: str, success: bool, latency: float):
        """[8] new_value = 0.8 old + 0.2 new"""
        if routing_key not in self.state["router_stats"]:
            self.state["router_stats"][routing_key] = {}
        
        if route not in self.state["router_stats"][routing_key]:
            self.state["router_stats"][routing_key][route] = {
                "success": 0, "fail": 0, "latency": latency, "cost": 0.05, "risk": 0.05
            }
            
        stats = self.state["router_stats"][routing_key][route]
        
        if success: stats["success"] += 1
        else: stats["fail"] += 1
        
        # Moving average for latency
        stats["latency"] = (1 - self.alpha) * stats["latency"] + self.alpha * latency
        
        # Cost is usually fixed per route but could be learned
        cost_map = {"cache": 0.0, "tiny_model": 0.01, "main_model": 0.05, "api_model": 0.2}
        stats["cost"] = cost_map.get(route, 0.1)
        
        # Risk update
        risk_val = 0.0 if success else 1.0
        stats["risk"] = (1 - self.alpha) * stats["risk"] + self.alpha * risk_val
