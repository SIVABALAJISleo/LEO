import json
import logging
import sys
import os

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hyper_runtime.retrieval.rag_retrieval_system import RAGMemoryIndex

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')

KNOWLEDGE_CORPUS = [
    {
        "text": """
        HyperCore Runtime is a CPU-first AI orchestration system designed to minimize GPU dependence.
        It uses semantic replay, retrieval-first execution, and novelty-proportional compute.
        The system routes repeated or semantically similar queries directly from cache,
        avoiding expensive model inference entirely when confidence is above threshold.
        """,
        "metadata": {"source": "hypercore_docs", "topic": "overview"}
    },
    {
        "text": """
        The Mamba State Space Model (SSM) architecture provides linear-time sequence processing,
        replacing the quadratic attention mechanism used in traditional Transformers.
        Mamba uses selective scan kernels and recurrent state reuse to maintain long-context
        comprehension with significantly reduced memory and compute costs.
        """,
        "metadata": {"source": "mamba_paper", "topic": "mamba_ssm"}
    },
    {
        "text": """
        BitNet implements ternary weight quantization using values in {-1, 0, +1},
        replacing standard floating-point multiply-accumulate operations with integer addition.
        With INT8 activations and AVX2/AVX-512 SIMD vectorization, BitNet achieves
        near-floating-point accuracy at a fraction of the arithmetic cost on CPUs.
        """,
        "metadata": {"source": "bitnet_paper", "topic": "bitnet_quantization"}
    },
    {
        "text": """
        DiLoCo (Distributed Local SGD with Communication) is an asynchronous training algorithm
        that allows distributed nodes to train locally for many steps before synchronizing gradients.
        This minimizes communication bandwidth and allows GPU-irrelevant commodity CPU clusters
        to cooperate on training without high-speed interconnects.
        """,
        "metadata": {"source": "diloco_paper", "topic": "distributed_training"}
    },
    {
        "text": """
        FAISS (Facebook AI Similarity Search) provides efficient exact and approximate
        nearest neighbor search at scale. The IndexFlatIP index uses inner-product (cosine similarity
        when normalized), while IndexLSH provides ultra-fast Locality-Sensitive Hashing
        for sub-millisecond approximate filtering before exact verification.
        """,
        "metadata": {"source": "faiss_docs", "topic": "vector_search"}
    },
    {
        "text": """
        BM25 (Okapi Best Match 25) is a probabilistic sparse retrieval algorithm.
        It scores documents by term frequency (TF), inverse document frequency (IDF),
        and document length normalization with parameters k1=1.5 and b=0.75.
        Hybrid retrieval combines BM25 with dense vector search via reciprocal rank fusion.
        """,
        "metadata": {"source": "ir_textbook", "topic": "bm25_retrieval"}
    },
]

def run_benchmark():
    print("=" * 70)
    print("  HYPERCORE RUNTIME — MODULE 2: RETRIEVAL-FIRST INTELLIGENCE LAYER")
    print("=" * 70)

    index = RAGMemoryIndex(
        embedding_dim=384,
        chunk_size=80,
        chunk_overlap=20,
        hybrid_alpha=0.7,
        top_k=3,
        index_dir=".hyper_cache/rag_bench",
        db_path=".hyper_cache/rag_bench/doc_store.db",
        force_fallback_encoder=True  # Use TF-IDF+SVD for speed in benchmark
    )

    print("\n[1/3] Ingesting Knowledge Corpus...")
    for entry in KNOWLEDGE_CORPUS:
        result = index.add_document(entry["text"], metadata=entry["metadata"])
        print(f"  Doc ingested: {result['chunks_added']} chunks added, {result['chunks_skipped']} dedup-skipped.")

    # Test semantic deduplication - add the same doc again
    print("\n[2/3] Testing Semantic Deduplication (re-ingesting same corpus)...")
    for entry in KNOWLEDGE_CORPUS:
        result = index.add_document(entry["text"], metadata=entry["metadata"])
        print(f"  Re-ingest: {result['chunks_added']} added (should be 0), {result['chunks_skipped']} skipped.")

    print("\n[3/3] Running Retrieval Queries...")
    queries = [
        "How does HyperCore avoid GPU computation?",
        "What is Mamba and how does it replace attention?",
        "Explain BitNet ternary quantization and SIMD",
        "How does distributed training work without high-speed interconnects?",
        "What is the difference between BM25 and FAISS vector search?",
        "What is quantum entanglement?",  # Out-of-domain query
    ]

    for query in queries:
        print(f"\n  Query: '{query}'")
        context = index.assemble_context(query, max_tokens=150, top_k=3)
        chunks = index.retrieve(query, top_k=2)
        if chunks:
            for i, chunk in enumerate(chunks):
                print(f"    [{i+1}] Hybrid={chunk['scores']['hybrid']:.4f} | "
                      f"Vector={chunk['scores']['vector']:.4f} | "
                      f"BM25={chunk['scores']['bm25']:.4f}")
                print(f"        Source: {chunk['metadata'].get('topic', 'unknown')}")
                print(f"        Content: {chunk['content'][:100]}...")
        else:
            print("    No relevant chunks found (out-of-domain query).")

    print("\n" + "=" * 70)
    print("  MODULE 2 TELEMETRY")
    print("=" * 70)
    print(json.dumps(index.get_metrics(), indent=2))

    # Save index for future reuse
    index.save()
    print("\nFAISS index saved to disk.")

if __name__ == "__main__":
    run_benchmark()
