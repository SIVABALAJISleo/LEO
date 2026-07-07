import faiss
from typing import Optional
from sentence_transformers import SentenceTransformer

class PerfectCache:
    def __init__(self, index_path: str = "data/perfect_cache/index.faiss"):
        self.index_path = index_path
        self.model = SentenceTransformer("all-MiniLM-L6-v2", device='cpu')
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.metadata = []
        self.index = faiss.IndexFlatIP(self.dimension)

    def lookup(self, task: str) -> Optional[str]:
        if self.index.ntotal == 0: return None
        embedding = self.model.encode([task], convert_to_numpy=True)
        faiss.normalize_L2(embedding)
        scores, indices = self.index.search(embedding, k=1)
        if indices[0][0] != -1 and scores[0][0] >= 0.92:
            return self.metadata[indices[0][0]]["code"]
        return None

    def store(self, task: str, code: str):
        embedding = self.model.encode([task], convert_to_numpy=True)
        faiss.normalize_L2(embedding)
        self.index.add(embedding)
        self.metadata.append({"task": task, "code": code})
