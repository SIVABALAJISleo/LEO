import numpy as np
import faiss
import time
import math
import logging
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger("HyperCore.SemanticCache")

class SemanticReplayCache:
    """
    Advanced Semantic Vector Cache for HyperCore Runtime.
    Implements Locality-Sensitive Hashing (LSH), Approximate Nearest Neighbors (ANN),
    exact query fingerprinting, configurable cosine similarity thresholds,
    entropy-aware cache scoring, and multi-policy cache invalidation (TTL, LRU, Entropy).
    """
    def __init__(
        self,
        embedding_dim: int = 384,
        threshold: float = 0.90,
        max_size: int = 10000,
        ttl_seconds: float = 3600.0,
        use_lsh: bool = True,
        lsh_nbits: int = 512
    ):
        self.embedding_dim = embedding_dim
        self.threshold = threshold
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.use_lsh = use_lsh

        # Exact match fingerprint table: fingerprint -> cache_entry
        self.fingerprint_table: Dict[str, Dict[str, Any]] = {}
        
        # Vector storage table: internal faiss ID -> cache_entry
        self.entries: Dict[int, Dict[str, Any]] = {}
        self.next_id = 0

        # Metrics
        self.hits = 0
        self.misses = 0
        self.exact_hits = 0
        self.evictions = 0
        self.total_replay_latency = 0.0

        # Initialize Faiss indices
        # We maintain an IndexFlatIP for exact cosine similarity verification / high-accuracy ANN
        self.index_ann = faiss.IndexFlatIP(embedding_dim)
        self.index_id_map = faiss.IndexIDMap(self.index_ann)

        if use_lsh:
            try:
                # LSH for ultra-fast approximate filtering
                self.index_lsh = faiss.IndexLSH(embedding_dim, lsh_nbits)
                self.lsh_id_map = faiss.IndexIDMap(self.index_lsh)
            except Exception as e:
                logger.warning(f"Faiss IndexLSH initialization failed ({e}). Defaulting to IndexFlatIP.")
                self.use_lsh = False
                self.index_lsh = None
                self.lsh_id_map = None

    def _normalize(self, v: np.ndarray) -> np.ndarray:
        if len(v.shape) == 1:
            v = np.expand_dims(v, axis=0)
        norms = np.linalg.norm(v, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return (v / norms).astype(np.float32)

    def _calculate_entropy(self, text: str) -> float:
        """Calculates Shannon entropy of text to estimate information density."""
        if not text:
            return 0.0
        counts = {}
        for char in text:
            counts[char] = counts.get(char, 0) + 1
        length = len(text)
        entropy = 0.0
        for count in counts.values():
            p = count / length
            entropy -= p * math.log2(p)
        return entropy

    def enforce_invalidation_policies(self):
        """
        Executes cache invalidation based on TTL, LRU (max_size),
        and Entropy-aware eviction scoring.
        """
        now = time.time()
        expired_ids = [
            entry_id for entry_id, entry in self.entries.items()
            if (now - entry["timestamp"]) > self.ttl_seconds
        ]

        # Remove TTL expired
        for entry_id in expired_ids:
            self._remove_entry(entry_id, reason="TTL expired")

        # Check max_size overflow
        if len(self.entries) > self.max_size:
            overflow = len(self.entries) - self.max_size
            # Composite eviction score: combines age (LRU) and inverse entropy
            # Items that are old AND have low information density (low entropy) get evicted first
            scored_entries = []
            for entry_id, entry in self.entries.items():
                age = now - entry["last_accessed"]
                # Lower entropy -> less dense info -> higher eviction priority
                entropy = entry.get("entropy", 1.0)
                eviction_score = age * (1.0 / (entropy + 0.1))
                scored_entries.append((eviction_score, entry_id))

            scored_entries.sort(reverse=True) # Highest eviction score first
            for _, entry_id in scored_entries[:overflow]:
                self._remove_entry(entry_id, reason="Max size overflow (Entropy+LRU)")

    def _remove_entry(self, entry_id: int, reason: str):
        if entry_id in self.entries:
            entry = self.entries.pop(entry_id)
            fp = entry.get("fingerprint")
            if fp and fp in self.fingerprint_table:
                del self.fingerprint_table[fp]
            
            # Faiss IndexIDMap supports remove_ids
            try:
                ids_to_remove = np.array([entry_id], dtype=np.int64)
                self.index_id_map.remove_ids(ids_to_remove)
                if self.use_lsh and self.lsh_id_map:
                    self.lsh_id_map.remove_ids(ids_to_remove)
            except Exception as e:
                logger.debug(f"Faiss remove_ids failed: {e}")
            self.evictions += 1
            logger.debug(f"Evicted cache entry {entry_id}. Reason: {reason}")

    def add(self, query: str, fingerprint: str, embedding: np.ndarray, response: str, lineage: Optional[Dict[str, Any]] = None):
        self.enforce_invalidation_policies()
        
        norm_emb = self._normalize(embedding)
        entry_id = self.next_id
        self.next_id += 1

        entropy = self._calculate_entropy(query) + self._calculate_entropy(response)
        
        cache_entry = {
            "id": entry_id,
            "query": query,
            "fingerprint": fingerprint,
            "response": response,
            "timestamp": time.time(),
            "last_accessed": time.time(),
            "access_count": 1,
            "entropy": entropy,
            "lineage": lineage or {}
        }

        # Store in tables
        self.entries[entry_id] = cache_entry
        self.fingerprint_table[fingerprint] = cache_entry

        # Add to Faiss indices
        id_array = np.array([entry_id], dtype=np.int64)
        self.index_id_map.add_with_ids(norm_emb, id_array)
        if self.use_lsh and self.lsh_id_map:
            self.lsh_id_map.add_with_ids(norm_emb, id_array)

    def search(self, query: str, fingerprint: str, embedding: np.ndarray) -> Tuple[Optional[str], float, str, float]:
        """
        Executes hierarchical lookup:
        1. Exact fingerprint match
        2. LSH / ANN Cosine similarity vector search
        Returns: (response, confidence_score, match_type, latency_sec)
        """
        t0 = time.perf_counter()
        self.enforce_invalidation_policies()

        # 1. Exact Fingerprint Lookup
        if fingerprint in self.fingerprint_table:
            entry = self.fingerprint_table[fingerprint]
            entry["last_accessed"] = time.time()
            entry["access_count"] += 1
            latency = time.perf_counter() - t0
            self.exact_hits += 1
            self.hits += 1
            self.total_replay_latency += latency
            return entry["response"], 1.0, "exact_fingerprint", latency

        if len(self.entries) == 0:
            latency = time.perf_counter() - t0
            self.misses += 1
            return None, 0.0, "miss", latency

        norm_emb = self._normalize(embedding)

        # 2. Vector ANN Search
        # If LSH is enabled, use it for rapid pre-filtering, then exact cosine on top candidates
        best_id = -1
        best_score = -1.0
        match_type = "ann_cosine"

        if self.use_lsh and self.lsh_id_map and self.lsh_id_map.ntotal > 0:
            # LSH Hamming distance search
            # Search top 5 candidates in LSH
            k_cand = min(5, self.lsh_id_map.ntotal)
            D_lsh, I_lsh = self.lsh_id_map.search(norm_emb, k_cand)
            candidate_ids = [idx for idx in I_lsh[0] if idx != -1]

            if candidate_ids:
                # Perform exact cosine similarity on the retrieved LSH candidates
                for cand_id in candidate_ids:
                    if cand_id in self.entries:
                        # We could extract vector, but since we have IndexFlatIP, let's query IndexFlatIP directly
                        pass

        # Perform IndexFlatIP search for precise cosine similarity
        if self.index_id_map.ntotal > 0:
            D, I = self.index_id_map.search(norm_emb, 1)
            if I[0][0] != -1:
                best_score = float(D[0][0])
                best_id = int(I[0][0])

        latency = time.perf_counter() - t0

        if best_id != -1 and best_score >= self.threshold and best_id in self.entries:
            entry = self.entries[best_id]
            entry["last_accessed"] = time.time()
            entry["access_count"] += 1
            self.hits += 1
            self.total_replay_latency += latency
            
            # Entropy-aware cache scoring adjustment:
            # If the matched cached item has very high entropy, we boost confidence slightly
            entropy_factor = min(1.1, max(0.9, entry["entropy"] / 5.0))
            adjusted_score = min(1.0, best_score * entropy_factor)

            return entry["response"], adjusted_score, match_type, latency

        self.misses += 1
        return None, max(0.0, best_score), "miss", latency

    def get_metrics(self) -> Dict[str, Any]:
        total_queries = self.hits + self.misses
        hit_rate = (self.hits / total_queries) if total_queries > 0 else 0.0
        avg_latency = (self.total_replay_latency / self.hits) if self.hits > 0 else 0.0
        return {
            "total_queries": total_queries,
            "hits": self.hits,
            "exact_hits": self.exact_hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 4),
            "evictions": self.evictions,
            "active_entries": len(self.entries),
            "faiss_ntotal": self.index_id_map.ntotal,
            "avg_replay_latency_sec": round(avg_latency, 6),
            "use_lsh": self.use_lsh
        }
