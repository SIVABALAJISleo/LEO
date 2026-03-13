import numpy as np
import re
from typing import List, Dict, Any

# --- Zero-Binary Hardening: Robust Numpy Implementation ---

class NumpyIndexIP:
    """Pure Numpy replacement for faiss.IndexFlatIP (Inner Product)"""
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
            return np.array([[0.0]]), np.array([[-1]])
        
        data = np.stack(self.vectors)
        # Inner Product for Cosine Similarity (assuming input is normalized)
        scores = np.dot(data, query_vec.T).flatten()
        indices = np.argsort(scores)[::-1][:k]
        
        return scores[indices].reshape(1, -1), indices.reshape(1, -1)

class TFIDFLite:
    """Lightweight keyword-based similarity fallback for SentenceTransformer"""
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.stopwords = {"a", "an", "the", "is", "of", "to", "for", "in", "with"}
        
    def _tokenize(self, text: str) -> List[str]:
        return [w for w in re.findall(r'\w+', text.lower()) if w not in self.stopwords]

    def encode(self, texts: List[str]) -> np.ndarray:
        embeddings = []
        for text in texts:
            vec = np.zeros(self.dimension, dtype='float32')
            tokens = self._tokenize(text)
            if not tokens:
                embeddings.append(vec)
                continue
                
            for token in tokens:
                seed = sum(ord(c) for c in token)
                rs = np.random.RandomState(seed % 4294967295)
                vec += rs.normal(0, 0.1, self.dimension)
            
            # Normalize for Inner Product (Cosine Similarity)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec /= norm
            embeddings.append(vec)
            
        return np.array(embeddings)

def normalize_L2(x: np.ndarray):
    norm = np.linalg.norm(x, axis=1, keepdims=True)
    mask = (norm > 0).flatten()
    if np.any(mask):
        x[mask] /= norm[mask]
    return x

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

class RAGEngine:
    def __init__(self, dimension: int = 384, persist_dir: str = "rag_data"):
        self.persist_dir = persist_dir
        self.index_path = os.path.join(persist_dir, "faiss.index")
        self.docs_path = os.path.join(persist_dir, "documents.json")
        
        self.model = SentenceTransformer('all-MiniLM-L6-v2') if HAS_TRANSFORMERS else TFIDFLite(dimension)
        
        if HAS_FAISS:
             self.index = faiss.IndexFlatIP(dimension)
        else:
             self.index = NumpyIndexIP(dimension)
        
        self.documents = []
        
        # Auto-load if exists
        self.load()

    async def add_documents(self, docs: List[str], tenant_id: str = "default"):
        """Ingests and indexes documents with tenant isolation and chunking."""
        processed_docs = []
        for doc in docs:
            # Simple chunking for documents > 2000 chars
            if len(doc) > 2000:
                chunks = [doc[i:i+2000] for i in range(0, len(doc), 1500)] # 500 char overlap
                for chunk in chunks:
                    processed_docs.append({"content": chunk, "tenant_id": tenant_id})
            else:
                processed_docs.append({"content": doc, "tenant_id": tenant_id})

        embeddings = self.model.encode([d["content"] for d in processed_docs])
        from backend.core.logging import logger as struct_logger
        struct_logger.info("documents_indexed", count=len(docs), tenant_id=tenant_id)
        
        if HAS_FAISS:
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings.astype('float32'))
        else:
            normalize_L2(embeddings)
            self.index.add(embeddings.astype('float32'))
        self.documents.extend(processed_docs)
        
        # Persist after addition
        self.save()

    def save(self):
        """Persists the index and documents to disk with tenant metadata."""
        if not os.path.exists(self.persist_dir):
            os.makedirs(self.persist_dir)
            
        import json
        if HAS_FAISS:
            faiss.write_index(self.index, self.index_path)
        
        # Consistent JSON storage for documents across all tenants
        with open(self.docs_path, "w", encoding="utf-8") as f:
            json.dump(self.documents, f)

    def load(self):
        """Loads index and documents from disk."""
        import json
        if os.path.exists(self.index_path) and os.path.exists(self.docs_path):
            try:
                if HAS_FAISS:
                    self.index = faiss.read_index(self.index_path)
                
                with open(self.docs_path, "r", encoding="utf-8") as f:
                    self.documents = json.load(f)
            except Exception as e:
                print(f"Error loading RAG persistence: {e}")

    def retrieve(self, query: str, tenant_id: str = "default", k: int = 3) -> List[Dict[str, Any]]:
        """Retrieves documents for a specific query, strictly filtered by tenant_id."""
        if self.index.ntotal == 0:
            return []
        
        from backend.core.middleware import redis_client
        import json
        import numpy as np
        
        # 1. Check Embedding Cache (Compute Bypass - Cache per Tenant for security)
        query_hash = str(hash(query))
        cache_key = f"embed_cache:{tenant_id}:{query_hash}"
        cached_vec = redis_client.get(cache_key) if redis_client else None
        
        if cached_vec:
            query_vec = np.array(json.loads(cached_vec)).astype('float32')
        else:
            query_vec = self.model.encode([query]).astype('float32')
            if HAS_FAISS:
                faiss.normalize_L2(query_vec)
            else:
                normalize_L2(query_vec)
            
            # 2. Store in Cache for 1 hour
            if redis_client:
                redis_client.set(cache_key, json.dumps(query_vec.tolist()), ex=3600)
            
        # We search for k*3 to allow for filtering of non-tenant documents
        # In a massive scale scenario, we'd use partitioned indices or FAISS ID tags.
        search_k = min(self.index.ntotal, k * 5)
        distances, indices = self.index.search(query_vec, search_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.documents):
                doc_meta = self.documents[idx]
                
                # STRICT TENANT ISOLATION CHECK
                if doc_meta.get("tenant_id") == tenant_id:
                    score = float(distances[0][i])
                    results.append({
                        "content": doc_meta["content"],
                        "score": score
                    })
                    if len(results) >= k:
                        break
        return results
