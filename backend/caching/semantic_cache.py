"""
backend/caching/semantic_cache.py
GPTCache-style Multi-Level Semantic Cache with ONNX embedding, SQLite, and FAISS.
Avoids LLM inference entirely by checking for exact string matches
or dense vector semantic similarity to previous queries.
"""

import os
import time
import logging
import sqlite3
import queue
import numpy as np
import faiss
import onnxruntime as ort
from transformers import AutoTokenizer
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)

class MultiLevelSemanticCache:
    """
    Subsystem 4: Multi-Level Semantic Cache.
    GPTCache-style Semantic Cache powered by a local all-MiniLM-L6-v2 ONNX model,
    SQLite database for metadata, and FAISS for vector similarity search.
    """
    def __init__(
        self,
        max_exact_items: int = 10000,
        max_semantic_items: int = 5000,
        db_path: str = "models/semantic_cache.db",
        onnx_model_path: str = "models/all-MiniLM-L6-v2/onnx/model_quantized.onnx",
        tokenizer_path: str = "models/all-MiniLM-L6-v2",
        dimension: int = 384,
        similarity_threshold: float = 0.85
    ):
        self.db_path = db_path
        self.onnx_model_path = onnx_model_path
        self.tokenizer_path = tokenizer_path
        self.dimension = dimension
        self.similarity_threshold = similarity_threshold
        
        self.max_exact_items = max_exact_items
        self.max_semantic_items = max_semantic_items
        
        self.tokenizer = None
        self.session = None
        self.faiss_index = None
        self.cache_hits = 0
        self.total_requests = 0
        
        # Initialize SQLite database
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()
        
        # Initialize ONNX embedding model and FAISS index
        self._init_onnx_and_faiss()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT UNIQUE,
                response TEXT,
                timestamp REAL
            )
        """)
        self.conn.commit()

    def _init_onnx_and_faiss(self):
        # Load ONNX model and tokenizer if present
        if os.path.exists(self.onnx_model_path) and os.path.exists(self.tokenizer_path):
            try:
                providers = ort.get_available_providers()
                provider = "CPUExecutionProvider"
                if "DmlExecutionProvider" in providers:
                    provider = "DmlExecutionProvider"
                
                self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_path)  # nosec B615 - loading from local path, not HuggingFace Hub
                self.session = ort.InferenceSession(self.onnx_model_path, providers=[provider])
                logger.info(f"[SemanticCache] ONNX session loaded successfully on {provider}.")
            except Exception as e:
                logger.error(f"[SemanticCache] Failed to load ONNX session: {e}")
                
        # Initialize FAISS IndexIDMap with a flat index
        try:
            quantizer = faiss.IndexFlatIP(self.dimension) # Cosine similarity uses inner product on normalized vectors
            self.faiss_index = faiss.IndexIDMap(quantizer)
            logger.info("[SemanticCache] FAISS index initialized.")
            
            # Load existing vectors from SQLite to rebuild the FAISS index
            self._rebuild_faiss_index()
        except Exception as e:
            logger.error(f"[SemanticCache] Failed to initialize FAISS index: {e}")

    def _rebuild_faiss_index(self):
        if not self.faiss_index:
            return
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, query FROM cache")
        rows = cursor.fetchall()
        
        if not rows:
            return
            
        ids = []
        vectors = []
        for row_id, query in rows:
            vec = self._embed_query_local(query)
            if vec is not None:
                ids.append(row_id)
                vectors.append(vec)
                
        if vectors:
            vectors_arr = np.vstack(vectors).astype(np.float32)
            ids_arr = np.array(ids, dtype=np.int64)
            self.faiss_index.add_with_ids(vectors_arr, ids_arr)
            logger.info(f"[SemanticCache] Rebuilt FAISS index with {len(ids)} items.")

    def _embed_query_local(self, query: str) -> Optional[np.ndarray]:
        """Embed query using the local all-MiniLM-L6-v2 ONNX model."""
        if not self.session or not self.tokenizer:
            # Fallback embedding if model is not loaded yet
            # Deterministic pseudo-embedding based on character counts to prevent crashes
            seed = sum(ord(c) for c in query)
            np.random.seed(seed)
            vec = np.random.randn(self.dimension)
            return vec / (np.linalg.norm(vec) + 1e-9)
            
        try:
            inputs = self.tokenizer(query, padding=True, truncation=True, max_length=128, return_tensors="np")
            ort_inputs = {
                "input_ids": inputs["input_ids"].astype(np.int64),
                "attention_mask": inputs["attention_mask"].astype(np.int64),
            }
            if "token_type_ids" in inputs:
                ort_inputs["token_type_ids"] = inputs["token_type_ids"].astype(np.int64)
                
            outputs = self.session.run(None, ort_inputs)
            token_embeddings = outputs[0]
            # Perform mean pooling
            input_mask_expanded = np.expand_dims(inputs["attention_mask"], -1)
            sum_embeddings = np.sum(token_embeddings * input_mask_expanded, axis=1)
            sum_mask = np.clip(np.sum(input_mask_expanded, axis=1), 1e-9, None)
            pooled = sum_embeddings / sum_mask
            
            norm = np.linalg.norm(pooled, axis=1, keepdims=True)
            normalized = pooled / (norm + 1e-9)
            return normalized[0]
        except Exception as e:
            logger.error(f"[SemanticCache] ONNX embedding error: {e}")
            return None

    def check_cache(self, query: str, query_vector: Optional[np.ndarray] = None, similarity_threshold: float = 0.85) -> Optional[str]:
        """Checks Level 1 then Level 2 for a cached response."""
        self.total_requests += 1
        query_norm = " ".join(query.lower().split())
        
        # 1. Exact string match check (L1 cache)
        cursor = self.conn.cursor()
        cursor.execute("SELECT response FROM cache WHERE query = ?", (query_norm,))
        row = cursor.fetchone()
        if row:
            self.cache_hits += 1
            logger.info("L1 Semantic Cache HIT (Exact Match). Inference Avoided.")
            return row[0]
            
        # 2. FAISS Semantic Similarity check (L2 cache)
        if self.faiss_index and self.faiss_index.ntotal > 0:
            vec = query_vector if query_vector is not None else self._embed_query_local(query_norm)
            if vec is not None and len(vec) == self.faiss_index.d:
                vec_arr = np.array([vec], dtype=np.float32)
                similarities, ids = self.faiss_index.search(vec_arr, 1)
                
                best_sim = similarities[0][0]
                best_id = ids[0][0]
                
                if best_sim >= similarity_threshold and best_id != -1:
                    cursor.execute("SELECT response FROM cache WHERE id = ?", (int(best_id),))
                    row = cursor.fetchone()
                    if row:
                        self.cache_hits += 1
                        logger.info(f"L2 Semantic Cache HIT (Similarity: {best_sim:.3f}). Inference Avoided.")
                        return row[0]
                        
        return None

    def add_to_cache(self, query: str, response: str, query_vector: Optional[np.ndarray] = None):
        """Adds a new query/response pair to SQLite and updates FAISS index."""
        query_norm = " ".join(query.lower().split())
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO cache (query, response, timestamp) VALUES (?, ?, ?)",
                (query_norm, response, time.time())
            )
            self.conn.commit()
            
            cursor.execute("SELECT id FROM cache WHERE query = ?", (query_norm,))
            row = cursor.fetchone()
            if row and self.faiss_index:
                row_id = row[0]
                vec = query_vector if query_vector is not None else self._embed_query_local(query_norm)
                if vec is not None:
                    if self.faiss_index.d != len(vec):
                        try:
                            import faiss
                            self.faiss_index = faiss.IndexIDMap(faiss.IndexFlatIP(len(vec)))
                        except Exception:
                            pass
                    try:
                        self.faiss_index.remove_ids(np.array([row_id], dtype=np.int64))
                    except Exception:
                        pass
                    vec_arr = np.array([vec], dtype=np.float32)
                    ids_arr = np.array([row_id], dtype=np.int64)
                    self.faiss_index.add_with_ids(vec_arr, ids_arr)
        except Exception as e:
            logger.error(f"[SemanticCache] Failed to add item to cache: {e}")

    def get_hit_rate(self) -> float:
        """Returns cache hit rate as a percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.cache_hits / self.total_requests) * 100.0
