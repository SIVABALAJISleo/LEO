import faiss
import numpy as np
import os
import json
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class RetrievalEngine:
    """
    Local FAISS-based RAG for providing sparse context to experts.
    """
    def __init__(self, dimension: int = 384, db_path: str = "retrieval/faiss_index.bin"):
        self.dimension = dimension
        self.db_path = db_path
        self.metadata_path = db_path.replace(".bin", "_meta.json")
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata: List[Dict] = []
        
        if os.path.exists(self.db_path):
            self.index = faiss.read_index(self.db_path)
            with open(self.metadata_path, "r") as f:
                self.metadata = json.load(f)
            logger.info(f"Retrieval DB Loaded: {len(self.metadata)} documents")

    def add_documents(self, embeddings: np.ndarray, meta_list: List[Dict]):
        self.index.add(embeddings.astype("float32"))
        self.metadata.extend(meta_list)
        faiss.write_index(self.index, self.db_path)
        with open(self.metadata_path, "w") as f:
            json.dump(self.metadata, f)

    def search(self, query_emb: np.ndarray, k: int = 5) -> List[Dict]:
        if self.index.ntotal == 0: return []
        distances, indices = self.index.search(query_emb.astype("float32").reshape(1, -1), k)
        return [self.metadata[idx] for idx in indices[0] if idx != -1]
