import os
import logging
import numpy as np
import re
from typing import List, Dict, Any, Optional
try:
    from rank_bm25 import BM25Okapi # type: ignore
    HAS_BM25 = True
except ImportError:
    HAS_BM25 = False

logger = logging.getLogger(__name__)

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
                rs = np.random.RandomState(seed % 4294967295) # nosec B311
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

class FakeSentenceTransformer:
    def __init__(self, model_name: str = ""):
        self._impl = TFIDFLite()
    def encode(self, texts: List[str]) -> np.ndarray:
        return self._impl.encode(texts)

try:
    from sentence_transformers import SentenceTransformer
    HAS_TRANSFORMERS = True
except ImportError:
    SentenceTransformer = FakeSentenceTransformer
    HAS_TRANSFORMERS = False

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

class VectorDBAdapter:
    """
    SaaS Scale Adapter:
    Abstracts index storage to allow swapping FAISS with Qdrant, Milvus, or Weaviate.
    """
    def __init__(self, mode: str = "local", dimension: int = 384, persist_dir: str = "rag_data"):
        self.mode = mode
        self.dimension = dimension
        self.persist_dir = persist_dir
        self.index_path = os.path.join(persist_dir, "faiss.index")
        
        if mode == "local":
            if HAS_FAISS:
                self.index = faiss.IndexFlatIP(dimension)
            else:
                self.index = NumpyIndexIP(dimension)
        else:
            # Placeholder for remote vector DB client (Qdrant/Milvus)
            self.index = NumpyIndexIP(dimension) # Fallback if remote fails initialization
        self.index: Any = self.index # Type hint to satisfy pyright
    def add(self, embeddings: np.ndarray):
        if self.mode == "local":
            self.index.add(embeddings.astype('float32')) # type: ignore
        else:
            # push to remote Qdrant/Milvus cluster
            pass

    def search(self, query_vec: np.ndarray, k: int):
        if self.mode == "local":
            return self.index.search(query_vec, k=k) # type: ignore
        else:
            # query remote cluster
            return np.array([[]]), np.array([[]])

    def save(self):
        if self.mode == "local" and HAS_FAISS:
            faiss.write_index(self.index, self.index_path)

    def load(self):
        if self.mode == "local" and os.path.exists(self.index_path) and HAS_FAISS:
            return faiss.read_index(self.index_path)
        return None

class RAGEngine:
    def __init__(self, dimension: int = 384, persist_dir: str = "rag_data"):
        self.persist_dir = persist_dir
        self.docs_path = os.path.join(persist_dir, "documents.json")
        if os.getenv("LEO_OFFLINE", "0") == "1" or os.getenv("TRANSFORMERS_OFFLINE", "0") == "1":
            logger.info("RAGEngine: Running in offline mode - using FakeSentenceTransformer.")
            self.model = FakeSentenceTransformer()
        else:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                logger.warning(f"RAGEngine: SentenceTransformer unavailable ({e}). Falling back to FakeSentenceTransformer.")
                self.model = FakeSentenceTransformer()
        
        # Select storage mode: 'local' (FAISS) or 'distributed' (Qdrant/Milvus)
        db_mode = os.getenv("VECTOR_DB_MODE", "local")
        self.db = VectorDBAdapter(mode=db_mode, dimension=dimension, persist_dir=persist_dir)
        self.index = self.db.index # Maintain compatibility
        
        self.documents: List[Dict[str, Any]] = []
        self.bm25: Optional[BM25Okapi] = None
        self.load()
        self._update_bm25()

    def _update_bm25(self):
        """Initializes/Updates the BM25 index with current documents."""
        if not HAS_BM25 or not self.documents:
            return
        tokenized_docs = [re.findall(r'\w+', doc["content"].lower()) for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_docs)

    def expand_query(self, query: str) -> List[str]:
        """Generates simple query variants to improve recall."""
        # In a hyperscale system, this would use a small LLM or synonym map.
        # For now, we use a heuristic approach.
        variants = [query]
        if "best" not in query.lower():
            variants.append(query + " best practices")
        if "how" not in query.lower():
            variants.append(f"how to {query}")
        return list(set(variants))

    async def add_documents(self, docs: List[str], tenant_id: str = "default"):
        """Ingests and indexes documents with tenant isolation and chunking."""
        from backend.security.prompt_guard import global_prompt_guard
        
        processed_docs = []
        for doc in docs:
            # RAG Memory Poisoning Defense: Scan document
            security_result = global_prompt_guard.check_document(doc, f"rag_ingest_{tenant_id}")
            if not security_result["is_safe"]:
                logger.warning(f"RAG Poisoning Detected! Dropping document for tenant {tenant_id}. Threats: {security_result['threats']}")
                continue

            # Simple chunking for documents > 2000 chars
            if len(doc) > 2000:
                chunks = [doc[i:i+2000] for i in range(0, len(doc), 1500)] # 500 char overlap
                for chunk in chunks:
                    processed_docs.append({"content": chunk, "tenant_id": tenant_id})
            else:
                processed_docs.append({"content": doc, "tenant_id": tenant_id})

        embeddings = np.asarray(self.model.encode([d["content"] for d in processed_docs]))
        logger.info(f"documents_indexed: count={len(docs)} tenant={tenant_id}")
        
        self.db.add(embeddings)
        self.documents.extend(processed_docs)
        self._update_bm25()
        self.save()

    def save(self):
        """Persists using the adapter and JSON store."""
        if not os.path.exists(self.persist_dir):
            os.makedirs(self.persist_dir)
            
        import json
        self.db.save()
        
        with open(self.docs_path, "w", encoding="utf-8") as f:
            json.dump(self.documents, f)

    def load(self):
        """Loads via the adapter and JSON store."""
        import json
        if os.path.exists(self.docs_path):
            try:
                loaded_index = self.db.load()
                if loaded_index:
                    self.index = loaded_index
                
                with open(self.docs_path, "r", encoding="utf-8") as f:
                    self.documents = json.load(f)
            except Exception as e:
                print(f"Error loading RAG persistence: {e}")

    def retrieve(self, query: str, tenant_id: str = "default", k: int = 3, runtime_fast: bool = False) -> List[Dict[str, Any]]:
        """Retrieves and filters by tenant using Hybrid Search (BM25 + Vector)."""
        if not self.documents:
            return []
        
        from backend.core.middleware import redis_client # type: ignore
        import json
        import numpy as np
        
        # 1. QUERY EXPANSION (Conditional)
        queries = [query] if runtime_fast else self.expand_query(query)
        
        # 2. VECTOR SEARCH (Multi-query fusion)
        all_vec_hits = {}
        for q in queries:
            query_hash = str(hash(q))
            cache_key = f"embed_cache:{tenant_id}:{query_hash}"
            cached_vec = redis_client.get(cache_key) if redis_client else None
            
            if cached_vec:
                try:
                    # cached_vec might be string or bytes
                    data = json.loads(cached_vec) if isinstance(cached_vec, (str, bytes)) else cached_vec
                    query_vec = np.asarray(data).astype('float32')
                except:
                    query_vec = np.asarray(self.model.encode([q])).astype('float32').reshape(1, -1)
            else:
                query_vec = np.asarray(self.model.encode([q])).astype('float32').reshape(1, -1)
                if redis_client:
                    redis_client.set(cache_key, json.dumps(query_vec.tolist()), ex=3600)
            
            distances, indices = self.db.search(query_vec, k * 3)
            for i, idx in enumerate(indices[0]):
                if idx != -1 and idx < len(self.documents):
                    score = float(distances[0][i])
                    all_vec_hits[idx] = max(all_vec_hits.get(idx, 0), score)

        # 3. BM25 KEYWORD SEARCH (Keyword Overlap)
        bm25_hits = {}
        if self.bm25:
            tokenized_query = re.findall(r'\w+', query.lower())
            bm25_scores = self.bm25.get_scores(tokenized_query)
            # Normalize BM25 scores roughly to 0-1
            max_bm25 = max(bm25_scores) if len(bm25_scores) > 0 else 1.0
            if max_bm25 > 0:
                for i, score in enumerate(bm25_scores):
                    if score > 0:
                         bm25_hits[i] = score / max_bm25

        # 4. HYBRID FUSION (60% Vector, 40% BM25)
        combined_results = []
        all_indices = set(all_vec_hits.keys()).union(set(bm25_hits.keys()))
        
        for idx in all_indices:
             doc_meta = self.documents[idx]
             if doc_meta.get("tenant_id") == tenant_id:
                 vec_score = all_vec_hits.get(idx, 0)
                 keyword_score = bm25_hits.get(idx, 0)
                 final_score = (0.6 * vec_score) + (0.4 * keyword_score)
                 combined_results.append({
                     "content": doc_meta["content"],
                     "score": final_score,
                     "metadata": {"hybrid_rank": final_score}
                 })

        # Sort combined results by score
        combined_results.sort(key=lambda x: x['score'], reverse=True)

        # 5. FAST-PATH: Skip reranking if initial match is extremely strong (>0.95)
        top_score = combined_results[0]['score'] if combined_results else 0
        if top_score > 0.95:
            logger.info(f"rag_fast_path_triggered [score={top_score:.3f}]")
            return combined_results[:k]

        # 6. PRECISION RERANKING (Final Pass)
        if runtime_fast:
             return combined_results[:k]

        from backend.intelligence.reranker import global_reranker # type: ignore
        reranked_results = global_reranker.rerank(query, combined_results, top_k=k)
        
        return reranked_results
global_rag_engine = RAGEngine()

# Cache invalidation trigger
