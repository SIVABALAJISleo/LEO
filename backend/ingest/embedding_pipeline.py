import os
import logging
import numpy as np
from typing import List, Optional

logger = logging.getLogger(__name__)

# ── Lazy Singleton Pattern ──────────────────────────────────────────────────
# Model is never loaded at import time. It is only constructed on first use.
# This prevents test collection from hanging on HuggingFace network requests
# when running in offline / CI environments.

_pipeline_instance: Optional["EmbeddingPipeline"] = None


def _make_encoder():
    """Build the best available encoder without blocking at import time."""
    # Respect explicit offline flags set by tests or CI environments
    offline = (
        os.getenv("TRANSFORMERS_OFFLINE", "0") == "1"
        or os.getenv("HF_DATASETS_OFFLINE", "0") == "1"
        or os.getenv("LEO_OFFLINE", "0") == "1"
    )
    if offline:
        from backend.intelligence.router import TFIDFLite
        logger.info("embedding_pipeline: offline mode -> TFIDFLite fallback")
        return TFIDFLite(384)

    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("embedding_pipeline: SentenceTransformer loaded successfully")
        return model
    except Exception as e:
        from backend.intelligence.router import TFIDFLite
        logger.warning(f"embedding_pipeline: SentenceTransformer unavailable ({e}) -> TFIDFLite fallback")
        return TFIDFLite(384)


class EmbeddingPipeline:
    """
    Generates embeddings for document chunks using the best available model.

    Model selection order:
      1. SentenceTransformer all-MiniLM-L6-v2  (online / cached)
      2. TFIDFLite                              (offline / CI fallback)
    """

    def __init__(self):
        # Lazy — _encoder is only initialised on first call to get_embeddings
        self._encoder = None

    def _get_encoder(self):
        if self._encoder is None:
            self._encoder = _make_encoder()
        return self._encoder

    def get_embeddings(self, chunks: List[str]) -> np.ndarray:
        logger.info(f"generating_embeddings: count={len(chunks)}")
        encoder = self._get_encoder()
        embeddings = encoder.encode(chunks)
        return np.asarray(embeddings).astype("float32")


def get_global_pipeline() -> EmbeddingPipeline:
    """Return the process-wide singleton EmbeddingPipeline (lazy-initialised)."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = EmbeddingPipeline()
    return _pipeline_instance


# Backwards-compatible alias — code that imports `global_embedding_pipeline`
# directly still works, but the model is no longer loaded at import time.
class _LazyPipelineProxy:
    """Transparent proxy so ``global_embedding_pipeline.get_embeddings(...)``
    works without constructing the pipeline at import time."""
    def __getattr__(self, name):
        return getattr(get_global_pipeline(), name)


global_embedding_pipeline = _LazyPipelineProxy()  # type: ignore[assignment]
