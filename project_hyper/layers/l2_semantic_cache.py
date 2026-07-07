import faiss

from sentence_transformers import SentenceTransformer
from typing import Optional, List, Dict

class SemanticCache:
    """
    Layer 2: Semantic Cache
    Similarity search based on meaning. Target: 40-70% coverage.
    """
    def __init__(self, threshold: float = 0.95):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dimension)
        self.threshold = threshold
        self.metadata: List[Dict[str, str]] = []

    def get(self, query: str) -> Optional[str]:
        if self.index.ntotal == 0: return None
        
        embedding = self.model.encode([query])[0].astype('float32')
        faiss.normalize_L2(embedding.reshape(1, -1))
        
        scores, indices = self.index.search(embedding.reshape(1, -1), 1)
        
        if scores[0][0] >= self.threshold:
            return self.metadata[indices[0][0]]["response"]
        return None

    def add(self, query: str, response: str):
        embedding = self.model.encode([query])[0].astype('float32')
        faiss.normalize_L2(embedding.reshape(1, -1))
        
        self.index.add(embedding.reshape(1, -1))
        self.metadata.append({"query": query, "response": response})

if __name__ == "__main__":
    cache = SemanticCache()
    cache.add("What is the capital of France?", "Paris is the capital of France.")
    print("Similar Hit: {}".format(cache.get("Tell me France's capital city")))
