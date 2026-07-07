import numpy as np
import sqlite3
from backend.core.db_utils import get_concurrent_db_connection
import os
import json
import logging
import time
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger("HyperCore.VectorStore")

class FaissVectorStore:
    """
    FAISS-backed vector store for semantic retrieval.
    Falls back to a pure-NumPy linear scan store when FAISS is unavailable.
    Supports persist/load, IDMap for stable document IDs, and L2/cosine search.
    """
    def __init__(self, embedding_dim: int = 384, index_dir: str = ".hyper_cache/faiss"):
        self.embedding_dim = embedding_dim
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)

        self._vectors: List[np.ndarray] = []   # Fallback list
        self._ids: List[str] = []
        self.use_faiss = False

        try:
            import faiss
            # Flat inner-product index (cosine when normalized)
            self._faiss_inner = faiss.IndexFlatIP(embedding_dim)
            self._index = faiss.IndexIDMap(self._faiss_inner)
            self._faiss_id_map: Dict[str, int] = {}  # chunk_id -> int id
            self._int_id_to_cid: Dict[int, str] = {}
            self._next_int_id = 0
            self.use_faiss = True
            logger.info("FAISS vector store initialized.")
        except ImportError:
            logger.warning("FAISS not available. Using NumPy linear scan fallback.")

    def _normalize(self, v: np.ndarray) -> np.ndarray:
        if v.ndim == 1:
            v = v[np.newaxis, :]
        norms = np.linalg.norm(v, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1.0, norms)
        return (v / norms).astype(np.float32)

    def add(self, chunk_id: str, embedding: np.ndarray):
        emb = self._normalize(embedding)
        if self.use_faiss:
            int_id = self._next_int_id
            self._next_int_id += 1
            self._faiss_id_map[chunk_id] = int_id
            self._int_id_to_cid[int_id] = chunk_id
            self._index.add_with_ids(emb, np.array([int_id], dtype=np.int64))
        else:
            self._vectors.append(emb[0])
            self._ids.append(chunk_id)

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        """Returns list of (chunk_id, cosine_score) sorted by relevance."""
        emb = self._normalize(query_embedding)

        if self.use_faiss and self._index.ntotal > 0:
            k = min(top_k, self._index.ntotal)
            D, I = self._index.search(emb, k)
            results = []
            for score, int_id in zip(D[0], I[0]):
                if int_id == -1:
                    continue
                cid = self._int_id_to_cid.get(int(int_id))
                if cid:
                    results.append((cid, float(score)))
            return results

        if not self._vectors:
            return []

        # NumPy fallback: brute-force cosine similarity
        matrix = np.stack(self._vectors, axis=0)          # [N, D]
        scores = matrix @ emb[0]                           # [N]
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(self._ids[i], float(scores[i])) for i in top_indices]

    def save(self):
        if self.use_faiss:
            import faiss
            faiss.write_index(self._index, os.path.join(self.index_dir, "faiss.index"))
            with open(os.path.join(self.index_dir, "id_maps.json"), "w") as f:
                json.dump({
                    "faiss_id_map": self._faiss_id_map,
                    "int_id_to_cid": {str(k): v for k, v in self._int_id_to_cid.items()},
                    "next_int_id": self._next_int_id
                }, f)
            logger.info(f"FAISS index saved: {self._index.ntotal} vectors.")

    def load(self):
        index_path = os.path.join(self.index_dir, "faiss.index")
        maps_path = os.path.join(self.index_dir, "id_maps.json")
        if self.use_faiss and os.path.exists(index_path):
            import faiss
            self._index = faiss.read_index(index_path)
            if os.path.exists(maps_path):
                with open(maps_path) as f:
                    data = json.load(f)
                self._faiss_id_map = data.get("faiss_id_map", {})
                self._int_id_to_cid = {int(k): v for k, v in data.get("int_id_to_cid", {}).items()}
                self._next_int_id = data.get("next_int_id", 0)
            logger.info(f"FAISS index loaded: {self._index.ntotal} vectors.")

    @property
    def ntotal(self) -> int:
        if self.use_faiss:
            return self._index.ntotal
        return len(self._vectors)


class SQLiteDocumentStore:
    """
    SQLite-backed document metadata and content store.
    Lightweight, zero-dependency fallback for persistent chunk storage.
    """
    def __init__(self, db_path: str = ".hyper_cache/doc_store.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = get_concurrent_db_connection(db_path)
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id TEXT PRIMARY KEY,
                doc_id TEXT NOT NULL,
                content TEXT NOT NULL,
                fingerprint TEXT NOT NULL,
                metadata TEXT NOT NULL,
                added_at REAL NOT NULL
            )
        """)
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_doc_id ON chunks(doc_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_fingerprint ON chunks(fingerprint)")
        self.conn.commit()

    def add_chunk(self, chunk: Dict[str, Any]):
        try:
            self.conn.execute(
                "INSERT OR REPLACE INTO chunks VALUES (?,?,?,?,?,?)",
                (
                    chunk["chunk_id"],
                    chunk["doc_id"],
                    chunk["content"],
                    chunk["fingerprint"],
                    json.dumps(chunk["metadata"]),
                    time.time()
                )
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"SQLiteDocumentStore.add_chunk error: {e}")

    def get_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.execute(
            "SELECT chunk_id, doc_id, content, fingerprint, metadata FROM chunks WHERE chunk_id=?",
            (chunk_id,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "chunk_id": row[0], "doc_id": row[1], "content": row[2],
                "fingerprint": row[3], "metadata": json.loads(row[4])
            }
        return None

    def get_chunks_by_doc(self, doc_id: str) -> List[Dict[str, Any]]:
        cursor = self.conn.execute(
            "SELECT chunk_id, doc_id, content, fingerprint, metadata FROM chunks WHERE doc_id=?",
            (doc_id,)
        )
        return [{"chunk_id": r[0], "doc_id": r[1], "content": r[2],
                 "fingerprint": r[3], "metadata": json.loads(r[4])} for r in cursor.fetchall()]

    def fingerprint_exists(self, fp: str) -> bool:
        cursor = self.conn.execute("SELECT 1 FROM chunks WHERE fingerprint=?", (fp,))
        return cursor.fetchone() is not None

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
