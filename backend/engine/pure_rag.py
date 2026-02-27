
import numpy as np
import json
import os

class PureRagEngine:
    """
    Pure Python/Numpy RAG Engine.
    Achieves semantic search without Faiss or Torch by using Cosine Similarity on a pre-computed local embedding dict.
    """
    def __init__(self):
        self.knowledge_base = [
            {"text": "HYPER uses Software-First Compute Substitution to achieve GPU-level results on CPU.", "metadata": {"source": "core_docs"}},
            {"text": "Semantic Cache reduces redundant computation by mapping queries to previous results.", "metadata": {"source": "opt_docs"}},
            {"text": "Probabilistic structures like Bloom Filters and HLL manage state at O(1) space.", "metadata": {"source": "prob_docs"}},
            {"text": "The MoE Router decomposes queries into atomic subtasks for specialized experts.", "metadata": {"source": "arch_docs"}},
            {"text": "Perceptual Media pipelines use neural upscaling to mask low-resolution compute.", "metadata": {"source": "vision_docs"}},
            {"text": "The capital of France is Paris.", "metadata": {"source": "geo"}},
            {"text": "William Shakespeare wrote Romeo and Juliet.", "metadata": {"source": "lit"}},
            {"text": "The chemical symbol for gold is Au.", "metadata": {"source": "chem"}},
            {"text": "Mars is known as the Red Planet.", "metadata": {"source": "space"}},
            {"text": "World War II ended in 1945.", "metadata": {"source": "history"}},
            {"text": "Mount Everest is the tallest mountain in the world.", "metadata": {"source": "geo"}},
            {"text": "Leonardo da Vinci painted the Mona Lisa.", "metadata": {"source": "art"}},
            {"text": "The Pacific Ocean is the largest ocean on Earth.", "metadata": {"source": "geo"}},
            {"text": "Hydrogen has the atomic number 1.", "metadata": {"source": "chem"}},
            {"text": "Sir Isaac Newton discovered gravity.", "metadata": {"source": "science"}},
        ]
        
        # Simple word-weighting "mock" embeddings for demonstration without external LLM
        # In a real substitution, we'd use a small 10MB local model (e.g. fastText)
        self.vocab = sorted(list(set(" ".join([k["text"].lower() for k in self.knowledge_base]).split())))
        self.vectors = [self._vectorize(k["text"]) for k in self.knowledge_base]

    def _vectorize(self, text):
        words = text.lower().split()
        vector = np.zeros(len(self.vocab))
        for word in words:
            if word in self.vocab:
                vector[self.vocab.index(word)] += 1
        norm = np.linalg.norm(vector)
        return vector / norm if norm > 0 else vector

    def query(self, text, k=3):
        query_vec = self._vectorize(text)
        similarities = []
        for i, doc_vec in enumerate(self.vectors):
            similarity = np.dot(query_vec, doc_vec)
            similarities.append((similarity, self.knowledge_base[i]))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[0], reverse=True)
        results = [{"score": float(s), "text": d["text"], "metadata": d["metadata"]} for s, d in similarities[:k]]
        
        return {
            "query": text,
            "results": results,
            "engine": "PurePython-VectorSearch",
            "latency_type": "O(N)_linear_scan"
        }

if __name__ == "__main__":
    engine = PureRagEngine()
    test = engine.query("How does HYPER save compute?")
    print(json.dumps(test, indent=2))
