from .detector import detector, ComplexityLevel

class SmartRouter:
    """
    LAYER 2: SMART ROUTER
    Maps analysis results to execution paths.
    """
    def route(self, query: str) -> str:
        analysis = detector.analyze(query)
        level = analysis["level"]
        
        # Priority 1: SIMPLE -> Cache / Fast Path
        if level == ComplexityLevel.SIMPLE:
            return "PATH_CACHE_TINY"
        
        # Priority 2: MEDIUM -> RAG / Reasoned Path
        if level == ComplexityLevel.MEDIUM:
            return "PATH_RAG_MEDIUM"
            
        # Priority 3: HARD -> Speculative / Heavy Path
        if level == ComplexityLevel.HARD:
            return "PATH_HEAVY_ASYNC"
            
        # Priority 4: EXTREME -> Fallback Control
        return "PATH_FALLBACK_ANYTIME"

brain = SmartRouter()
吐
