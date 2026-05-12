import logging

class SemanticSimilarityScheduler:
    def __init__(self, cache, embedding_model, compute_backend):
        self.cache = cache
        self.embedding_model = embedding_model
        self.compute_backend = compute_backend
        self.logger = logging.getLogger("SemanticScheduler")
        
    def route_query(self, query):
        # 1. Encode query
        query_emb = self.embedding_model.encode(query)
        
        # 2. Check semantic cache
        cached_response, score = self.cache.search(query_emb)
        if cached_response:
            self.logger.info(f"Replay Hit (score={score:.3f}). Skipped compute.")
            return {"response": cached_response, "source": "replay", "confidence": score}
            
        # 3. Fallback to compute
        self.logger.info("Replay Miss. Routing to Compute Backend.")
        response = self.compute_backend.generate(query)
        
        # 4. Update cache
        self.cache.add(query_emb, response, lineage_data={"query": query})
        
        return {"response": response, "source": "compute", "confidence": 1.0}
