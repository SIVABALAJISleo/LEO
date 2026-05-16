import numpy as np
import logging
import time
import uuid
from typing import List, Dict, Any, Optional

from .document_chunker import SemanticChunker
from .bm25_retriever import BM25Retriever
from .vector_store import FaissVectorStore, SQLiteDocumentStore

logger = logging.getLogger("HyperCore.RAGMemoryIndex")

class RAGMemoryIndex:
    """
    HyperCore MODULE 2 — Retrieval-First Intelligence Layer.

    Externalizes knowledge from dense model weights into a hybrid retrieval system:
    - FAISS vector store for semantic (dense) retrieval
    - BM25 for keyword (sparse) retrieval
    - SQLite for persistent chunk storage
    - Semantic deduplication via SHA-256 fingerprinting
    - Adaptive context assembly with compressed / ranked output
    - Hierarchical scoring: alpha * vector_score + (1-alpha) * bm25_score
    """
    def __init__(
        self,
        embedding_dim: int = 384,
        chunk_size: int = 256,
        chunk_overlap: int = 32,
        hybrid_alpha: float = 0.7,        # Weight for vector vs BM25 (0=pure BM25, 1=pure vector)
        top_k: int = 5,
        index_dir: str = ".hyper_cache/rag",
        db_path: str = ".hyper_cache/rag/doc_store.db",
        force_fallback_encoder: bool = False
    ):
        self.embedding_dim = embedding_dim
        self.hybrid_alpha = hybrid_alpha
        self.top_k = top_k

        # Embedding engine (reuse Module 1's encoder)
        try:
            from hyper_runtime.semantic_replay.replay_encoder import SemanticEmbeddingEngine
            self.encoder = SemanticEmbeddingEngine(
                embedding_dim=embedding_dim,
                force_fallback=force_fallback_encoder
            )
        except ImportError:
            from ..semantic_replay.replay_encoder import SemanticEmbeddingEngine
            self.encoder = SemanticEmbeddingEngine(
                embedding_dim=embedding_dim,
                force_fallback=force_fallback_encoder
            )

        # Storage backends
        self.chunker = SemanticChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.vector_store = FaissVectorStore(embedding_dim=embedding_dim, index_dir=index_dir)
        self.doc_store = SQLiteDocumentStore(db_path=db_path)
        self.bm25 = BM25Retriever()

        # In-memory chunk registry for BM25 (BM25 is stateful, no persistence yet)
        self._bm25_corpus: List[str] = []
        self._bm25_chunk_ids: List[str] = []

        # Telemetry
        self.total_docs_indexed = 0
        self.total_chunks_indexed = 0
        self.total_retrievals = 0
        self.total_dedup_skips = 0
        self.total_retrieval_latency = 0.0

        # Attempt to load persisted FAISS index
        self.vector_store.load()
        logger.info(
            f"RAGMemoryIndex initialized. "
            f"Vector store: {self.vector_store.ntotal} vectors. "
            f"SQLite chunks: {self.doc_store.count()}."
        )

    def add_document(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Ingests a document: chunks it, embeds each chunk, deduplicates,
        stores in SQLite and FAISS, and updates BM25 corpus.
        """
        doc_id = str(uuid.uuid4())
        metadata = metadata or {}
        metadata["doc_id"] = doc_id
        metadata["ingested_at"] = time.time()

        chunks = self.chunker.chunk(text, doc_id, metadata)
        added_count = 0
        skipped_count = 0

        for chunk in chunks:
            # Semantic deduplication via fingerprint
            if self.doc_store.fingerprint_exists(chunk["fingerprint"]):
                skipped_count += 1
                self.total_dedup_skips += 1
                continue

            # Embed chunk
            emb = self.encoder.encode(chunk["content"])
            emb_vec = emb[0]  # [D]

            # Add to stores
            self.doc_store.add_chunk(chunk)
            self.vector_store.add(chunk["chunk_id"], emb_vec)

            # Update BM25 in-memory corpus
            self._bm25_corpus.append(chunk["content"])
            self._bm25_chunk_ids.append(chunk["chunk_id"])

            added_count += 1

        # Rebuild BM25 index after ingestion
        if self._bm25_corpus:
            self.bm25.add_documents(self._bm25_corpus, self._bm25_chunk_ids)

        self.total_docs_indexed += 1
        self.total_chunks_indexed += added_count

        logger.info(
            f"Indexed doc {doc_id[:8]}...: "
            f"{added_count} chunks added, {skipped_count} dedup-skipped."
        )
        return {"doc_id": doc_id, "chunks_added": added_count, "chunks_skipped": skipped_count}

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Hybrid BM25 + Vector retrieval with reciprocal rank fusion.
        Returns ranked list of chunk dicts with combined hybrid scores.
        """
        t0 = time.perf_counter()
        top_k = top_k or self.top_k
        self.total_retrievals += 1

        if self.vector_store.ntotal == 0:
            logger.info("RAG index is empty. No retrieval results.")
            return []

        query_emb = self.encoder.encode(query)[0]

        # --- Dense vector retrieval ---
        vector_results = self.vector_store.search(query_emb, top_k=top_k * 2)
        vector_scores: Dict[str, float] = {cid: score for cid, score in vector_results}

        # --- Sparse BM25 retrieval ---
        bm25_raw = self.bm25.score(query, top_k=top_k * 2)
        # Normalize BM25 scores to [0,1]
        max_bm25 = max((s for _, s in bm25_raw), default=1.0)
        bm25_scores: Dict[str, float] = {}
        for idx, score in bm25_raw:
            if idx < len(self._bm25_chunk_ids):
                cid = self._bm25_chunk_ids[idx]
                bm25_scores[cid] = score / max(1e-9, max_bm25)

        # --- Hybrid Score Fusion ---
        all_chunk_ids = set(vector_scores.keys()) | set(bm25_scores.keys())
        fused: List[tuple] = []
        for cid in all_chunk_ids:
            vs = vector_scores.get(cid, 0.0)
            bs = bm25_scores.get(cid, 0.0)
            hybrid = self.hybrid_alpha * vs + (1.0 - self.hybrid_alpha) * bs
            fused.append((cid, hybrid, vs, bs))

        fused.sort(key=lambda x: x[1], reverse=True)

        # --- Adaptive Context Assembly ---
        results = []
        for cid, hybrid_score, vec_score, bm25_score in fused[:top_k]:
            chunk = self.doc_store.get_chunk(cid)
            if chunk:
                results.append({
                    "chunk_id": cid,
                    "content": chunk["content"],
                    "doc_id": chunk["doc_id"],
                    "metadata": chunk["metadata"],
                    "scores": {
                        "hybrid": round(hybrid_score, 4),
                        "vector": round(vec_score, 4),
                        "bm25": round(bm25_score, 4)
                    }
                })

        latency = time.perf_counter() - t0
        self.total_retrieval_latency += latency
        logger.info(
            f"Retrieval completed: {len(results)} chunks in {latency*1000:.2f}ms "
            f"(alpha={self.hybrid_alpha}, vector_store={self.vector_store.ntotal})"
        )
        return results

    def assemble_context(self, query: str, max_tokens: int = 1024, top_k: Optional[int] = None) -> str:
        """
        Hierarchical context assembly: retrieves top-k chunks and
        trims context to max_tokens budget (approximate, word-based).
        Returns a single concatenated context string.
        """
        chunks = self.retrieve(query, top_k=top_k)
        if not chunks:
            return ""

        context_parts = []
        word_budget = max_tokens
        for chunk in chunks:
            words = chunk["content"].split()
            if word_budget <= 0:
                break
            if len(words) > word_budget:
                words = words[:word_budget]
            context_parts.append(" ".join(words))
            word_budget -= len(words)

        return "\n\n".join(context_parts)

    def save(self):
        """Persist FAISS index to disk."""
        self.vector_store.save()
        logger.info("RAGMemoryIndex saved.")

    def get_metrics(self) -> Dict[str, Any]:
        avg_lat = (self.total_retrieval_latency / max(1, self.total_retrievals))
        return {
            "total_docs_indexed": self.total_docs_indexed,
            "total_chunks_indexed": self.total_chunks_indexed,
            "total_dedup_skips": self.total_dedup_skips,
            "total_retrievals": self.total_retrievals,
            "vector_store_size": self.vector_store.ntotal,
            "sqlite_chunks": self.doc_store.count(),
            "avg_retrieval_latency_ms": round(avg_lat * 1000, 3),
            "hybrid_alpha": self.hybrid_alpha,
            "use_faiss": self.vector_store.use_faiss
        }
