from .hardness import hardness_detector, ComplexityLevel

class AdaptiveRouter:
    """
    LAYER 2: ADAPTIVE ROUTER
    Determines execution path based on complexity and latency budget.
    """
    def route(self, query: str, budget_ms: int = 500) -> str:
        analysis = hardness_detector.analyze(query)
        level = analysis["level"]
        
        # Rule-based routing
        if level == ComplexityLevel.SIMPLE:
            return "PATH_CACHE_TINY"
        
        if level == ComplexityLevel.MEDIUM:
            return "PATH_RAG_QUANTIZED"
            
        # HARD or low budget for complex query → Async path
        return "PATH_ASYNC_HEAVY"

adaptive_router = AdaptiveRouter()

