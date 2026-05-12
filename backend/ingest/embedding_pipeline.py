import logging
import numpy as np
from typing import List
from backend.intelligence.router import HAS_TRANSFORMERS, SentenceTransformer, TFIDFLite

logger = logging.getLogger(__name__)

class EmbeddingPipeline:
    """
    Generates embeddings for document chunks using the HYPER standardized model.
    """
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2') if HAS_TRANSFORMERS else TFIDFLite(384)

    def get_embeddings(self, chunks: List[str]) -> np.ndarray:
        logger.info(f"generating_embeddings: count={len(chunks)}")
        # Ensure output is always numpy ndarray even if Tensor is returned by torch backend
        embeddings = self.model.encode(chunks)
        return np.asarray(embeddings).astype('float32')

global_embedding_pipeline = EmbeddingPipeline()
