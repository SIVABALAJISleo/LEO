import numpy as np
import pickle
import os
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

class LSHEngine:
    """
    Locality-Sensitive Hashing (LSH) Engine.
    Replaces FAISS/HNSW with ultra-fast, pure-CPU hashing.
    Achieves O(1) retrieval complexity by hashing dense embeddings into integer buckets.
    """
    def __init__(self, vector_dim: int, num_hash_tables: int = 10, hash_size: int = 16):
        self.vector_dim = vector_dim
        self.num_hash_tables = num_hash_tables
        self.hash_size = hash_size
        
        # We generate random hyperplanes for Random Projection LSH
        # Each table has `hash_size` hyperplanes.
        # Shape: (num_hash_tables, hash_size, vector_dim)
        np.random.seed(42) # Deterministic for now, could be dynamic
        self.hyperplanes = np.random.randn(num_hash_tables, hash_size, vector_dim).astype(np.float32)
        
        # The hash tables: list of dicts mapping integer hash -> list of (doc_id, vector)
        self.hash_tables = [{} for _ in range(num_hash_tables)]
        
        # Document store
        self.doc_store = {}
        self.doc_vectors = {}

    def _compute_hash(self, vector: np.ndarray) -> np.ndarray:
        """
        Projects a vector across the hyperplanes and returns a bitmask integer for each table.
        Input: (vector_dim,)
        Output: (num_hash_tables,) array of integers
        """
        # (num_hash_tables, hash_size, vector_dim) @ (vector_dim,) -> (num_hash_tables, hash_size)
        projections = np.dot(self.hyperplanes, vector)
        
        # Boolean array where dot product > 0
        bits = projections > 0
        
        # Convert boolean array to integer hash using bitwise shift
        # This is where the CPU blazes through using pure bitwise logic.
        hashes = np.zeros(self.num_hash_tables, dtype=np.uint32)
        for i in range(self.hash_size):
            hashes |= (bits[:, i].astype(np.uint32) << i)
            
        return hashes

    def add(self, doc_id: str, vector: np.ndarray, text: str):
        """Adds a document to the LSH engine."""
        self.doc_store[doc_id] = text
        self.doc_vectors[doc_id] = vector
        
        hashes = self._compute_hash(vector)
        for table_idx, h in enumerate(hashes):
            if h not in self.hash_tables[table_idx]:
                self.hash_tables[table_idx][h] = []
            self.hash_tables[table_idx][h].append(doc_id)

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[str, str, float]]:
        """
        O(1) retrieval using hash buckets, followed by exact distance on the collision subset.
        """
        hashes = self._compute_hash(query_vector)
        
        # Find candidate documents that share at least one hash bucket
        candidates = set()
        for table_idx, h in enumerate(hashes):
            if h in self.hash_tables[table_idx]:
                candidates.update(self.hash_tables[table_idx][h])
                
        if not candidates:
            return []
            
        # Compute exact Cosine Similarity ONLY on the O(1) fetched candidates
        candidate_list = list(candidates)
        cand_vectors = np.stack([self.doc_vectors[c] for c in candidate_list])
        
        # Cosine similarity: (A dot B) / (||A|| ||B||)
        dot_products = np.dot(cand_vectors, query_vector)
        norms = np.linalg.norm(cand_vectors, axis=1) * np.linalg.norm(query_vector)
        similarities = dot_products / (norms + 1e-9)
        
        # Sort by similarity
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            doc_id = candidate_list[idx]
            results.append((doc_id, self.doc_store[doc_id], float(similarities[idx])))
            
        return results

    def save(self, filepath: str):
        with open(filepath, 'wb') as f:
            pickle.dump({
                'hyperplanes': self.hyperplanes,
                'hash_tables': self.hash_tables,
                'doc_store': self.doc_store,
                'doc_vectors': self.doc_vectors
            }, f)
            
    def load(self, filepath: str):
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.hyperplanes = data['hyperplanes']
                self.hash_tables = data['hash_tables']
                self.doc_store = data['doc_store']
                self.doc_vectors = data['doc_vectors']
