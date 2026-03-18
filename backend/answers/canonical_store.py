"""
Canonical Answer System
One optimized answer per concept. All similar queries reuse it.
This is the HIGHEST PRIORITY bypass layer — checked before everything else.
Storing here means zero compute for that concept forever.
"""
import hashlib
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Pre-seeded canonical answers for high-frequency AI/computing concepts
SEED_CANONICALS = {
    "definition#RAG": "Retrieval-Augmented Generation (RAG) is an AI technique that retrieves relevant documents before generating responses, significantly improving accuracy and reducing hallucinations in large language models.",
    "definition#LLM": "A Large Language Model (LLM) is a neural network trained on massive text datasets to understand, generate, and reason about human language at scale.",
    "definition#AI": "Artificial Intelligence (AI) is the simulation of human cognitive functions by computer systems, encompassing learning, reasoning, problem-solving, perception, and language understanding.",
    "definition#ML": "Machine Learning (ML) is a subset of AI where systems automatically learn and improve from data without being explicitly programmed for each task.",
    "definition#GPU": "A Graphics Processing Unit (GPU) is a specialized processor designed for parallel computation, widely used for AI training and inference due to its massive parallelism.",
    "definition#KV": "Key-Value (KV) Cache stores intermediate transformer computation states (keys and values) to avoid recomputing them for repeated or similar prompts, reducing latency significantly.",
    "definition#API": "An Application Programming Interface (API) is a contract between software components that defines how they communicate, including available endpoints, data formats, and authentication requirements.",
    "definition#PPE": "Predictive Precomputation Engine (PPE) pre-generates answers for anticipated user queries before they are asked, achieving near-zero latency for common questions.",
    "definition#CACHE": "A cache is a high-speed storage layer that stores frequently accessed data to reduce latency and compute cost for repeated requests.",
    "definition#DOCKER": "Docker is a containerization platform that packages applications and their dependencies into portable containers, ensuring consistent execution across environments.",
    "definition#KUBERNETES": "Kubernetes (K8s) is an open-source container orchestration system that automates deployment, scaling, and management of containerized applications.",
    "definition#REDIS": "Redis is an in-memory data structure store used as a cache, message broker, and database, prized for its sub-millisecond read/write performance.",
    "definition#TRANSFORMER": "The Transformer is a deep learning architecture based on self-attention mechanisms, forming the foundation of modern LLMs like GPT, BERT, and T5.",
    "definition#VECTOR": "A vector database stores high-dimensional numerical representations (embeddings) of data, enabling fast semantic similarity search for AI applications.",
    "definition#EMBEDDING": "An embedding is a numerical vector representation of text, images, or other data that captures semantic meaning in a form machines can compare and compute.",
}


class CanonicalStore:
    """
    Stores exactly ONE optimized answer per `shape_key` (intent#entity).
    All queries that resolve to the same shape reuse this single answer.
    """

    def __init__(self):
        self._store: Dict[str, str] = dict(SEED_CANONICALS)
        self._hit_count: Dict[str, int] = {k: 0 for k in SEED_CANONICALS}

    def lookup(self, shape_key: str) -> Optional[str]:
        """Returns the canonical answer for a shape_key, or None."""
        answer = self._store.get(shape_key)
        if answer:
            self._hit_count[shape_key] = self._hit_count.get(shape_key, 0) + 1
            logger.info(f"canonical_hit: key={shape_key} hits={self._hit_count[shape_key]}")
        return answer

    def store(self, shape_key: str, answer: str, overwrite: bool = False):
        """Stores a canonical answer. Overwrites only if explicitly requested."""
        if shape_key in self._store and not overwrite:
            logger.debug(f"canonical_exists: key={shape_key} (skipping)")
            return
        self._store[shape_key] = answer
        self._hit_count[shape_key] = 0
        logger.info(f"canonical_stored: key={shape_key}")

    def stats(self) -> Dict[str, Any]:
        total_hits = sum(self._hit_count.values())
        return {
            "total_concepts": len(self._store),
            "total_hits": total_hits,
            "top_concepts": sorted(self._hit_count.items(), key=lambda x: -x[1])[:10],
        }

    def size(self) -> int:
        return len(self._store)


global_canonical_store = CanonicalStore()
