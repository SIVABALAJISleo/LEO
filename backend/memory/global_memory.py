import hashlib
import json
import logging
import time
import os
import itertools
from typing import Dict, Any, List, Optional
import numpy as np
import faiss
from backend.ingest.embedding_pipeline import global_embedding_pipeline
from backend.normalization.normalizer import global_normalizer

logger = logging.getLogger(__name__)

# Constants
MEMORY_DB_PATH = os.path.join(os.getcwd(), "data", "global_memory_faiss.idx")
LOG_PATH = os.path.join(os.getcwd(), "data", "global_memory_log.json")
DIMENSION = 384
MEMORY_CAP = 50_000
REUSE_THRESHOLD = 0.90  # Raised to 0.90 for TRIATTENTION requirements

class GlobalMemory:
    """
    Master memory store — upgraded with semantic FAISS index and persistence.
    """

    def __init__(self):
        self._log: Dict[str, Dict[str, Any]] = {}       # query_hash → entry
        self._id_map: List[str] = []                    # FAISS id → query_hash
        self._index = faiss.IndexFlatL2(DIMENSION)
        self._shape_answers: Dict[str, str] = {}        # shape_key → best answer seen
        self._ensure_data_dir()
        self.load()

    def _ensure_data_dir(self):
        os.makedirs(os.path.dirname(MEMORY_DB_PATH), exist_ok=True)

    def _hash(self, text: str) -> str:
        # Use the canonical text if possible, otherwise use raw
        digest = hashlib.sha256(text.strip().lower().encode()).hexdigest()
        return "".join(itertools.islice(digest, 16))

    def log(
        self,
        query: str,
        answer: str,
        mode: str,
        canonical_form: str,
        confidence: float,
        latency_ms: float = 0.0,
    ):
        """Log a query using canonical form for global indexing."""
        if len(self._log) >= MEMORY_CAP:
            self.compress_memory()

        # Use canonical form as the hash anchor for cross-user reuse
        qhash = self._hash(canonical_form)
        emb = global_embedding_pipeline.get_embeddings([query])[0].astype(np.float32)
        
        entry = {
            "query": query,
            "canonical": canonical_form,
            "answer": answer,
            "mode": mode,
            "confidence": confidence,
            "latency_ms": latency_ms,
            "timestamp": time.time(),
            "reuses": 0,
        }
        
        self._log[qhash] = entry
        self._index.add(np.array([emb]))
        self._id_map.append(qhash)

        self.save()
        logger.debug(f"memory_logged: canonical={canonical_form} qhash={qhash}")

    def lookup(self, query: str, canonical_form: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Hybrid lookup: Canonical Hash -> Semantic Fuzzy (>= 0.85)."""
        if canonical_form:
            qhash = self._hash(canonical_form)
            if qhash in self._log:
                entry = self._log[qhash]
                entry["reuses"] += 1
                return entry
            
        # 2. Semantic
        if self._index.ntotal > 0:
            emb = global_embedding_pipeline.get_embeddings([query])[0].astype(np.float32)
            dist, indices = self._index.search(np.array([emb]), 1)
            
            if indices[0][0] != -1:
                similarity = 1.0 - (dist[0][0] / 2.0)
                # Enforce REUSE_THRESHOLD (Point 2: Semantic similarity >= 0.90)
                if similarity >= REUSE_THRESHOLD: 
                    match_hash = self._id_map[indices[0][0]]
                    entry = self._log[match_hash]
                    entry["reuses"] += 1
                    logger.info(f"memory_semantic_hit: sim={similarity:.4f} (canonical={entry.get('canonical')})")
                    return entry

        logger.debug(f"global_memory: No knowledge found for '{query}' (score < {REUSE_THRESHOLD})")
        return None

    def save(self):
        """Persists the memory log and FAISS index."""
        try:
            with open(LOG_PATH, "w") as f:
                json.dump({
                    "log": self._log,
                    "id_map": self._id_map,
                    "shape_answers": self._shape_answers
                }, f)
            faiss.write_index(self._index, MEMORY_DB_PATH)
        except Exception as e:
            logger.error(f"memory_save_failed: {e}")

    def load(self):
        """Loads memory from disk."""
        if os.path.exists(LOG_PATH) and os.path.exists(MEMORY_DB_PATH):
            try:
                with open(LOG_PATH, "r") as f:
                    data = json.load(f)
                    self._log = data.get("log", {})
                    self._id_map = data.get("id_map", [])
                    self._shape_answers = data.get("shape_answers", {})
                self._index = faiss.read_index(MEMORY_DB_PATH)
                logger.info(f"memory_loaded: entries={len(self._log)}")
            except Exception as e:
                logger.error(f"memory_load_failed: {e}")

    def compress_memory(self):
        """Reduces detailed log size by keeping only best answers."""
        logger.info("memory_compression_started")
        sorted_entries = sorted(self._log.items(), key=lambda x: (x[1]["reuses"], x[1]["timestamp"]), reverse=True)
        keep_count = MEMORY_CAP // 10
        
        new_log = dict(itertools.islice(sorted_entries, keep_count))
        self._log = new_log
        # Index would need a full rebuild here in a production system
        logger.info(f"memory_compressed: remaining={len(self._log)}")
        self.save()

    def search(self, query: str, k: int = 3, threshold: float = 0.88) -> List[Dict[str, Any]]:
        """
        Top-K semantic search for TriAttention Tier 2.
        Returns list of hits with similarity >= threshold, sorted best-first.
        Each hit contains: answer, confidence, similarity, canonical.
        """
        results = []
        if self._index.ntotal == 0:
            return results

        try:
            emb = global_embedding_pipeline.get_embeddings([query])[0].astype(np.float32)
            actual_k = min(k, self._index.ntotal)
            dists, indices = self._index.search(np.array([emb]), actual_k)

            for dist, idx in zip(dists[0], indices[0]):
                if idx == -1:
                    continue
                similarity = 1.0 - (dist / 2.0)
                if similarity < threshold:
                    continue
                if idx >= len(self._id_map):
                    continue
                qhash = self._id_map[idx]
                entry = self._log.get(qhash)
                if entry is None:
                    continue
                results.append({
                    "answer":     entry.get("answer", ""),
                    "confidence": max(entry.get("confidence", similarity), similarity),
                    "similarity": round(similarity, 4),
                    "canonical":  entry.get("canonical", ""),
                    "mode":       entry.get("mode", "memory"),
                })

            # Sort by similarity descending
            results.sort(key=lambda x: x["similarity"], reverse=True)
            logger.debug(f"global_memory.search: k={k} threshold={threshold} found={len(results)}")
        except Exception as exc:
            logger.warning(f"global_memory.search_error: {exc}")

        return results

    def avoidance_stats(self) -> Dict[str, Any]:
        total = len(self._log)
        if total == 0: return {"total": 0, "avoidance_ratio": 0.0}
        model_calls = sum(1 for e in self._log.values() if e["mode"] in ("FULL_CALC", "LARGE_MODEL"))
        return {
            "total": total,
            "avoidance_ratio": float(f"{1.0 - model_calls / total:.3f}"),
            "faiss_total": self._index.ntotal,
            "shape_answers": len(self._shape_answers),
        }

global_memory = GlobalMemory()
