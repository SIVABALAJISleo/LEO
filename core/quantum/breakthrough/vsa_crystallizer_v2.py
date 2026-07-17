"""
LEO VSA Crystallizer v2
Pre-computes and maps knowledge graphs into a 10,000-dimensional binary hypervector space.
Inference for recurring patterns becomes a single dot product match.
"""
import torch
import numpy as np
from typing import Dict, List, Tuple, Optional

class VSACrystallizerV2:
    """
    Kanerva-Tesla Hyperdimensional Vector-Symbolic Architecture Engine.
    Encodes text inputs into 10,000-D binary hypervectors and resolves queries via dot product logic.
    """
    
    def __init__(self, dim: int = 10000, threshold: float = 0.70):
        self.dim = dim
        self.threshold = threshold
        self.concept_bank = {} # Name -> Hypervector
        self.knowledge_base = torch.zeros(self.dim, dtype=torch.float32)
        self.crystallized_mappings = {} # Query Hypervector -> Result string
        
    def generate_hypervector(self) -> torch.Tensor:
        """Generates a random 10,000-dimensional binary hypervector {0, 1}"""
        # Equal probability of 0 or 1
        probs = torch.full((self.dim,), 0.5)
        return torch.bernoulli(probs)
        
    def get_or_create_concept(self, name: str) -> torch.Tensor:
        """Fetches or registers a unique concept vector"""
        if name not in self.concept_bank:
            self.concept_bank[name] = self.generate_hypervector()
        return self.concept_bank[name]

    def bind(self, hv_a: torch.Tensor, hv_b: torch.Tensor) -> torch.Tensor:
        """Bind operator (XOR for binary hypervectors)"""
        # XOR operator binds features cleanly
        return torch.bitwise_xor(hv_a.to(torch.int8), hv_b.to(torch.int8)).to(torch.float32)

    def bundle(self, hvs: List[torch.Tensor]) -> torch.Tensor:
        """Bundle operator (majority vote thresholding)"""
        stacked = torch.stack(hvs, dim=0)
        sums = torch.sum(stacked, dim=0)
        threshold_val = len(hvs) / 2.0
        return torch.where(sums > threshold_val, torch.ones_like(sums), torch.zeros_like(sums))

    def similarity(self, hv_a: torch.Tensor, hv_b: torch.Tensor) -> float:
        """Cosine similarity equivalent for binary hypervectors (Hamming similarity)"""
        # Calculate matching bits
        matches = torch.eq(hv_a, hv_b).sum().item()
        return matches / self.dim

    def crystallize_query(self, query: str, answer: str):
        """Pre-computes and indexes a query/answer relationship as a VSA hypervector mapping"""
        hv_query = self._encode_text_to_hypervector(query)
        self.crystallized_mappings[query] = {
            'vector': hv_query,
            'answer': answer
        }

    def query_crystallized(self, query: str) -> Tuple[Optional[str], float]:
        """Resolves queries by running a single dot product match against VSA space"""
        if not self.crystallized_mappings:
            return None, 0.0
            
        hv_query = self._encode_text_to_hypervector(query)
        
        best_match = None
        best_sim = 0.0
        
        for q_text, val in self.crystallized_mappings.items():
            sim = self.similarity(hv_query, val['vector'])
            if sim > best_sim:
                best_sim = sim
                best_match = val['answer']
                
        if best_sim >= self.threshold:
            return best_match, best_sim
            
        return None, best_sim

    def _encode_text_to_hypervector(self, text: str) -> torch.Tensor:
        """Helper to convert token lists or text into a composite hypervector via bundling"""
        words = text.lower().strip().split()
        if not words:
            return self.generate_hypervector()
            
        vectors = []
        for i, word in enumerate(words):
            # Create a vector bound to positional index
            val_vec = self.get_or_create_concept(word)
            pos_vec = self.get_or_create_concept(f"pos_{i}")
            vectors.append(self.bind(val_vec, pos_vec))
            
        return self.bundle(vectors)
