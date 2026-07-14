"""
backend/memory/hierarchical_memory.py
Subsystem 5: Hierarchical Memory System.
Implements four distinct memory tiers:
  1. Working Memory  - current context window (fast, small, in-process dict)
  2. Episodic Memory - session logs (SQLite, recent interactions)
  3. Semantic Memory - long-term factual knowledge (persistent vector store)
  4. Long-Term Memory - summarized, compressed older sessions
"""

import sqlite3
import time
import json
import logging
import os
import numpy as np
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class WorkingMemory:
    """Fast in-process dict for current-session context. Fixed capacity."""
    def __init__(self, capacity: int = 32):
        self.capacity = capacity
        self.store: Dict[str, Any] = {}
        self._order: List[str] = []

    def set(self, key: str, value: Any):
        if key in self.store:
            self._order.remove(key)
        elif len(self.store) >= self.capacity:
            oldest = self._order.pop(0)
            del self.store[oldest]
        self.store[key] = value
        self._order.append(key)

    def get(self, key: str) -> Optional[Any]:
        return self.store.get(key)

    def get_all(self) -> List[tuple]:
        return [(k, self.store[k]) for k in self._order]

    def clear(self):
        self.store.clear()
        self._order.clear()


class EpisodicMemory:
    """SQLite-backed memory for recent user interactions (last 1000 turns)."""
    def __init__(self, db_path: str = "leo_memory.db"):
        self.db_path = db_path
        # For ":memory:" we must keep one persistent connection; for file-based DBs
        # we open/close per call for thread-safety.
        self._in_memory = (db_path == ":memory:")
        if self._in_memory:
            self._conn = sqlite3.connect(db_path, check_same_thread=False)
        else:
            self._conn = None
        self._init_db()

    def _get_conn(self):
        if self._in_memory:
            return self._conn
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                role TEXT,
                content TEXT,
                metadata TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON episodes(timestamp)")
        conn.commit()

    def add(self, role: str, content: str, metadata: Dict = None):
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO episodes (timestamp, role, content, metadata) VALUES (?, ?, ?, ?)",
            (time.time(), role, content, json.dumps(metadata or {}))
        )
        conn.execute("""
            DELETE FROM episodes WHERE id NOT IN (
                SELECT id FROM episodes ORDER BY id DESC LIMIT 1000
            )
        """)
        conn.commit()

    def recall(self, limit: int = 20) -> List[Dict]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT timestamp, role, content, metadata FROM episodes ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [
            {"timestamp": r[0], "role": r[1], "content": r[2], "metadata": json.loads(r[3])}
            for r in reversed(rows)
        ]


class SemanticMemory:
    """
    Long-term vector store for factual knowledge.
    Uses numpy arrays for portability; can be upgraded to FAISS/Chroma later.
    """
    def __init__(self):
        self.docs: List[str] = []
        self.vectors: List[np.ndarray] = []
        self.metadata: List[Dict] = []

    def store(self, text: str, embedding: np.ndarray, metadata: Dict = None):
        self.docs.append(text)
        self.vectors.append(embedding / (np.linalg.norm(embedding) + 1e-9))
        self.metadata.append(metadata or {})

    def query(self, query_vec: np.ndarray, top_k: int = 5) -> List[Dict]:
        if not self.vectors:
            return []
        q_norm = query_vec / (np.linalg.norm(query_vec) + 1e-9)
        matrix = np.vstack(self.vectors)
        sims = matrix @ q_norm
        top_idx = np.argsort(sims)[::-1][:top_k]
        return [
            {"text": self.docs[i], "similarity": float(sims[i]), "metadata": self.metadata[i]}
            for i in top_idx
        ]

    def compress(self, max_items: int = 5000):
        """Keep only the most recently stored entries up to max_items."""
        if len(self.docs) > max_items:
            self.docs = self.docs[-max_items:]
            self.vectors = self.vectors[-max_items:]
            self.metadata = self.metadata[-max_items:]
            logger.info(f"Semantic memory compressed to {max_items} entries.")


class HierarchicalMemory:
    """Unified interface for all memory tiers."""
    def __init__(self, db_path: str = "leo_memory.db"):
        self.working = WorkingMemory(capacity=32)
        self.episodic = EpisodicMemory(db_path=db_path)
        self.semantic = SemanticMemory()

    def record_turn(self, role: str, content: str):
        """Log every interaction to Episodic Memory."""
        self.episodic.add(role, content)

    def get_recent_context(self, limit: int = 10) -> List[Dict]:
        return self.episodic.recall(limit=limit)
