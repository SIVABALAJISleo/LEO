import time
from typing import Dict, Any
from app.core.config import settings

class CapabilityRouter:
    def __init__(self):
        self.metrics = {
            "requests_processed": 0,
            "compute_avoided_count": 0,
            "total_latency": 0,
            "cache_hits": 0,
            "retrieval_usage": 0,
            "prediction_usage": 0
        }

    async def route(self, query: str) -> Dict[str, Any]:
        """
        Routes the query based on intent.
        1. Classify Intent
        2. Detect if Prediction/Cache/Retrieval can solve it
        3. Dispatch to Module
        """
        start_time = time.time()
        self.metrics["requests_processed"] += 1
        
        # 1. SIMPLE INTENT CLASSIFICATION (Placeholder for Module 1 logic)
        intent = self._classify_intent(query)
        
        # 2. DISPATCH
        if intent == "RAG":
            response = await self._handle_rag(query)
            self.metrics["retrieval_usage"] += 1
        elif intent == "HYPOTHESIS":
            response = await self._handle_hypothesis(query)
            self.metrics["compute_avoided_count"] += 1
        elif intent == "DECISION":
            response = await self._handle_decision(query)
        elif intent == "PERCEPTUAL":
            response = await self._handle_perceptual(query)
            self.metrics["prediction_usage"] += 1
        else:
            response = {"answer": "Fallback: Standard Processing", "reasoning": "No specific intent detected."}

        latency = time.time() - start_time
        self.metrics["total_latency"] += latency
        
        # Standard Response Wrapper
        return {
            "answer": response.get("answer"),
            "reasoning": response.get("reasoning"),
            "confidence_score": response.get("confidence_score", 0.0),
            "data_sources": response.get("data_sources", []),
            "heavy_computation_avoided": response.get("heavy_computation_avoided", True),
            "latency_ms": round(latency * 1000, 2)
        }

    def _classify_intent(self, query: str) -> str:
        q = query.lower()
        if any(w in q for w in ["what", "who", "when", "how many"]): return "RAG"
        if any(w in q for w in ["hypothesis", "experiment", "test", "narrow"]): return "HYPOTHESIS"
        if any(w in q for w in ["decide", "option", "risk", "choice"]): return "DECISION"
        if any(w in q for w in ["render", "simulate", "visual", "predict"]): return "PERCEPTUAL"
        return "RAG"

    async def _handle_rag(self, query: str):
        from app.modules.intelligence import process_rag
        return await process_rag(query)

    async def _handle_hypothesis(self, query: str):
        from app.modules.hypothesis import process_hypothesis
        return await process_hypothesis(query)

    async def _handle_decision(self, query: str):
        from app.modules.decision import process_decision
        return await process_decision(query)

    async def _handle_perceptual(self, query: str):
        from app.modules.perceptual import process_perceptual
        return await process_perceptual(query)

    def get_metrics(self) -> Dict[str, Any]:
        avoidance_rate = (self.metrics["compute_avoided_count"] / self.metrics["requests_processed"]) if self.metrics["requests_processed"] > 0 else 0
        return {
            "total_requests": self.metrics["requests_processed"],
            "compute_avoidance_rate": round(avoidance_rate * 100, 2),
            "cache_hits": self.metrics["cache_hits"],
            "retrieval_usage": self.metrics["retrieval_usage"],
            "prediction_usage": self.metrics["prediction_usage"],
            "avg_latency_ms": round((self.metrics["total_latency"] / self.metrics["requests_processed"]) * 1000, 2) if self.metrics["requests_processed"] > 0 else 0
        }

orchestrator = CapabilityRouter()
