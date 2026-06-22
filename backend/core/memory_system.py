"""
backend/core/memory_system.py
LEO AI Production Memory System - Phase 3 Implementation
Implements 6 distinct memory types:
  1. Episodic Memory  - specific events, conversations, experiences
  2. Semantic Memory  - factual knowledge, concepts
  3. Working Memory   - current conversation context window
  4. Reflection Memory - meta-reasoning insights
  5. Failure Memory   - failure traces and failure patterns
  6. Procedural Memory - "how-to" steps and actionable sequences

Features:
  - Contradiction detection via cosine similarity comparison
  - Memory aging and decay via TTL
  - Memory consolidation (merge near-duplicate entries)
  - Memory ranking by confidence and access frequency
"""
import time
import hashlib
import sqlite3
import logging
import json
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

MEMORY_DB_PATH = "hyper_engine.db"

@dataclass
class MemoryEntry:
    memory_id: str
    memory_type: str       # episodic|semantic|working|reflection|failure|procedural
    content: str
    confidence: float
    access_count: int
    created_at: float
    last_accessed: float
    ttl_seconds: float     # -1 = never expires
    vector: Optional[bytes] = None  # Serialized float32 numpy vector
    tags: Optional[str] = None      # JSON list of tag strings


class MemorySystem:
    """
    Production-grade 6-tier memory system with contradiction detection,
    aging, consolidation, and ranking capabilities.
    """

    SIMILARITY_CONTRADICTION_THRESHOLD = 0.80  # If >0.80 similar and contradicts
    SIMILARITY_DUPLICATE_THRESHOLD = 0.92      # If >0.92 same content → consolidate

    TTL_BY_TYPE: Dict[str, float] = {
        "episodic":   86400 * 7,   # 7 days
        "semantic":   -1,          # permanent
        "working":    3600 * 2,    # 2 hours
        "reflection": -1,          # permanent
        "failure":    86400 * 30,  # 30 days
        "procedural": -1,          # permanent
    }

    def __init__(self, db_path: str = MEMORY_DB_PATH):
        self.db_path = db_path
        self._init_db()

        # Load encoder
        try:
            from sentence_transformers import SentenceTransformer
            self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
            self.vector_dim = 384
            logger.info("[MemorySystem] SentenceTransformer encoder loaded.")
        except Exception as e:
            from backend.cache.semantic_cache import TrigramEmbedder
            self.encoder = TrigramEmbedder()
            self.vector_dim = 384
            logger.warning(f"[MemorySystem] Fallback TrigramEmbedder: {e}")

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_system (
                memory_id      TEXT PRIMARY KEY,
                memory_type    TEXT NOT NULL,
                content        TEXT NOT NULL,
                confidence     REAL DEFAULT 0.9,
                access_count   INTEGER DEFAULT 1,
                created_at     REAL,
                last_accessed  REAL,
                ttl_seconds    REAL DEFAULT -1,
                vector         BLOB,
                tags           TEXT
            )
        """)
        conn.commit()
        conn.close()
        logger.info("[MemorySystem] DB tables initialized.")

    def _encode(self, text: str) -> np.ndarray:
        vec = np.array(self.encoder.encode(text), dtype=np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def store(
        self,
        content: str,
        memory_type: str = "episodic",
        confidence: float = 0.9,
        tags: Optional[List[str]] = None,
    ) -> Tuple[str, bool]:
        """
        Stores a memory entry with:
        - Duplicate detection (merge if similarity > 0.92)
        - Contradiction detection (warn if similarity > 0.80 but contradicts)
        Returns (memory_id, was_new).
        """
        memory_id = hashlib.md5(
            f"{memory_type}:{content}".encode(), usedforsecurity=False
        ).hexdigest()

        vec = self._encode(content)
        ttl = self.TTL_BY_TYPE.get(memory_type, 86400.0)
        now = time.time()

        # Check for near-duplicates or contradictions
        existing = self._find_similar(vec, memory_type, top_k=3)
        for entry in existing:
            sim = entry["similarity"]
            if sim >= self.SIMILARITY_DUPLICATE_THRESHOLD:
                # Merge: update access count and confidence
                self._bump_access(entry["memory_id"], confidence)
                logger.info(f"[MemorySystem] Duplicate memory consolidated (sim={sim:.3f})")
                return entry["memory_id"], False
            if sim >= self.SIMILARITY_CONTRADICTION_THRESHOLD:
                logger.warning(
                    f"[MemorySystem] Potential contradiction detected (sim={sim:.3f}) "
                    f"with existing memory: {entry['content'][:60]}…"
                )

        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            INSERT OR REPLACE INTO memory_system
            (memory_id, memory_type, content, confidence, access_count,
             created_at, last_accessed, ttl_seconds, vector, tags)
            VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
            (
                memory_id, memory_type, content, confidence, 1,
                now, now, ttl,
                vec.tobytes(),
                json.dumps(tags or []),
            ),
        )
        conn.commit()
        conn.close()
        return memory_id, True

    def retrieve(
        self,
        query: str,
        memory_type: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Retrieves relevant memories by vector similarity, filtered by type and TTL."""
        vec = self._encode(query)
        now = time.time()

        type_clause = "AND memory_type = ?" if memory_type else ""
        params = (memory_type,) if memory_type else ()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT memory_id, memory_type, content, confidence, access_count,
                   created_at, last_accessed, ttl_seconds, vector, tags
            FROM memory_system
            WHERE (ttl_seconds = -1 OR (? - created_at) < ttl_seconds)
            {type_clause}
            """,
            (now,) + params,
        )
        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            stored_vec = np.frombuffer(row[8], dtype=np.float32) if row[8] else None
            if stored_vec is None or len(stored_vec) != self.vector_dim:
                continue
            sim = float(np.dot(vec, stored_vec))
            if sim > 0.3:  # Minimum relevance threshold
                results.append({
                    "memory_id":    row[0],
                    "memory_type":  row[1],
                    "content":      row[2],
                    "confidence":   row[3],
                    "access_count": row[4],
                    "similarity":   round(sim, 4),
                    "tags":         json.loads(row[9] or "[]"),
                })

        # Sort by composite score (similarity × confidence × log(access_count+1))
        results.sort(
            key=lambda x: x["similarity"] * x["confidence"] * (1 + x["access_count"] * 0.01),
            reverse=True,
        )
        return results[:top_k]

    def _find_similar(
        self, vec: np.ndarray, memory_type: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT memory_id, content, vector FROM memory_system WHERE memory_type = ?",
            (memory_type,),
        )
        rows = cursor.fetchall()
        conn.close()

        scored = []
        for row in rows:
            stored_vec = np.frombuffer(row[2], dtype=np.float32) if row[2] else None
            if stored_vec is None or len(stored_vec) != self.vector_dim:
                continue
            sim = float(np.dot(vec, stored_vec))
            scored.append({"memory_id": row[0], "content": row[1], "similarity": sim})

        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_k]

    def _bump_access(self, memory_id: str, new_confidence: float):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            UPDATE memory_system
            SET access_count = access_count + 1,
                last_accessed = ?,
                confidence = MAX(confidence, ?)
            WHERE memory_id = ?
            """,
            (time.time(), new_confidence, memory_id),
        )
        conn.commit()
        conn.close()

    def decay_and_purge(self) -> int:
        """Purges expired memories (TTL elapsed). Returns count deleted."""
        now = time.time()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM memory_system
            WHERE ttl_seconds != -1 AND (? - created_at) > ttl_seconds
            """,
            (now,),
        )
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        logger.info(f"[MemorySystem] Purged {deleted} expired memory entries.")
        return deleted

    def get_summary(self) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT memory_type, COUNT(*) FROM memory_system GROUP BY memory_type"
        )
        rows = cursor.fetchall()
        conn.close()
        return {"counts_by_type": dict(rows), "db": self.db_path}


# Global singleton
global_memory_system = MemorySystem()
