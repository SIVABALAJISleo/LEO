from typing import Dict, Any
from archive_engines.hyper_optimized_ai.config import settings

class RealityFilter:
    """
    2. REALITY FILTER (NO-GUESS ENGINE)
    - Use RAG (vector DB + APIs + tools)
    - Cross-check sources
    - Compute confidence = agreement + recency + reliability
    - If confidence < 0.7 -> BLOCK execution and request missing data
    """
    def __init__(self, rag_service):
        self.rag = rag_service

    async def validate_execution(self, intent: str, action_plan: str) -> Dict[str, Any]:
        # 1. Fetch RAG data
        sources = await self.rag.rag_search(action_plan)
        
        if not sources:
            # No grounding found
            return {
                "valid": False,
                "confidence": 0.0,
                "reason": "No reality grounding found for this query.",
                "missing_data": ["Primary knowledge source"]
            }

        # 2. Cross-check logic
        # In a real system, we'd use a small model to check agreement between action_plan and sources
        # For this demo, we simulate the logic
        
        # Agreement: How much do sources support the action_plan?
        agreement = 0.9 if any(intent in s["text"].lower() for s in sources) else 0.5
        
        # Recency: Average recency of sources
        recency = sum(s.get("recency", 0.5) for s in sources) / len(sources)
        
        # Reliability: Average reliability (mocked as 0.85 for internal sources)
        reliability = 0.85 
        
        # Weighted Confidence
        confidence = (
            agreement * settings.CONFIDENCE_WEIGHT_AGREEMENT +
            recency * settings.CONFIDENCE_WEIGHT_RECENCY +
            reliability * settings.CONFIDENCE_WEIGHT_RELIABILITY
        )
        
        if confidence < settings.REALITY_FILTER_CONFIDENCE_THRESHOLD:
            return {
                "valid": False,
                "confidence": confidence,
                "reason": "Insufficient certainty from reality filter. Sources disagree or data is stale.",
                "missing_data": ["Verified hardware specs", "Fresh API docs"]
            }
            
        return {
            "valid": True,
            "confidence": confidence,
            "sources": [s["text"] for s in sources]
        }
