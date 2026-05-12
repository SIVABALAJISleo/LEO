from typing import Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class IntentLayer:
    """
    LAYER 2: INTENT + CONFIDENCE LAYER
    - Lightweight semantic model (sentence-transformers).
    - Output: {intent, confidence score}.
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dim)
        self.intents = []
        self.threshold = 0.85

    def register_intents(self, intent_map: Dict[str, str]):
        """intent_map: {intent_id: canonical_phrase}"""
        self.intents = list(intent_map.keys())
        phrases = list(intent_map.values())
        embeddings = self.model.encode(phrases, convert_to_tensor=False)
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)

    def determine_intent(self, query: str) -> Dict[str, Any]:
        if not self.intents:
            return {"status": "error", "message": "No intents registered"}

        query_emb = self.model.encode([query], convert_to_tensor=False)
        faiss.normalize_L2(query_emb)
        
        distances, indices = self.index.search(query_emb, 1)
        score = float(distances[0][0])
        best_intent = self.intents[indices[0][0]]

        result = {
            "intent": best_intent,
            "confidence": score
        }

        if score < self.threshold:
            result["status"] = "clarify"
            result["message"] = f"Did you mean to '{best_intent}'? (Confidence: {score:.2f})"
        else:
            result["status"] = "proceed"

        return result
