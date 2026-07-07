import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Optional, List
from ..models.schemas import Solution

class SemanticCache:
    """
    11. CACHE
    - store verified results
    - reuse if similarity >= 0.9
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", threshold: float = 0.9):
        self.model = SentenceTransformer(model_name)
        self.threshold = threshold
        self.index = faiss.IndexFlatL2(384) # Dim for MiniLM-L6
        self.solutions: List[Solution] = []
        self.intents: List[str] = []

    def add(self, intent: str, solution: Solution):
        embedding = self.model.encode([intent])[0]
        self.index.add(np.array([embedding]).astype("float32"))
        self.intents.append(intent)
        self.solutions.append(solution)

    def query(self, intent: str) -> Optional[Solution]:
        if not self.intents:
            return None
            
        embedding = self.model.encode([intent])[0]
        D, I = self.index.search(np.array([embedding]).astype("float32"), 1)
        
        # L2 distance to cosine similarity (approximate for normalized vectors)
        # For FlatL2 on normalized vectors: dist = 2 * (1 - sim) => sim = 1 - dist/2
        # MiniLM usually produces normalized or near-normalized embeddings
        distance = D[0][0]
        similarity = 1 - (distance / 2)
        
        if similarity >= self.threshold:
            return self.solutions[I[0][0]]
        
        return None
