import logging
from typing import List, Dict, Any, Optional, Tuple
from intel_core_ai.knowledge import IntelKnowledgeSystem

logger = logging.getLogger(__name__)

class VerifiedKnowledgeLayer(IntelKnowledgeSystem):
    """
    LAYER 3: KNOWLEDGE LAYER
    Ensures source grounding and consistency checks.
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        super().__init__(model_name)
        # Store metadata/sources mapping
        self.sources: Dict[int, str] = {}

    def seed_with_sources(self, data: List[Tuple[str, str]]):
        """
        data: List of (document, source_name)
        """
        docs = [d[0] for d in data]
        start_idx = len(self.documents)
        self.seed_knowledge(docs)
        for i, (doc, src) in enumerate(data):
            self.sources[start_idx + i] = src

    def retrieve_with_source(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        # Tiered retrieval with source mapping
        query_emb = self.encoder.encode([query], convert_to_tensor=False)
        self.encoder.encode # Warmup
        
        distances, indices = self.index.search(query_emb, 1)
        
        if indices[0][0] != -1 and distances[0][0] > 0.65:
            idx = indices[0][0]
            doc = self.documents[idx]
            source = self.sources.get(idx, "Unknown Source")
            return doc, source
            
        return None, None
