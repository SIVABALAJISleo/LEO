import logging
import faiss
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class OSMemory:
    """
    LAYER 3: CONTEXT MEMORY (RAM)
    Maintains a structured scratchpad for the current session.
    """
    def __init__(self):
        self.scratchpad: Dict[str, Any] = {
            "goal": "",
            "steps": [],
            "intermediate_results": []
        }

    def reset(self):
        self.scratchpad = {"goal": "", "steps": [], "intermediate_results": []}

    def get_context_ram(self) -> str:
        res = "--- CONTEXT RAM (SCRATCHPAD) ---\n"
        res += f"[GOAL]: {self.scratchpad['goal']}\n"
        for i, step in enumerate(self.scratchpad['steps']):
            res += f"[STEP {i+1}]: {step}\n"
            if i < len(self.scratchpad['intermediate_results']):
                res += f"[RESULT {i+1}]: {self.scratchpad['intermediate_results'][i]}\n"
        return res

class OSKnowledge:
    """
    LAYER 4: RAG SYSTEM
    Knowledge retrieval using FAISS.
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.encoder = SentenceTransformer(model_name)
        self.dim = self.encoder.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dim)
        self.documents: List[str] = []

    def add_docs(self, docs: List[str]):
        if not docs: return
        embs = self.encoder.encode(docs, convert_to_tensor=False)
        faiss.normalize_L2(embs)
        self.index.add(np.array(embs).astype('float32'))
        self.documents.extend(docs)

    def retrieve(self, query: str, k: int = 2) -> List[str]:
        query_emb = self.encoder.encode([query], convert_to_tensor=False)
        faiss.normalize_L2(query_emb)
        dists, indices = self.index.search(np.array(query_emb).astype('float32'), k)
        results = [self.documents[i] for i in indices[0] if i != -1]
        return results
