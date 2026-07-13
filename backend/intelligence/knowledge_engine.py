"""
backend/intelligence/knowledge_engine.py
Production-grade Knowledge Engine for LEO AI v∞.
Implements hybrid search, citation tracking, duplicate check, and relationship node graphs.
"""

import hashlib
import logging
import numpy as np
import re
from typing import Dict, Any, List, Tuple, Set

logger = logging.getLogger(__name__)

class KnowledgeGraph:
    """Extracts entities and constructs topological node relations from text."""
    def __init__(self):
        self.nodes: Set[str] = set()
        # Adjacency list: source -> list of (target, relationship)
        self.edges: Dict[str, List[Tuple[str, str]]] = {}

    def parse_and_add_relations(self, text: str) -> None:
        # Simple rule-based entity relation extraction using regex
        # Look for patterns like "A accelerates B", "A optimizes B", "A is a B", etc.
        patterns = [
            (r"(\b[A-Za-z0-9_\-\s]{2,15}\b)\s+(accelerates|optimizes|uses|implements|runs on|is a)\s+(\b[A-Za-z0-9_\-\s]{2,15}\b)", r"\2"),
            (r"(\b[A-Za-z0-9_\-\s]{2,15}\b)\s+(depends on|requires|needs)\s+(\b[A-Za-z0-9_\-\s]{2,15}\b)", r"\2")
        ]
        
        for pat, rel_expr in patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            for src, rel, tgt in matches:
                src_node = src.strip().title()
                tgt_node = tgt.strip().title()
                relationship = rel.strip().lower()
                
                self.nodes.add(src_node)
                self.nodes.add(tgt_node)
                if src_node not in self.edges:
                    self.edges[src_node] = []
                # Prevent duplicate relations
                if (tgt_node, relationship) not in self.edges[src_node]:
                    self.edges[src_node].append((tgt_node, relationship))

    def get_relationship_map(self) -> Dict[str, List[Dict[str, str]]]:
        res = {}
        for src, edges in self.edges.items():
            res[src] = [{"target": tgt, "relation": rel} for tgt, rel in edges]
        return res


class KnowledgeEngine:
    """Hybrid indexing, Jaccard duplicate detection, and search query processor."""
    def __init__(self):
        # List of indexed document chunks: List[Dict[str, Any]]
        # Structure: {"chunk_id": str, "source": str, "text": str, "vector": np.ndarray}
        self.chunks: List[Dict[str, Any]] = []
        self.vocab: List[str] = []
        self.graph = KnowledgeGraph()
        
        # Vocab frequency database
        self.vocab_index: Dict[str, List[int]] = {}

    def add_document(self, source_name: str, text: str) -> int:
        """Process, clean, chunk, and index text documents."""
        # 1. Word frequency analysis for incremental vocab expansion
        words = re.findall(r"\b\w{3,15}\b", text.lower())
        for w in words:
            if w not in self.vocab:
                self.vocab.append(w)
                
        # 2. Chunking
        from backend.intelligence.document_processor import DocumentProcessor
        dp = DocumentProcessor()
        cleaned = dp.clean_text(text)
        new_chunks = dp.chunk_text(cleaned, max_chunk_size=150, overlap=30)
        
        added_count = 0
        for idx, chunk_text in enumerate(new_chunks):
            # Check for duplicates using Jaccard Similarity index
            if self._is_duplicate(chunk_text):
                continue
                
            chunk_id = hashlib.sha256(f"{source_name}_{idx}_{chunk_text[:30]}".encode()).hexdigest()[:16]
            chunk_vec = self._vectorize(chunk_text)
            
            self.chunks.append({
                "chunk_id": chunk_id,
                "source": source_name,
                "text": chunk_text,
                "vector": chunk_vec,
                "index": idx
            })
            
            # Extract relation graph
            self.graph.parse_and_add_relations(chunk_text)
            added_count += 1
            
        return added_count

    def _is_duplicate(self, text: str, threshold: float = 0.8) -> bool:
        """Determines if a chunk is structurally redundant using Jaccard index similarity."""
        words_new = set(re.findall(r"\w+", text.lower()))
        if not words_new:
            return True
            
        for chunk in self.chunks:
            words_ref = set(re.findall(r"\w+", chunk["text"].lower()))
            intersection = words_new.intersection(words_ref)
            union = words_new.union(words_ref)
            sim = len(intersection) / len(union)
            if sim >= threshold:
                return True
        return False

    def _vectorize(self, text: str) -> np.ndarray:
        """Generates a TF-IDF weighted vector representation of text chunk."""
        vec = np.zeros(len(self.vocab), dtype=np.float32)
        q_words = re.findall(r"\b\w{3,15}\b", text.lower())
        for w in q_words:
            if w in self.vocab:
                idx = self.vocab.index(w)
                vec[idx] += 1.0
        
        # Soft TF-IDF normalization
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Executes hybrid vector similarity and keyword checks, returning citations."""
        if not self.chunks:
            return []
            
        q_vec = self._vectorize(query)
        results = []
        
        for chunk in self.chunks:
            # Cosine similarity metric
            sim = 0.0
            chunk_vec = chunk["vector"]
            # Pad chunk vector if vocab expanded incrementally
            if len(chunk_vec) < len(self.vocab):
                padded = np.zeros(len(self.vocab), dtype=np.float32)
                padded[:len(chunk_vec)] = chunk_vec
                chunk["vector"] = padded
                chunk_vec = padded
                
            norm_q = np.linalg.norm(q_vec)
            norm_c = np.linalg.norm(chunk_vec)
            if norm_q > 0 and norm_c > 0:
                sim = np.dot(q_vec, chunk_vec) / (norm_q * norm_c)
                
            # Score scaling: prioritize exact matching keyword boost
            keyword_match_count = sum(1 for w in query.lower().split() if w in chunk["text"].lower())
            score = float(sim) + (keyword_match_count * 0.05)
            
            results.append((score, chunk))
            
        # Sort and return top-k matches
        results.sort(key=lambda x: x[0], reverse=True)
        
        citations = []
        for score, chunk in results[:top_k]:
            if score > 0.05:  # Relevance cutoff threshold
                citations.append({
                    "chunk_id": chunk["chunk_id"],
                    "source": chunk["source"],
                    "index": chunk["index"],
                    "text": chunk["text"],
                    "score": round(score, 4),
                    "citation": f"[Source: {chunk['source']} - Block {chunk['index']}]"
                })
        return citations
