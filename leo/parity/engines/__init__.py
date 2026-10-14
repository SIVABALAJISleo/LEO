"""
leo/parity/engines/__init__.py
==============================
Toggleable execution engines for the four contract workloads:
1. LLMInferenceEngine (speculative decoding + INT8/INT4 layer streaming)
2. RAGRetrievalEngine (vector search + semantic & exact cache)
3. TextEmbeddingsEngine (L3 cache-blocked tiling + low-rank projection)
4. TemporalRenderingEngine (tile reprojection + scene cut detection)
"""

from .llm_inference import LLMInferenceEngine
from .rag_retrieval import RAGRetrievalEngine
from .text_embeddings import TextEmbeddingsEngine
from .temporal_rendering import TemporalRenderingEngine

__all__ = [
    "LLMInferenceEngine",
    "RAGRetrievalEngine",
    "TextEmbeddingsEngine",
    "TemporalRenderingEngine",
]
