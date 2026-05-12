from typing import List, Optional

class HierarchicalRAG:
    """
    LAYER 4: HIERARCHICAL RAG
    Multi-tier retrieval (Exact -> Fuzzy -> Global)
    """
    def __init__(self):
        self.kb = ["HYPER uses CPU optimization for matrix math.", "Project HYPER handles 97% of requests via cache."]

    def retrieve(self, query: str, top_k: int = 2) -> List[str]:
        # Tier 1: Exact / Keyword (Simulated)
        # Tier 2: Fuzzy / Semantic (Simulated)
        return [context for context in self.kb if any(word in context.lower() for word in query.lower().split())]

    def build_context(self, chunks: List[str]) -> str:
        return "\n".join([f"Context {i}: {c}" for i, c in enumerate(chunks)])

hierarchical_rag = HierarchicalRAG()

