from project_hyper.cache import CacheFirstLayer
from project_hyper.router import QueryRouter
from project_hyper.rag import RetrievalEngine
from project_hyper.compute import ComputeEngine
from project_hyper.tools import ToolExecutionLayer
from project_hyper.reasoning import ReasoningEngine
from project_hyper.uncertainty import UncertaintyHandler

class ProjectLEOZeroGPU:
    """MASTER ORCHESTRATOR FOR ZERO-GPU HYPER SYSTEM"""
    def __init__(self):
        self.cache = CacheFirstLayer()
        self.router = QueryRouter()
        self.rag = RetrievalEngine()
        self.compute = ComputeEngine()
        self.tools = ToolExecutionLayer()
        self.reasoning = ReasoningEngine(self.compute)
        self.uncertainty = UncertaintyHandler()

    def process_query(self, query: str):
        # Layer 0: Cache
        cached_res = self.cache.check_cache(query)
        if cached_res:
            return f"[L0 CACHE HIT] {cached_res}"
            
        # Layer 1: Routing
        route = self.router.classify(query)
        
        # Layer 4: Exact Tools Bypass
        if route == "high-precision":
            res = self.tools.execute(query)
            self.cache.add_to_cache(query, res)
            return f"[L4 TOOL BYPASS] {res}"
            
        # Layer 2: RAG Context
        context = ""
        if route == "retrieval-based" or route == "reasoning":
            context = self.rag.retrieve(query)
            
        # Layer 5: Reasoning vs Layer 3: Direct Compute
        if route == "reasoning":
            raw_res = self.reasoning.self_consistency(query, context)
        else:
            raw_res = self.compute.generate(query, context)
            
        # Layer 8: Uncertainty Scoring
        conf = self.uncertainty.evaluate(raw_res)
        final_res = self.uncertainty.handle(raw_res, conf)
        
        # Cache successful high-confidence responses
        if conf >= 0.8:
            self.cache.add_to_cache(query, final_res)
            
        return final_res

if __name__ == "__main__":
    leo = ProjectLEOZeroGPU()
    print(leo.process_query("What is 1+1?"))
    print(leo.process_query("Explain quantum computing."))
