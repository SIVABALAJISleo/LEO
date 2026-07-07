"""
Global Reasoning Memory (Upgraded PHASE 3)
Stores reasoning steps for past queries using a FAISS-backed semantic index
and persistent SQLite storage for cross-session query reuse.
"""
import hashlib
import json
import logging
import sqlite3
from backend.core.db_utils import get_concurrent_db_connection
import os
from typing import Optional, Dict, Any, List
import numpy as np
import faiss
from backend.ingest.embedding_pipeline import global_embedding_pipeline

logger = logging.getLogger(__name__)

# Constants
REASONING_DB_PATH = os.path.join(os.getcwd(), "data", "reasoning_cache.db")
FAISS_INDEX_PATH = os.path.join(os.getcwd(), "data", "reasoning_faiss.idx")
DIMENSION = 384  # MiniLM-L6-v2 dimension
SIMILARITY_THRESHOLD = 0.92  # High threshold for reasoning reuse

class ReasoningStore:
    """
    Persistent store of {query_hash → {steps, answer, confidence}}.
    Uses hybrid search: Exact (Hash) + Fuzzy (FAISS/Embeddings).
    """

    def __init__(self):
        self._ensure_data_dir()
        self._conn = get_concurrent_db_connection(REASONING_DB_PATH)
        self._init_db()
        self._index = faiss.IndexFlatL2(DIMENSION)
        self._id_map: List[str] = []  # Maps FAISS index to query_hash
        self._load_index()

    def _ensure_data_dir(self):
        os.makedirs(os.path.dirname(REASONING_DB_PATH), exist_ok=True)

    def _init_db(self):
        cursor = self._conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reasoning (
                query_hash TEXT PRIMARY KEY,
                query_text TEXT,
                steps TEXT,
                answer TEXT,
                confidence REAL,
                reuses INTEGER DEFAULT 0,
                embedding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self._conn.commit()

    def _load_index(self):
        """Loads all embeddings into FAISS from SQLite."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT query_hash, embedding FROM reasoning WHERE embedding IS NOT NULL")
        rows = cursor.fetchall()
        
        if not rows:
            return

        embeddings = []
        for q_hash, emb_blob in rows:
            emb = np.frombuffer(emb_blob, dtype=np.float32)
            embeddings.append(emb)
            self._id_map.append(q_hash)
            
        if embeddings:
            self._index.add(np.array(embeddings).astype(np.float32)) # type: ignore
            logger.info(f"reasoning_index_loaded: count={len(embeddings)}")

    def _get_embedding(self, query: str) -> np.ndarray:
        """Standardized embedding generation."""
        emb = global_embedding_pipeline.get_embeddings([query])[0]
        return emb.astype(np.float32)

    def _key(self, query: str) -> str:
        return hashlib.sha256(query.strip().lower().encode()).hexdigest()

    def store(self, query: str, steps: List[str], answer: str, confidence: float = 0.9):
        """Persistently stores a reasoning trace."""
        q_hash = self._key(query)
        embedding = self._get_embedding(query)
        
        cursor = self._conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO reasoning (query_hash, query_text, steps, answer, confidence, embedding)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (q_hash, query, json.dumps(steps), answer, confidence, embedding.tobytes()))
        self._conn.commit()

        # Update FAISS
        self._index.add(np.array([embedding]).astype('float32')) # type: ignore
        self._id_map.append(q_hash)
        
        logger.info("reasoning_stored: hash=%s..." % q_hash[0:8])

    def lookup(self, query: str) -> Optional[Dict[str, Any]]:
        """Hybrid lookup: Exact Hash -> Semantic Fuzzy."""
        q_hash = self._key(query)
        
        # 1. Exact Match
        cursor = self._conn.cursor()
        cursor.execute("SELECT steps, answer, confidence, reuses FROM reasoning WHERE query_hash = ?", (q_hash,))
        row = cursor.fetchone()
        
        if row:
            steps, answer, confidence, reuses = row
            cursor.execute("UPDATE reasoning SET reuses = reuses + 1 WHERE query_hash = ?", (q_hash,))
            self._conn.commit()
            return {
                "steps": json.loads(steps),
                "answer": answer,
                "confidence": confidence,
                "mode": "EXACT"
            }

        # 2. Semantic Fuzzy Match
        if self._index.ntotal == 0:
            return None

        query_emb = self._get_embedding(query)
        distances, indices = self._index.search(np.array([query_emb]).astype('float32'), k=1) # type: ignore
        
        # In L2 distance, lower is closer. For normalized vectors, dist ~ 2(1-cos_sim)
        # Cosine Similarity = 1 - (dist/2)
        if indices[0][0] != -1:
            dist = distances[0][0]
            similarity = 1.0 - (dist / 2.0)
            
            if similarity >= SIMILARITY_THRESHOLD:
                match_hash = self._id_map[indices[0][0]]
                cursor.execute("SELECT steps, answer, confidence FROM reasoning WHERE query_hash = ?", (match_hash,))
                match_row = cursor.fetchone()
                
                if match_row:
                    steps, answer, confidence = match_row
                    logger.info(f"reasoning_semantic_hit: sim={similarity:.4f}")
                    return {
                        "steps": json.loads(steps),
                        "answer": answer,
                        "confidence": confidence,
                        "mode": "SEMANTIC",
                        "similarity": float(similarity)
                    }

        return None

    def stats(self) -> Dict[str, Any]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT COUNT(*), SUM(reuses) FROM reasoning")
        count, reuses = cursor.fetchone()
        return {
            "total_stored": count,
            "total_reuses": reuses or 0,
            "faiss_total": self._index.ntotal
        }


global_reasoning_store = ReasoningStore()
