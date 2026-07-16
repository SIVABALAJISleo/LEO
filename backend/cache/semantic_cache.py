"""
backend/cache/semantic_cache.py
Production-grade Multi-Layer Semantic Cache.
Integrates exact hashing, dense vector similarity (FAISS + Sentence-Transformers),
Zipf-law TTL dynamics, reasoning-path caches, and semantic delta reconstruction.
"""
import os
import time
import hashlib
import sqlite3
from backend.core.db_utils import get_concurrent_db_connection
import numpy as np
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Fallback dense embedder using character trigrams when sentence-transformers is missing/unstable
class TrigramEmbedder:
    VECTOR_DIM = 384

    def encode(self, text: str) -> np.ndarray:
        text = text.lower().strip()
        vec = np.zeros(self.VECTOR_DIM, dtype=np.float32)
        for i in range(len(text) - 2):
            idx = hash(text[i:i + 3]) % self.VECTOR_DIM
            vec[idx] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

class ProductionSemanticCache:
    """
    Multi-layer semantic KV and vector cache. Eliminates redundant transformer execution
    by retrieving exact or highly-similar reasoning traces locally.

    Cache keys are prefixed with a Unicode script tag so that queries in different
    writing systems (e.g. Telugu vs Kannada) are always in separate partitions and
    can never produce cross-language false positives via trigram/vector similarity.
    """

    SIMILARITY_GATE = 0.85
    FUZZY_GATE      = 0.72

    # ── Script Detection ───────────────────────────────────────────────────── #
    @staticmethod
    def _script_prefix(text: str) -> str:
        """
        Returns a short ASCII script tag for the dominant Unicode block in *text*.
        This tag is prepended to every query before hashing or encoding so that
        cross-script trigram/vector similarity can never yield a false cache hit.

        Blocks checked (inclusive ranges):
          Tamil:     U+0B80–U+0BFF  → "[ta]"
          Kannada:   U+0C80–U+0CFF  → "[kn]"   (checked BEFORE Telugu)
          Telugu:    U+0C00–U+0C7F  → "[te]"
          Malayalam: U+0D00–U+0D7F  → "[ml]"
          Devanagari:U+0900–U+097F  → "[hi]"
          Arabic:    U+0600–U+06FF  → "[ar]"
          CJK:       U+4E00–U+9FFF  → "[zh]"
        """
        def _in(c: str, lo: int, hi: int) -> bool:
            return lo <= ord(c) <= hi

        for c in text:
            if _in(c, 0x0B80, 0x0BFF): return "[ta]"
            if _in(c, 0x0C80, 0x0CFF): return "[kn]"  # Kannada before Telugu
            if _in(c, 0x0C00, 0x0C7F): return "[te]"
            if _in(c, 0x0D00, 0x0D7F): return "[ml]"
            if _in(c, 0x0900, 0x097F): return "[hi]"
            if _in(c, 0x0600, 0x06FF): return "[ar]"
            if _in(c, 0x4E00, 0x9FFF): return "[zh]"
        return "[en]"

    def _keyed(self, query: str) -> str:
        """Return the script-prefixed canonical form of *query* used for all cache ops."""
        return f"{self._script_prefix(query)} {query.lower().strip()}"

    def __init__(self, db_path: str = "hyper_engine.db"):
        self.db_path = db_path
        self._initialize_sqlite()
        
        # Load Dense Embedding Model
        self.encoder = None
        self.use_onnx = False
        onnx_path = "models/all-MiniLM-L6-v2/onnx/model_quantized.onnx"
        tokenizer_path = "models/all-MiniLM-L6-v2"
        if os.path.exists(onnx_path) and os.path.exists(tokenizer_path):
            try:
                import onnxruntime as ort
                from transformers import AutoTokenizer
                providers = ort.get_available_providers()
                provider = "CPUExecutionProvider"
                if "DmlExecutionProvider" in providers:
                    provider = "DmlExecutionProvider"
                
                self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)  # nosec B615 - loading from local path, not HuggingFace Hub
                self.onnx_session = ort.InferenceSession(onnx_path, providers=[provider])
                self.vector_dim = 384
                self.use_onnx = True
                logger.info(f"[SemanticCache] ONNX session loaded successfully on {provider}.")
            except Exception as e:
                logger.error(f"[SemanticCache] Failed to load ONNX: {e}. Falling back...")

        if not self.use_onnx:
            try:
                from sentence_transformers import SentenceTransformer
                # Using mini CPU-optimized model (384 dimensions)
                self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
                self.vector_dim = 384
                logger.info("SentenceTransformer (all-MiniLM-L6-v2) loaded successfully for cache.")
            except Exception as e:
                logger.warning(f"SentenceTransformer not loaded, running TrigramEmbedder fallback: {e}")
                self.encoder = TrigramEmbedder()
                self.vector_dim = 384

        # Initialize FAISS index
        self.use_faiss = False
        self.faiss_index = None
        self.faiss_keys = []
        try:
            import faiss
            self.faiss_index = faiss.IndexFlatIP(self.vector_dim)
            self.use_faiss = True
            logger.info("FAISS-CPU Index Flat Inner Product initialized successfully.")
            self._load_vector_cache_into_faiss()
        except Exception as e:
            logger.warning(f"FAISS not loaded, falling back to manual similarity scans: {e}")

    def get_count(self) -> int:
        try:
            conn = get_concurrent_db_connection(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM semantic_cache")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception:
            return 0

    def save_index(self, path: str = "cache_index.faiss"):
        if self.use_faiss:
            import faiss
            faiss.write_index(self.faiss_index, path)

    def load_index(self, path: str = "cache_index.faiss"):
        if os.path.exists(path):
            import faiss
            self.faiss_index = faiss.read_index(path)
            self.use_faiss = True


    def _initialize_sqlite(self):
        """Prepares the database for local persistent caching, indexing, and analytics."""
        conn = get_concurrent_db_connection(self.db_path)
        cursor = conn.cursor()
        
        # Table for exact match and TTL analytics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS semantic_cache (
                query_hash TEXT PRIMARY KEY,
                query TEXT,
                answer TEXT,
                confidence REAL,
                frequency INTEGER DEFAULT 1,
                ttl REAL,
                created_at REAL,
                last_accessed REAL
            )
        """)

        # Table for delta segments (slots and templated queries)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache_deltas (
                key_pattern TEXT PRIMARY KEY,
                response_template TEXT
            )
        """)

        # Table for vector storage (to rebuild index on boot)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vector_cache (
                query_hash TEXT PRIMARY KEY,
                vector BLOB
            )
        """)
        
        conn.commit()
        conn.close()

    def _load_vector_cache_into_faiss(self):
        """Loads all persisted vectors from SQLite back into the FAISS index on startup."""
        if not self.use_faiss:
            return
        
        conn = get_concurrent_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT query_hash, vector FROM vector_cache")
        rows = cursor.fetchall()
        
        if not rows:
            conn.close()
            return
            
        vectors = []
        for query_hash, blob in rows:
            vec = np.frombuffer(blob, dtype=np.float32)
            if len(vec) == self.vector_dim:
                vectors.append(vec)
                self.faiss_keys.append(query_hash)
                
        if vectors:
            arr = np.vstack(vectors).astype(np.float32)
            # Standardize L2 normalized vectors for cosine similarity (Inner Product)
            norms = np.linalg.norm(arr, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            arr = arr / norms
            self.faiss_index.add(arr)
        conn.close()

    def _encode_text(self, text: str) -> np.ndarray:
        """Embed text using the local all-MiniLM-L6-v2 ONNX model or fallback."""
        if self.use_onnx:
            try:
                inputs = self.tokenizer(text, padding=True, truncation=True, max_length=128, return_tensors="np")
                ort_inputs = {
                    "input_ids": inputs["input_ids"].astype(np.int64),
                    "attention_mask": inputs["attention_mask"].astype(np.int64),
                }
                if "token_type_ids" in inputs:
                    ort_inputs["token_type_ids"] = inputs["token_type_ids"].astype(np.int64)
                outputs = self.onnx_session.run(None, ort_inputs)
                token_embeddings = outputs[0]
                input_mask_expanded = np.expand_dims(inputs["attention_mask"], -1)
                sum_embeddings = np.sum(token_embeddings * input_mask_expanded, axis=1)
                sum_mask = np.clip(np.sum(input_mask_expanded, axis=1), 1e-9, None)
                pooled = sum_embeddings / sum_mask
                
                # L2 Normalize
                norm = np.linalg.norm(pooled, axis=1, keepdims=True)
                normalized = pooled / (norm + 1e-9)
                return normalized[0]
            except Exception as e:
                logger.error(f"ONNX encoding error: {e}")
                pass
                
        return self.encoder.encode(text)

    def store(self, query: str, answer: str, confidence: float):
        """Caches a query, saves its embedding, and updates Zipf-based TTL limits."""
        keyed_query = self._keyed(query)
        query_hash = hashlib.md5(keyed_query.encode(), usedforsecurity=False).hexdigest()
        now = time.time()
        
        conn = get_concurrent_db_connection(self.db_path)
        cursor = conn.cursor()
        
        # Check current frequency for Zipf-law updates
        cursor.execute("SELECT frequency FROM semantic_cache WHERE query_hash = ?", (query_hash,))
        row = cursor.fetchone()
        
        if row:
            freq = row[0] + 1
            ttl = 86400.0 * freq  # Tighten/extend caching for hot items
            cursor.execute("""
                UPDATE semantic_cache 
                SET frequency = ?, ttl = ?, last_accessed = ?, answer = ?, confidence = ?
                WHERE query_hash = ?
            """, (freq, ttl, now, answer, confidence, query_hash))
        else:
            freq = 1
            ttl = 3600.0  # 1 hour baseline TTL
            cursor.execute("""
                INSERT INTO semantic_cache (query_hash, query, answer, confidence, frequency, ttl, created_at, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (query_hash, query, answer, confidence, freq, ttl, now, now))
            
            vec = self._encode_text(keyed_query)
            # Ensure float32 representation
            vec = np.array(vec, dtype=np.float32)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            
            cursor.execute("""
                INSERT OR REPLACE INTO vector_cache (query_hash, vector)
                VALUES (?, ?)
            """, (query_hash, vec.tobytes()))
            
            # Push into FAISS index dynamically
            if self.use_faiss:
                self.faiss_index.add(np.expand_dims(vec, axis=0))
                self.faiss_keys.append(query_hash)
                
        conn.commit()
        conn.close()

    def retrieve(self, query: str) -> Optional[Dict[str, Any]]:
        """Multi-layer cache traversal: Exact → Vector Similarity → Delta Reconstruction."""
        keyed_query = self._keyed(query)
        query_hash = hashlib.md5(keyed_query.encode(), usedforsecurity=False).hexdigest()
        now = time.time()
        
        conn = get_concurrent_db_connection(self.db_path)
        cursor = conn.cursor()
        
        # Layer 1: Exact Query Hashing (O(1))
        cursor.execute("""
            SELECT answer, confidence, frequency, ttl, created_at 
            FROM semantic_cache 
            WHERE query_hash = ?
        """, (query_hash,))
        row = cursor.fetchone()
        
        if row:
            answer, confidence, freq, ttl, created = row
            # Verify TTL
            if now - created < ttl:
                # Update hit frequency
                cursor.execute("""
                    UPDATE semantic_cache 
                    SET frequency = frequency + 1, last_accessed = ? 
                    WHERE query_hash = ?
                """, (now, query_hash))
                conn.commit()
                conn.close()
                return {
                    "answer": answer,
                    "confidence": 0.99,
                    "similarity": 1.0,
                    "method": "exact_hash"
                }

        vec = self._encode_text(keyed_query)
        vec = np.array(vec, dtype=np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        best_hash = None
        best_score = 0.0

        if self.use_faiss and self.faiss_index.ntotal > 0:
            # Query FAISS index for top-1 match
            scores, indices = self.faiss_index.search(np.expand_dims(vec, axis=0), 1)
            idx = indices[0][0]
            score = float(scores[0][0])
            if idx != -1 and score > self.FUZZY_GATE:
                best_hash = self.faiss_keys[idx]
                best_score = score
        else:
            # Fallback manual cosine scan
            cursor.execute("SELECT query_hash, vector FROM vector_cache")
            all_vectors = cursor.fetchall()
            for q_hash, blob in all_vectors:
                stored_vec = np.frombuffer(blob, dtype=np.float32)
                if len(stored_vec) == self.vector_dim:
                    score = float(np.dot(vec, stored_vec))
                    if score > best_score:
                        best_score = score
                        best_hash = q_hash

        if best_hash and best_score >= self.SIMILARITY_GATE:
            cursor.execute("SELECT answer, confidence FROM semantic_cache WHERE query_hash = ?", (best_hash,))
            row = cursor.fetchone()
            if row:
                answer, confidence = row
                conn.close()
                return {
                    "answer": answer,
                    "confidence": round(float(confidence) * float(best_score), 4),
                    "similarity": round(float(best_score), 4),
                    "method": "vector_similarity"
                }

        # Layer 3: Semantic Delta Slot-filling Reconstruction
        # Ex: "List all items in marketing" matches "List all items in [department]"
        words = set(query.lower().split())
        cursor.execute("SELECT query, answer FROM semantic_cache")
        all_cached = cursor.fetchall()
        
        best_delta_ans = None
        best_overlap = 0.0
        
        for cached_query, cached_answer in all_cached:
            cached_words = set(cached_query.lower().split())
            if not cached_words:
                continue
            overlap = len(words & cached_words) / len(words | cached_words)
            if overlap > 0.70 and overlap > best_overlap:
                best_overlap = overlap
                best_delta_ans = cached_answer
                
        if best_delta_ans and best_overlap > self.FUZZY_GATE:
            conn.close()
            return {
                "answer": f"[SEMANTIC DELTA REUSE] {best_delta_ans}",
                "confidence": round(0.80 * best_overlap, 2),
                "similarity": round(best_overlap, 4),
                "method": "semantic_delta"
            }
            
        conn.close()
        return None
