"""
backend/crystallization/crystallizer.py
Reasoning trace crystallization compiler (Tier 5) -> Semantic Crystallization Cache.
Converts repeated neural reasoning traces into semantic cache hits to permanently minimize GPU computation costs.
"""
import os
import time
import json
import sqlite3
import numpy as np
import logging
from typing import Dict, Any, List, Optional, Tuple
from backend.core.db_utils import get_concurrent_db_connection

logger = logging.getLogger(__name__)

class SemanticCrystallizer:
    """
    Analyzes historical query execution traces and embeds them into a local Faiss index.
    On new queries, performs ANN lookup to bypass inference if cosine similarity > 0.92.
    """

    def __init__(self, db_path: str = "hyper_engine.db"):
        self.db_path = db_path
        self.embedding_model = None
        self.index = None
        self.trace_ids = []
        self.threshold = 0.92
        self._initialize_sqlite()
        self._load_embedder()
        self._build_index()

    def _initialize_sqlite(self):
        conn = get_concurrent_db_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crystallized_answers (
                trace_id TEXT PRIMARY KEY,
                query TEXT,
                response TEXT,
                workload_class TEXT,
                embedding_json TEXT,
                hit_count INTEGER DEFAULT 0,
                latency_ms REAL DEFAULT 0.0,
                timestamp REAL
            )
        """)
        
        conn.commit()
        conn.close()

    def _load_embedder(self):
        try:
            from sentence_transformers import SentenceTransformer
            # Try bge-small-en-v1.5 or fallback to nomic-embed-text
            try:
                self.embedding_model = SentenceTransformer('BAAI/bge-small-en-v1.5')
                logger.info("Loaded bge-small-en-v1.5 embedding model for semantic caching.")
            except Exception:
                self.embedding_model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)
                logger.info("Loaded nomic-embed-text-v1.5 embedding model for semantic caching.")
        except ImportError:
            logger.warning("sentence-transformers not installed. Using mocked local embedder.")
            self.embedding_model = None

    def embed_query(self, query: str) -> np.ndarray:
        if self.embedding_model:
            # Handle nomic prefixing if necessary
            prefix = "search_query: " if "nomic" in getattr(self.embedding_model, "model_card_data", {}).get("model_name", "").lower() else ""
            emb = self.embedding_model.encode(prefix + query, normalize_embeddings=True)
            return emb
        else:
            # Mocked deterministic embedding using simple hashing for test purposes
            import hashlib
            h = int(hashlib.md5(query.encode()).hexdigest(), 16)
            np.random.seed(h % (2**32))
            emb = np.random.randn(384).astype(np.float32)
            emb = emb / np.linalg.norm(emb)
            return emb

    def _build_index(self):
        conn = get_concurrent_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT trace_id, embedding_json FROM crystallized_answers")
        rows = cursor.fetchall()
        conn.close()

        try:
            import faiss
            self.index = faiss.IndexFlatIP(384) # Inner product for cosine sim (embeddings must be normalized)
            self.faiss_available = True
        except ImportError:
            logger.warning("faiss-cpu not installed. Using exact numpy matching fallback.")
            self.index = []
            self.faiss_available = False

        self.trace_ids = []
        if rows:
            embeddings = []
            for trace_id, emb_json in rows:
                if emb_json:
                    emb = np.array(json.loads(emb_json), dtype=np.float32)
                    embeddings.append(emb)
                    self.trace_ids.append(trace_id)
            
            if embeddings:
                embeddings_np = np.vstack(embeddings)
                if self.faiss_available:
                    self.index.add(embeddings_np)
                else:
                    self.index = embeddings_np
        logger.info(f"Crystallization index built with {len(self.trace_ids)} cached answers.")

    def record_trace(self, trace_id: str, query: str, response: str, w_class: str, latency_ms: float = 0.0):
        """Records a successful execution trace and adds it to the semantic cache."""
        emb = self.embed_query(query)
        emb_json = json.dumps(emb.tolist())
        
        conn = get_concurrent_db_connection(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO crystallized_answers (trace_id, query, response, workload_class, embedding_json, latency_ms, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (trace_id, query, response, w_class, emb_json, latency_ms, time.time()))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to record crystallization trace: {e}")
        finally:
            conn.close()
            
        # Update in-memory index
        if self.faiss_available:
            self.index.add(np.expand_dims(emb, axis=0))
        else:
            if isinstance(self.index, list):
                self.index = np.expand_dims(emb, axis=0)
            else:
                self.index = np.vstack([self.index, emb])
        self.trace_ids.append(trace_id)

    def invalidate_trace(self, trace_id: str):
        """Removes a trace when underlying facts change."""
        conn = get_concurrent_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM crystallized_answers WHERE trace_id = ?", (trace_id,))
        conn.commit()
        conn.close()
        # Rebuild index from scratch to drop it safely
        self._build_index()

    def rephrase_template(self, query: str, response: str) -> str:
        """Lightly rephrase the response if a template dynamic match occurs."""
        # Simple dynamic template substitution / rephraser for personalization
        greeting_words = ["hello", "hi", "hey"]
        if any(w in query.lower() for w in greeting_words):
            return f"Hello! Here is your crystallized response: {response}"
        return response

    def match_shortcut(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Searches the semantic cache. If cosine similarity > threshold, returns cached answer.
        """
        if not self.trace_ids:
            return None
            
        emb = self.embed_query(query)
        
        best_idx = -1
        best_score = -1.0
        
        if self.faiss_available:
            scores, indices = self.index.search(np.expand_dims(emb, axis=0), 1)
            best_score = float(scores[0][0])
            best_idx = int(indices[0][0])
        else:
            if not isinstance(self.index, list) and self.index.shape[0] > 0:
                scores = np.dot(self.index, emb)
                best_idx = int(np.argmax(scores))
                best_score = float(scores[best_idx])
                
        if best_score > self.threshold and best_idx != -1:
            trace_id = self.trace_ids[best_idx]
            # Fetch answer and increment hit count
            conn = get_concurrent_db_connection(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT response FROM crystallized_answers WHERE trace_id = ?", (trace_id,))
            row = cursor.fetchone()
            if row:
                cursor.execute("UPDATE crystallized_answers SET hit_count = hit_count + 1 WHERE trace_id = ?", (trace_id,))
                conn.commit()
                conn.close()
                
                # Apply light rephrasing template
                final_response = self.rephrase_template(query, row[0])
                
                # Track in global avoidance tracker
                try:
                    from backend.analytics.avoidance_tracker import global_avoidance_tracker
                    global_avoidance_tracker.log_request(
                        request_id=f"cryst_{trace_id}_{int(time.time())}",
                        query=query,
                        family_id="crystallization",
                        path_taken="crystallization",
                        latency_ms=1.5,
                        model_called=False,
                        entropy_score=0.01,
                        is_cache_hit=True,
                        is_prediction_hit=False,
                        is_recovery=False
                    )
                except Exception:
                    pass

                return {
                    "shortcut_id": trace_id,
                    "response": final_response,
                    "similarity": best_score,
                    "method": "semantic_crystallization"
                }
            conn.close()
            
        return None

# Backward compatibility alias
TraceCompiler = SemanticCrystallizer
