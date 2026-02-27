import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from app.core.config import settings

class VectorService:
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.dimension = 384 # all-MiniLM-L6-v2 dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = [] # Stores raw text linked to index
        
        # Load local index if exists
        if os.path.exists(settings.FAISS_INDEX_PATH):
            self.index = faiss.read_index(settings.FAISS_INDEX_PATH)

    def add_documents(self, texts: list):
        embeddings = self.model.encode(texts)
        self.index.add(np.array(embeddings).astype('float32'))
        self.documents.extend(texts)

    def search(self, query: str, k: int = 3):
        embedding = self.model.encode([query])
        distances, indices = self.index.search(np.array(embedding).astype('float32'), k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                results.append({
                    "text": self.documents[idx],
                    "score": float(distances[0][i])
                })
        return results

vector_service = VectorService()
