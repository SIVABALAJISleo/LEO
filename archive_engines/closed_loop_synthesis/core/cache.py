import faiss
import os
import json
import logging
from typing import Optional
from sentence_transformers import SentenceTransformer
from archive_engines.closed_loop_synthesis.config import settings

logger = logging.getLogger(__name__)

class SynthesisCache:
    """
    Zero-Compute Cache Layer.
    Uses semantic search to reuse verified solutions.
    """
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME, device='cpu')
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        if os.path.exists(settings.CACHE_INDEX_PATH) and os.path.exists(settings.CACHE_METADATA_PATH):
            try:
                self.index = faiss.read_index(settings.CACHE_INDEX_PATH)
                with open(settings.CACHE_METADATA_PATH, 'r') as f:
                    self.metadata = json.load(f)
            except Exception as e:
                logger.error(f"Error loading cache: {e}")
                self._init_empty()
        else:
            self._init_empty()

    def _init_empty(self):
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []

    def lookup(self, task: str) -> Optional[str]:
        if self.index.ntotal == 0:
            return None

        embedding = self.model.encode([task], convert_to_numpy=True)
        faiss.normalize_L2(embedding)
        
        scores, indices = self.index.search(embedding, k=1)
        
        if indices[0][0] != -1:
            score = float(scores[0][0])
            if score >= settings.CACHE_THRESHOLD:
                return self.metadata[indices[0][0]]["code"]
        
        return None

    def store(self, task: str, code: str):
        embedding = self.model.encode([task], convert_to_numpy=True)
        faiss.normalize_L2(embedding)
        
        self.index.add(embedding)
        self.metadata.append({"task": task, "code": code})
        self._save()

    def _save(self):
        try:
            os.makedirs(os.path.dirname(settings.CACHE_INDEX_PATH), exist_ok=True)
            faiss.write_index(self.index, settings.CACHE_INDEX_PATH)
            with open(settings.CACHE_METADATA_PATH, 'w') as f:
                json.dump(self.metadata, f)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
