import logging
import math
from collections import Counter
from typing import List, Dict, Tuple
import numpy as np

logger = logging.getLogger(__name__)

class BM25Engine:
    """Lightweight pure-python implementation of Okapi BM25 for keyword retrieval."""
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.document_count = 0
        self.avgdl = 0.0
        self.doc_lengths = []
        self.doc_freqs = []
        self.idf = {}
        self.corpus = []

    def add_document(self, doc_id: str, text: str):
        words = text.lower().split()
        self.corpus.append((doc_id, text))
        self.doc_lengths.append(len(words))
        
        freq_dict = Counter(words)
        self.doc_freqs.append(freq_dict)
        
        for word in freq_dict:
            if word not in self.idf:
                self.idf[word] = 0
            self.idf[word] += 1
            
        self.document_count += 1
        self.avgdl = sum(self.doc_lengths) / self.document_count
        
        # Recompute IDF
        for word, freq in self.idf.items():
            # BM25 IDF formulation
            self.idf[word] = math.log(1 + (self.document_count - freq + 0.5) / (freq + 0.5))

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, str, float]]:
        query_words = query.lower().split()
        scores = []
        
        for idx in range(self.document_count):
            score = 0.0
            doc_len = self.doc_lengths[idx]
            freqs = self.doc_freqs[idx]
            
            for word in query_words:
                if word not in freqs:
                    continue
                qf = freqs[word]
                numerator = self.idf.get(word, 0) * qf * (self.k1 + 1)
                denominator = qf + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
                score += numerator / denominator
                
            scores.append((self.corpus[idx][0], self.corpus[idx][1], score))
            
        # Sort by BM25 score descending
        scores.sort(key=lambda x: x[2], reverse=True)
        return scores[:top_k]

class HybridRetrievalEngine:
    """
    Subsystem 14: Hybrid Retrieval Engine.
    Fuses BM25 (sparse keyword match) with Dense Vector similarity.
    """
    def __init__(self):
        self.bm25 = BM25Engine()
        self.dense_vectors = {}
        
    def add_document(self, doc_id: str, text: str, embedding: np.ndarray):
        self.bm25.add_document(doc_id, text)
        self.dense_vectors[doc_id] = embedding
        
    def search(self, query: str, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict[str, str]]:
        # 1. Get BM25 scores
        bm25_results = self.bm25.search(query, top_k=top_k*2) # Fetch extra for reranking
        
        # 2. Compute Dense Vector scores for the BM25 candidates (Reranking Phase)
        fused_results = []
        for doc_id, text, bm_score in bm25_results:
            doc_vec = self.dense_vectors.get(doc_id)
            if doc_vec is not None:
                # Cosine Similarity
                sim = np.dot(query_embedding, doc_vec) / (np.linalg.norm(query_embedding) * np.linalg.norm(doc_vec) + 1e-9)
                
                # Hybrid Reciprocal Rank Fusion (RRF) - simplified to normalized sum for prototype
                # We boost semantic similarity significantly
                hybrid_score = (sim * 0.7) + (bm_score * 0.05) # Adjust weights as needed
                fused_results.append({
                    "doc_id": doc_id,
                    "text": text,
                    "hybrid_score": hybrid_score,
                    "bm25_score": bm_score,
                    "dense_score": sim
                })
                
        # Sort by final hybrid score
        fused_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return fused_results[:top_k]
