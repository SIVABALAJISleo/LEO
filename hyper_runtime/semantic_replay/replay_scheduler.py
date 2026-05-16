import logging
import time
from typing import Dict, Any

logger = logging.getLogger("HyperCore.SemanticScheduler")

class SemanticSimilarityScheduler:
    """
    Orchestrates the HyperCore Semantic Replay Pipeline.
    Manages embedding generation, exact fingerprint checks, LSH/ANN vector caching,
    confidence scoring, exact verification fallback, and backend routing.
    """
    def __init__(self, cache, embedding_engine, compute_backend, verification_threshold=0.95):
        self.cache = cache
        self.embedding_engine = embedding_engine
        self.compute_backend = compute_backend
        self.verification_threshold = verification_threshold # Scores between cache.threshold and this get verified

    def route_query(self, query: str) -> Dict[str, Any]:
        t_start = time.perf_counter()

        # 1. Generate O(1) Fingerprint
        fingerprint = self.embedding_engine.get_fingerprint(query)

        # 2. Generate Dense Semantic Vector
        query_emb = self.embedding_engine.encode(query)

        # 3. Cache Search (Exact -> LSH -> ANN)
        response, confidence, match_type, search_latency = self.cache.search(query, fingerprint, query_emb)

        if response:
            # Check if confidence is borderline, requiring Exact Verification Fallback
            if match_type != "exact_fingerprint" and confidence < self.verification_threshold:
                logger.info(f"Borderline Replay Match (score={confidence:.3f} < {self.verification_threshold}). Triggering Exact Verification Fallback.")
                # Verify by running compute backend and comparing / ensuring correctness
                # In a real system, verification might be a lighter LLM or exact solver. Here we invoke backend.
                t_verif_start = time.perf_counter()
                verified_response = self.compute_backend.generate(query)
                verif_latency = time.perf_counter() - t_verif_start

                # Update cache with verified response
                self.cache.add(query, fingerprint, query_emb, verified_response, lineage={"query": query, "verified": True})
                
                total_latency = time.perf_counter() - t_start
                return {
                    "response": verified_response,
                    "source": "exact_verification_fallback",
                    "confidence": 1.0,
                    "match_type": match_type,
                    "search_latency_sec": search_latency,
                    "verif_latency_sec": verif_latency,
                    "total_latency_sec": total_latency,
                    "replayed": False
                }

            # High confidence Replay Hit
            logger.info(f"Semantic Replay Hit ({match_type}, score={confidence:.3f}). Bypassing compute backend.")
            total_latency = time.perf_counter() - t_start
            return {
                "response": response,
                "source": "semantic_replay",
                "confidence": confidence,
                "match_type": match_type,
                "search_latency_sec": search_latency,
                "total_latency_sec": total_latency,
                "replayed": True
            }

        # 4. Replay Miss -> Route to Compute Backend
        logger.info("Semantic Replay Miss. Routing query to primary Compute Backend.")
        t_comp_start = time.perf_counter()
        response = self.compute_backend.generate(query)
        comp_latency = time.perf_counter() - t_comp_start

        # Populate cache for future queries
        self.cache.add(query, fingerprint, query_emb, response, lineage={"query": query})

        total_latency = time.perf_counter() - t_start
        return {
            "response": response,
            "source": "compute_backend",
            "confidence": 1.0,
            "match_type": "none",
            "search_latency_sec": search_latency,
            "compute_latency_sec": comp_latency,
            "total_latency_sec": total_latency,
            "replayed": False
        }
