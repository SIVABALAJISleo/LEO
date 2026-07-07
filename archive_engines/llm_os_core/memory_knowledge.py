import logging
import faiss
import numpy as np
import time
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class AdvancedOSMemory:
    """
    [ARCHITECTURE POINT 6: FEEDBACK LOOP]
    Captures multi-signal feedback and applies weighted scoring.
    """
    def __init__(self):
        self.scratchpad: Dict[str, Any] = {
            "goal": "",
            "steps": [],
            "intermediate_results": [],
            "signals": [] # Store implicit/explicit signals
        }
        self.blacklisted_routes: List[str] = [] # Point 7

    def capture_feedback(self, query: str, route: str, signals: Dict[str, Any]):
        """
        [6] Weighted scoring: explicit > implicit.
        [7] Blacklist detection.
        """
        score = 0.0
        # Explicit signals (High weight)
        if signals.get("thumbs_up"): score += 1.0
        if signals.get("thumbs_down"): score -= 1.5
        if signals.get("correction"): score -= 1.0
        
        # Implicit signals (Low weight)
        if signals.get("copy"): score += 0.2
        if signals.get("dwell_time", 0) > 30: score += 0.1
        
        signal_entry = {"q": query, "r": route, "score": score, "t": time.time()}
        self.scratchpad["signals"].append(signal_entry)
        
        # Check for blacklisting (Point 7)
        if score < -1.0:
            failures = [s for s in self.scratchpad["signals"] if s["r"] == route and s["score"] < 0]
            if len(failures) >= 3:
                logger.warning(f"BLACKLISTING ROUTE: {route} due to repeated failures.")
                self.blacklisted_routes.append(route)

class SemanticCache:
    """
    [ARCHITECTURE POINT 9: SEMANTIC CACHE]
    Vector similarity ≥ 0.95 → reuse output.
    """
    def __init__(self, encoder: SentenceTransformer):
        self.encoder = encoder
        self.dim = self.encoder.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dim)
        self.cache_entries: List[Dict[str, Any]] = []

    def check(self, query: str) -> Optional[Dict[str, Any]]:
        if self.index.ntotal == 0: return None
        
        emb = self.encoder.encode([query], convert_to_tensor=False)
        faiss.normalize_L2(emb)
        dists, indices = self.index.search(np.array(emb).astype('float32'), 1)
        
        similarity = dists[0][0]
        if similarity >= 0.95:
            logger.info(f"CACHE HIT: Similarity {similarity:.4f}")
            return self.cache_entries[indices[0][0]]
        return None

    def store(self, query: str, response: Dict[str, Any]):
        emb = self.encoder.encode([query], convert_to_tensor=False)
        faiss.normalize_L2(emb)
        self.index.add(np.array(emb).astype('float32'))
        self.cache_entries.append({"q": query, "ans": response})

class AdvancedOSKnowledge:
    """
    [ARCHITECTURE POINT 4 & 7: VERIFICATION + SELF-IMPROVEMENT]
    RAG system with support for guardrails and failure storage.
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.encoder = SentenceTransformer(model_name)
        self.dim = self.encoder.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dim)
        self.documents: List[str] = []
        self.cache = SemanticCache(self.encoder)
        self.failure_log: List[Dict[str, Any]] = [] # Point 7

    def retrieve(self, query: str, k: int = 2) -> List[str]:
        if self.index.ntotal == 0: return []
        query_emb = self.encoder.encode([query], convert_to_tensor=False)
        faiss.normalize_L2(query_emb)
        dists, indices = self.index.search(np.array(query_emb).astype('float32'), k)
        return [self.documents[i] for i in indices[0] if i != -1]

    def add_docs(self, docs: List[str]):
        if not docs: return
        embs = self.encoder.encode(docs, convert_to_tensor=False)
        faiss.normalize_L2(embs)
        self.index.add(np.array(embs).astype('float32'))
        self.documents.extend(docs)
