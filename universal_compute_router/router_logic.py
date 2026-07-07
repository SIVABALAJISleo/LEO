import logging
import json
import random
from typing import Dict, Any

logger = logging.getLogger(__name__)

class UniversalComputeRouter:
    """
    [SYSTEM DIRECTIVE — UNIVERSAL COMPUTE ROUTER (80% GPU DOMAIN COVERAGE)]
    Intelligent orchestrator that routes tasks to CPU, local engines, or API fallbacks.
    """
    def __init__(self, state_path: str = "router_state.json"):
        self.state_path = state_path
        self.routes = [
            "tiny_model", "main_model", "video_engine", 
            "data_engine", "solver_engine", "api_fallback"
        ]
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        try:
            with open(self.state_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"stats": {}, "cache": []}

    def _save_state(self):
        with open(self.state_path, "w") as f:
            json.dump(self.state, f, indent=2)

    def classify_task(self, query: str) -> Dict[str, Any]:
        """[1] TASK CLASSIFICATION: Extract task_type, complexity, input_size"""
        query_lower = query.lower()
        
        # Heuristic classification (can be upgraded to a tiny-LLM classifier)
        task_type = "AI"
        if any(w in query_lower for w in ["video", "ffmpeg", "mp4", "upscale"]):
            task_type = "VIDEO"
        elif any(w in query_lower for w in ["data", "csv", "json", "table", "dataframe", "polars", "duckdb"]):
            task_type = "DATA"
        elif any(w in query_lower for w in ["optimize", "solver", "path", "route", "constraint", "schedule"]):
            task_type = "OPTIMIZATION"
            
        complexity = "medium"
        if len(query) < 50: complexity = "simple"
        elif len(query) > 500: complexity = "complex"
        
        return {
            "task_type": task_type,
            "complexity": complexity,
            "query_length": len(query)
        }

    def decide_route(self, task_metadata: Dict[str, Any]) -> str:
        """[3] ROUTING DECISION: UCB / Epsilon-Greedy"""
        routing_key = f"{task_metadata['task_type']}:{task_metadata['complexity']}"
        
        # Epsilon-greedy: 10% explore
        if random.random() < 0.1:
            return random.choice(self.routes)
            
        # Exploit: Select based on expected_score
        stats = self.state["stats"].get(routing_key, {})
        best_route = "main_model" # Default
        max_score = -1.0
        
        for route in self.routes:
            r_stats = stats.get(route, {"success": 1, "fail": 0, "latency": 0.1, "cost": 0.01, "risk": 0.01})
            score = self._calculate_expected_score(r_stats)
            if score > max_score:
                max_score = score
                best_route = route
                
        return best_route

    def _calculate_expected_score(self, stats: Dict[str, Any]) -> float:
        """expected_score = success_rate / (latency + cost + risk)"""
        total = stats["success"] + stats["fail"]
        success_rate = stats["success"] / total if total > 0 else 0.5
        return success_rate / (stats["latency"] + stats["cost"] + stats["risk"])

    def update_learning(self, task_metadata: Dict[str, Any], route: str, success: bool, latency: float):
        """[9] ROUTER LEARNING UPDATE: 0.8 old + 0.2 new"""
        routing_key = f"{task_metadata['task_type']}:{task_metadata['complexity']}"
        if routing_key not in self.state["stats"]:
            self.state["stats"][routing_key] = {}
            
        if route not in self.state["stats"][routing_key]:
            self.state["stats"][routing_key][route] = {
                "success": 0, "fail": 0, "latency": latency, "cost": 0.05, "risk": 0.05
            }
            
        stats = self.state["stats"][routing_key][route]
        if success: stats["success"] += 1
        else: stats["fail"] += 1
        
        # Moving averages
        alpha = 0.2
        stats["latency"] = (1 - alpha) * stats["latency"] + alpha * latency
        # Cost mapping (heuristic)
        costs = {"tiny_model": 0.01, "main_model": 0.05, "api_fallback": 0.2, "video_engine": 0.05, "data_engine": 0.02, "solver_engine": 0.03}
        stats["cost"] = costs.get(route, 0.1)
        stats["risk"] = (1 - alpha) * stats["risk"] + alpha * (0.0 if success else 1.0)
        
        self._save_state()
