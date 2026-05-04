from .hardness import QueryHardness, detector

class SmartRouter:
    """
    INTELLIGENT BRAIN: Routes based on hardness classification.
    Implements work-reduction by avoiding unnecessary high-compute tiers.
    """
    def route(self, query: str) -> str:
        hardness = detector.audit(query)
        
        # [TIER 1] SIMPLE -> Cache Bypass / Lookup
        if hardness == QueryHardness.SIMPLE:
            return "PATH_FAST_CACHE"
        
        # [TIER 2] MEDIUM -> RAG / Tiny-Med Hybrid
        if hardness == QueryHardness.MEDIUM:
            return "PATH_REASONED_RAG"
            
        # [TIER 3] HARD -> Async Heavy Pipeline
        return "PATH_ASYNC_HEAVY"

# Singleton instance
router = SmartRouter()
吐
