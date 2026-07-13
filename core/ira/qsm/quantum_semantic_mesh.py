"""
Quantum Semantic Mesh (QSM).
Provides O(1) semantic lookups for bypassing standard AI inference.
"""
import os
import json
import time
import numpy as np
from typing import Optional, Tuple, List, Dict
from collections import defaultdict

from core.ira.shared.config import QSMConfig
from core.ira.shared.hashing import FastHashEngine
from core.ira.shared.logging import IRALogger
from core.ira.shared.metrics import get_metric_collector
from core.ira.shared.timing import PrecisionTimer

class QuantumSemanticMesh:
    def __init__(self, config: QSMConfig = None):
        self.config = config or QSMConfig()
        
        # Initialize hash tables as defaultdict(list)
        self.tables = [defaultdict(list) for _ in range(self.config.num_tables)]
        self.response_store = {}
        
        # Generate hyperplanes for each table with a different random seed
        self.hyperplanes = []
        for i in range(self.config.num_tables):
            hp = FastHashEngine.generate_hyperplanes(
                self.config.embedding_dim, 
                self.config.hash_bits, 
                seed=42 + i
            )
            self.hyperplanes.append(hp)
            
        os.makedirs(self.config.cache_dir, exist_ok=True)
        
        self.auto_save_counter = 0
        
        self.logger = IRALogger.get_logger("qsm")
        self.metrics = get_metric_collector().system.get_or_create_pillar("qsm")
        
        if self.config.enable_persistence:
            self._load_persistent_cache()

    def _build_persistent_path(self) -> str:
        return os.path.join(self.config.cache_dir, self.config.persistence_file)

    def _load_persistent_cache(self) -> None:
        path = self._build_persistent_path()
        if not os.path.exists(path):
            return
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            entries = data.get("entries", {})
            for entry_id, entry_data in entries.items():
                if "embedding" not in entry_data:
                    self.logger.warning(f"Skipping corrupted entry {entry_id}")
                    continue
                    
                # Reconstruct embedding
                emb = np.array(entry_data["embedding"], dtype=np.float32)
                
                # Rebuild all hash tables
                for table_idx in range(self.config.num_tables):
                    bucket_key = self._hash_to_bucket(emb, table_idx)
                    self.tables[table_idx][bucket_key].append(entry_id)
                    
                self.response_store[entry_id] = entry_data
                
            self.logger.info(f"Loaded {len(entries)} entries from persistent cache.")
        except json.JSONDecodeError:
            self.logger.warning("Failed to decode persistent cache. Starting fresh.")
        except Exception as e:
            self.logger.warning(f"Error loading persistent cache: {e}")

    def _persist_cache(self) -> None:
        path = self._build_persistent_path()
        tmp_path = path + ".tmp"
        
        try:
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump({"entries": self.response_store}, f, ensure_ascii=False)
            
            # Atomic replace
            os.replace(tmp_path, path)
            self.logger.info(f"Persisted {len(self.response_store)} entries to cache.")
        except Exception as e:
            self.logger.warning(f"Failed to persist cache: {e}")

    def _get_embedding(self, text: str) -> np.ndarray:
        timer = PrecisionTimer("get_embedding").start()
        emb = FastHashEngine.ngram_hash_embedding(text, self.config.embedding_dim)
        IRALogger.log_performance("qsm", "get_embedding", timer.stop())
        return emb

    def _hash_to_bucket(self, embedding: np.ndarray, table_idx: int) -> str:
        return FastHashEngine.lsh_hash(embedding, self.hyperplanes[table_idx])

    def store(self, query: str, response: str, metadata: dict = None) -> str:
        timer = PrecisionTimer("store").start()
        
        entry_id = FastHashEngine.sha256_short(query)
        embedding = self._get_embedding(query)
        
        for table_idx in range(self.config.num_tables):
            bucket_key = self._hash_to_bucket(embedding, table_idx)
            self.tables[table_idx][bucket_key].append(entry_id)
            
        self.response_store[entry_id] = {
            "query": query,
            "response": response,
            "metadata": metadata or {},
            "embedding": embedding.tolist(),
            "access_count": 0,
            "created_at": time.time(),
            "last_accessed_at": time.time()
        }
        
        self.auto_save_counter += 1
        if self.auto_save_counter >= self.config.auto_save_interval:
            self._persist_cache()
            self.auto_save_counter = 0
            
        elapsed = timer.stop()
        self.metrics.record_call(is_hit=False, latency_ms=elapsed)
        return entry_id

    def retrieve(self, query: str, threshold: float = None) -> Optional[Tuple[str, float]]:
        timer = PrecisionTimer("retrieve").start()
        if threshold is None:
            threshold = self.config.lookup_threshold
            
        embedding = self._get_embedding(query)
        candidate_ids = set()
        
        for table_idx in range(self.config.num_tables):
            bucket_key = self._hash_to_bucket(embedding, table_idx)
            if bucket_key in self.tables[table_idx]:
                candidate_ids.update(self.tables[table_idx][bucket_key])
                
        if not candidate_ids:
            elapsed = timer.stop()
            self.metrics.record_call(is_hit=False, latency_ms=elapsed)
            return None
            
        best_match = None
        best_score = -1.0
        
        for candidate_id in candidate_ids:
            entry = self.response_store.get(candidate_id)
            if not entry:
                continue
                
            stored_emb = np.array(entry["embedding"], dtype=np.float32)
            score = float(np.dot(embedding, stored_emb))
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = candidate_id
                
        if best_match:
            entry = self.response_store[best_match]
            entry["access_count"] += 1
            entry["last_accessed_at"] = time.time()
            
            elapsed = timer.stop()
            self.metrics.record_call(is_hit=True, latency_ms=elapsed)
            return (entry["response"], best_score)
            
        elapsed = timer.stop()
        self.metrics.record_call(is_hit=False, latency_ms=elapsed)
        return None

    def delete(self, entry_id: str) -> bool:
        if entry_id not in self.response_store:
            return False
            
        entry = self.response_store[entry_id]
        embedding = np.array(entry["embedding"], dtype=np.float32)
        
        for table_idx in range(self.config.num_tables):
            bucket_key = self._hash_to_bucket(embedding, table_idx)
            if bucket_key in self.tables[table_idx]:
                if entry_id in self.tables[table_idx][bucket_key]:
                    self.tables[table_idx][bucket_key].remove(entry_id)
                    
        del self.response_store[entry_id]
        if self.config.enable_persistence:
            self._persist_cache()
            
        return True

    def clear(self) -> None:
        self.tables = [defaultdict(list) for _ in range(self.config.num_tables)]
        self.response_store.clear()
        
        if self.config.enable_persistence:
            path = self._build_persistent_path()
            if os.path.exists(path):
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump({"entries": {}}, f)
                except Exception:
                    pass
                    
        self.logger.info("Cleared all QSM tables and cache.")

    def contains(self, query: str, threshold: float = None) -> bool:
        return self.retrieve(query, threshold) is not None
