import time
import numpy as np
import re
from collections import Counter
from typing import Optional, Dict, List, Any

# --- Zero-Binary Hardening: Robust Numpy Implementation ---

class NumpyIndexL2:
    """Pure Numpy replacement for faiss.IndexFlatL2"""
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.vectors: List[np.ndarray] = []
        self.ntotal = 0

    def add(self, x: np.ndarray):
        # x is assumed to be (n, d)
        for vec in x:
            self.vectors.append(vec.flatten())
        self.ntotal = len(self.vectors)

    def search(self, query_vec: np.ndarray, k: int):
        if not self.vectors:
            return np.array([[1e9]]), np.array([[-1]])
        
        # Convert list to matrix for vectorized search
        data = np.stack(self.vectors)
        # L2 Distance: ||a-b||^2 = ||a||^2 + ||b||^2 - 2<a,b>
        # For simplicity and small scale, just use linalg.norm
        distances = np.linalg.norm(data - query_vec, axis=1)
        indices = np.argsort(distances)[:k]
        
        return distances[indices].reshape(1, -1), indices.reshape(1, -1)

class TFIDFLite:
    """Lightweight keyword-based similarity fallback for SentenceTransformer"""
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.stopwords = {"a", "an", "the", "is", "of", "to", "for", "in", "with"}
        
    def _tokenize(self, text: str) -> List[str]:
        return [w for w in re.findall(r'\w+', text.lower()) if w not in self.stopwords]

    def encode(self, texts: List[str]) -> np.ndarray:
        # Optimized Batch Projection: 
        # Pre-allocating matrix and using vectorized normalization
        n = len(texts)
        embeddings = np.zeros((n, self.dimension), dtype='float32')
        
        for i, text in enumerate(texts):
            tokens = self._tokenize(text)
            if not tokens:
                continue
                
            for token in tokens:
                seed = sum(ord(c) for c in token)
                rs = np.random.RandomState(seed % 4294967295)
                # Inplace addition to leverage memory locality
                embeddings[i] += rs.normal(0, 0.1, self.dimension)
        
        # Batch Normalization (L2) - SIMD-friendly loop
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        # Avoid division by zero
        safe_norms = np.where(norms > 0, norms, 1.0)
        embeddings /= safe_norms
            
        return embeddings

try:
    from sentence_transformers import SentenceTransformer
    HAS_TRANSFORMERS = True
except ImportError:
    SentenceTransformer = TFIDFLite
    HAS_TRANSFORMERS = False

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

# --- Intelligence Trace & Verification Layers ---

class HallucinationGuard:
    """Verifies that the generated answer is grounded in the retrieved context."""
    def __init__(self, model: Optional[Any] = None):
        self.model = model

    def verify(self, answer: str, context: List[str]) -> float:
        if not context:
            return 0.5 # Neutral if no context provided
        
        # Perceptual grounding check: 
        # In a real system, this would use an NLI model or cross-encoder.
        # Here we use a high-performance keyword overlap / semantic density check.
        answer_words = set(re.findall(r'\w+', answer.lower()))
        context_words = set(re.findall(r'\w+', " ".join(context).lower()))
        
        if not answer_words:
            return 0.0
            
        overlap = len(answer_words.intersection(context_words)) / len(answer_words)
        return float(min(1.0, overlap * 1.5)) # Scaled overlap

class ConfidenceScorer:
    """Calculates a confidence score based on retrieval depth and result similarity."""
    def calculate(self, distance: float, threshold: float) -> float:
        # Distance is L2; lower is better. 
        # Score = 1.0 (exact match) to 0.0 (at threshold)
        score = 1.0 - (distance / (1 - threshold + 1e-9))
        return float(max(0.0, min(1.0, score)))

class TraceEngine:
    """Provides a machine-readable trace of the decision process."""
    def __init__(self):
        self.trace: List[Dict[str, Any]] = []

    def add_step(self, module: str, action: str, metadata: Dict[str, Any]):
        self.trace.append({
            "timestamp": time.time(),
            "module": module,
            "action": action,
            "metadata": metadata
        })

    def get_full_trace(self) -> List[Dict[str, Any]]:
        return self.trace

class SemanticCache:
    def __init__(self, dimension: int = 384, threshold: float = 0.98):
        from backend.core.logging import logger as struct_logger
        self.logger = struct_logger
        self.model = SentenceTransformer('all-MiniLM-L6-v2') if HAS_TRANSFORMERS else TFIDFLite(dimension)
        if HAS_FAISS:
             self.index = faiss.IndexFlatL2(dimension)
        else:
             self.index = NumpyIndexL2(dimension)
        self.threshold = threshold
        # Redis-backed persistent storage for cache results
        from backend.core.middleware import redis_client
        self.redis = redis_client

    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves result from cache using tenant-aware key.
        Checks for exact hash hit first (fast), then semantic similarity (robust).
        """
        if not self.redis:
            return None

        # 1. Exact Hash Hit (Prompt Cache Bypass)
        exact_hit = self.redis.get(f"exact_cache:{cache_key}")
        if exact_hit:
            import json
            self.logger.info("semantic_cache_exact_hit", key=cache_key)
            return {"result": json.loads(exact_hit), "confidence": 1.0}

        # 2. Semantic Similarity Bypass
        if self.index.ntotal == 0:
            return None
        
        # We use a sub-string or hash for the actual vector storage reference
        query_vec = self.model.encode([cache_key]).astype('float32')
        distances, indices = self.index.search(query_vec, 1)
        
        distance = float(distances[0][0])
        if distance < (1 - self.threshold):
            idx = indices[0][0]
            # Retrieve from Redis using index as pointer
            result_json = self.redis.get(f"semantic_val:{idx}")
            if result_json:
                import json
                scorer = ConfidenceScorer()
                confidence = scorer.calculate(distance, self.threshold)
                self.logger.info("semantic_cache_similarity_hit", distance=distance, confidence=confidence)
                
                return {
                    "result": json.loads(result_json),
                    "confidence": confidence,
                    "distance": distance
                }
        return None

    def set(self, cache_key: str, result: Any):
        """Stores result with exact and semantic indexing."""
        if not self.redis:
            return

        import json
        result_json = json.dumps(result)
        
        # 1. Store exact hash
        self.redis.set(f"exact_cache:{cache_key}", result_json, ex=86400) # 24h

        # 2. Add to semantic index
        query_vec = self.model.encode([cache_key]).astype('float32')
        idx = self.index.ntotal
        self.index.add(query_vec)
        self.redis.set(f"semantic_val:{idx}", result_json, ex=86400)
        
        self.logger.info("semantic_cache_stored", key=cache_key, index_size=self.index.ntotal)

class MoERouter:
    """Mixture of Experts Router to dispatch tasks based on intent."""
    def __init__(self):
        self.experts = {
            "code": "CodeExpert",
            "reasoning": "ReasoningExpert",
            "creative": "CreativeExpert",
            "security": "SecurityExpert"
        }
        self.trace = TraceEngine()

    def route(self, query: str) -> Dict[str, Any]:
        q = query.lower()
        intent = "reasoning" # Default
        confidence = 0.8
        
        if any(w in q for w in ["calculate", "math", "+", "-", "*", "/", "sqrt"]):
            intent = "reasoning" # In a real system, this would route to a PythonInterpreterExpert
            confidence = 1.0
        elif any(w in q for w in ["document", "file", "search", "find", "paper"]):
            intent = "reasoning" # Trigger RAG context
            confidence = 0.9
        elif any(w in q for w in ["python", "js", "code", "function", "api"]):
            intent = "code"
        elif any(w in q for w in ["why", "how", "solve", "logic"]):
            intent = "reasoning"
        elif any(w in q for w in ["write", "story", "poem", "imagine"]):
            intent = "creative"
        elif any(w in q for w in ["firewall", "leak", "secure", "exploit"]):
            intent = "security"
            confidence = 1.0 # Explicit security intent
            
        self.trace.add_step("MoERouter", "intent_detection", {"query": query, "intent": intent, "confidence": confidence})
        
        return {
            "intent": intent,
            "confidence": confidence,
            "expert": self.experts[intent],
            "trace": self.trace.get_full_trace()
        }
