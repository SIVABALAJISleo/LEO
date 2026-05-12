import time
from .replay_cache import SemanticReplayCache
from .replay_scheduler import SemanticSimilarityScheduler

class MockEmbeddingModel:
    def encode(self, text):
        import numpy as np
        np.random.seed(hash(text) % (2**32))
        return np.random.randn(384).astype(np.float32)

class MockComputeBackend:
    def generate(self, text):
        time.sleep(0.5) # Simulate compute latency
        return f"Generated response for: {text}"

class SemanticReplayRuntime:
    def __init__(self, threshold=0.90):
        self.cache = SemanticReplayCache(threshold=threshold)
        self.embedder = MockEmbeddingModel()
        self.backend = MockComputeBackend()
        self.scheduler = SemanticSimilarityScheduler(self.cache, self.embedder, self.backend)
        
    def execute(self, query):
        start = time.time()
        result = self.scheduler.route_query(query)
        latency = time.time() - start
        result["latency_sec"] = latency
        return result
