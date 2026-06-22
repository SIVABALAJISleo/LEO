"""
Layer 1: Intelligent Routing Layer
Classifies queries and determines complexity, domain, intent, and V19 routing targets.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class IntelligentRouter:
    def __init__(self):
        self.layer_id = 1
        self.layer_name = "Layer 1: Intelligent Router"

    def execute(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        query_lower = query.lower().strip()
        
        # 1. Intent & Domain Detection
        intent = "general"
        domain = "general"
        if any(w in query_lower for w in ["how to", "code", "function", "compile", "bug", "error"]):
            intent = "reasoning"
            domain = "coding"
        elif any(w in query_lower for w in ["why", "compare", "debate", "versus", "vs"]):
            intent = "debate"
            domain = "philosophy_or_science"
        elif any(w in query_lower for w in ["what is", "define", "history", "who"]):
            intent = "knowledge"
            domain = "factual"
        elif any(w in query_lower for w in ["policy", "compliance", "standard", "regulation"]):
            intent = "enterprise"
            domain = "compliance"
        elif any(w in query_lower for w in ["nature", "ieee", "physics", "gravity", "force"]):
            intent = "scientific"
            domain = "science"
        elif len(query.split()) < 4:
            intent = "simple"
            domain = "general"

        # 2. Complexity Scoring
        word_count = len(query.split())
        complexity = min(1.0, (word_count / 25.0) * 0.5 + (0.5 if intent in ["reasoning", "debate"] else 0.0))

        # 3. Confidence Prediction
        confidence = round(0.95 - (complexity * 0.3), 2)

        # 4. Routing Decision Rules for V19
        if intent == "simple" or complexity < 0.2:
            route_target = "cache"
        elif intent == "knowledge" and complexity < 0.5:
            route_target = "memory"
        elif intent == "knowledge" and complexity >= 0.5:
            route_target = "graphrag"
        elif intent == "enterprise":
            route_target = "knowledge_graph"
        elif intent == "reasoning":
            route_target = "llm"
        elif intent == "debate":
            route_target = "multi_agent_debate"
        elif intent == "scientific":
            route_target = "verification_engine"
        else:
            route_target = "research_agent"

        decision = {
            "resolved": False,
            "intent": intent,
            "domain": domain,
            "complexity": complexity,
            "confidence": confidence,
            "route_target": route_target,
            "latency_ms": 1.1
        }
        
        logger.info(f"[{self.layer_name}] Routed query to '{route_target}' with complexity {complexity}")
        return decision

    def execute_layer(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        res = self.execute(query, context)
        res["answer"] = f"[ROUTER] Target = {res['route_target']}"
        return res
