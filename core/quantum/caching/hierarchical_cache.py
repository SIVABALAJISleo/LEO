"""
Hierarchical Caching System for LEO
Implements exact match, semantic, and KV cache optimization
"""
import torch
import numpy as np
import hashlib
import time
import json
import faiss
from typing import Dict, Any, Optional, Tuple, List
from collections import OrderedDict, defaultdict

# Attempt to load Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from core.quantum.caching.kv_cache_optimizer import KVCacheOptimizer
from core.quantum.caching.predictive_prefetcher import PredictivePrefetcher


class HierarchicalCache:
    """
    Multi-level caching system:
    L1: Exact match cache (in-memory, <1ms)
    L2: Semantic cache (vector similarity, ~20ms)
    L3: KV cache compression (for multi-turn)
    L4: Predictive prefetch (anticipated queries)
    """
    def __init__(self, config: Optional[Dict] = None):
        self.config = self._default_config()
        if config:
            self.config.update(config)
        
        # L1: Exact match cache
        self.exact_cache = OrderedDict()
        self.exact_cache_size = 0
        
        # L2: Semantic cache
        self.semantic_cache = faiss.IndexFlatIP(384)  # MiniLM embedding size
        self.semantic_queries = []
        self.semantic_responses = []
        
        # L3: KV cache (for conversation context)
        self.kv_cache = {}
        self.kv_optimizer = KVCacheOptimizer()
        
        # L4: Predictive prefetch
        self.prefetcher = PredictivePrefetcher()
        self.prefetch_queue = []
        self.query_patterns = defaultdict(list)
        
        # Statistics
        self.stats = {
            'exact_hits': 0,
            'semantic_hits': 0,
            'kv_cache_hits': 0,
            'prefetch_hits': 0,
            'total_queries': 0,
            'cache_misses': 0,
            'avg_latency': 0.0
        }
        
        # Redis client (fallback if redis not available/offline)
        self.redis_client = None
        if REDIS_AVAILABLE and self.config['redis_enabled']:
            try:
                self.redis_client = redis.Redis(
                    host=self.config['redis_host'],
                    port=self.config['redis_port'],
                    db=0,
                    decode_responses=True,
                    socket_connect_timeout=1
                )
                self.redis_client.ping()
            except Exception:
                self.redis_client = None
        
    def _default_config(self) -> Dict:
        return {
            'exact_cache_size': 1000,  # 1000 queries
            'semantic_cache_size': 5000,  # 5000 queries
            'kv_cache_size': 100,  # 100 conversations
            'similarity_threshold': 0.85,
            'prefetch_enabled': True,
            'redis_enabled': True,
            'redis_host': 'localhost',
            'redis_port': 6379
        }
    
    def get(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        embedding: Optional[np.ndarray] = None
    ) -> Tuple[Optional[str], float, str]:
        """
        Get response from cache hierarchy
        
        Returns:
            response: Cached response or None
            latency: Retrieval latency in ms
            cache_level: Which cache level was hit
        """
        start_time = time.time()
        self.stats['total_queries'] += 1
        
        # L1: Check exact match cache
        response = self._get_from_exact_cache(query)
        if response is not None:
            latency = (time.time() - start_time) * 1000
            self.stats['exact_hits'] += 1
            self._update_stats(latency)
            return response, latency, 'L1_exact'
        
        # L2: Check semantic cache
        if embedding is not None:
            response = self._get_from_semantic_cache(embedding)
            if response is not None:
                latency = (time.time() - start_time) * 1000
                self.stats['semantic_hits'] += 1
                self._update_stats(latency)
                return response, latency, 'L2_semantic'
        
        # L3: Check KV cache for conversation
        if conversation_id:
            response = self._get_from_kv_cache(conversation_id, query)
            if response is not None:
                latency = (time.time() - start_time) * 1000
                self.stats['kv_cache_hits'] += 1
                self._update_stats(latency)
                return response, latency, 'L3_kv'
        
        # L4: Check prefetch queue
        response = self._get_from_prefetch(query)
        if response is not None:
            latency = (time.time() - start_time) * 1000
            self.stats['prefetch_hits'] += 1
            self._update_stats(latency)
            return response, latency, 'L4_prefetch'
        
        # Cache miss
        latency = (time.time() - start_time) * 1000
        self.stats['cache_misses'] += 1
        self._update_stats(latency)
        
        # Add to prefetch patterns
        if self.config['prefetch_enabled']:
            self._update_prefetch_patterns(query)
        
        return None, latency, 'miss'
    
    def _get_from_exact_cache(self, query: str) -> Optional[str]:
        """Get from exact match cache"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        
        # Check Redis if available
        if self.redis_client:
            try:
                response = self.redis_client.get(f"exact:{query_hash}")
                if response:
                    return json.loads(response)
            except Exception:
                pass
        
        # Check local cache
        if query_hash in self.exact_cache:
            # Move to end (LRU)
            self.exact_cache.move_to_end(query_hash)
            return self.exact_cache[query_hash]
        
        return None
    
    def _get_from_semantic_cache(self, embedding: np.ndarray) -> Optional[str]:
        """Get from semantic cache using vector similarity"""
        if len(self.semantic_queries) == 0:
            return None
        
        # Search in FAISS index
        embedding = embedding.reshape(1, -1).astype(np.float32)
        # Normalize for cosine similarity
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        distances, indices = self.semantic_cache.search(embedding, 1)
        
        if len(indices) > 0 and indices[0][0] >= 0:
            similarity = distances[0][0]
            if similarity >= self.config['similarity_threshold']:
                return self.semantic_responses[indices[0][0]]
        
        return None

    def _get_from_kv_cache(self, conversation_id: str, query: str) -> Optional[str]:
        """Get from conversation-specific KV cache"""
        if conversation_id in self.kv_cache:
            conv = self.kv_cache[conversation_id]
            if query in conv:
                return conv[query]
        return None

    def _get_from_prefetch(self, query: str) -> Optional[str]:
        """Get from predictive prefetch list"""
        # Prefetch hits return the pre-calculated responses
        for q, resp in self.prefetch_queue:
            if q == query:
                return resp
        return None

    def _update_prefetch_patterns(self, query: str):
        """Analyze query transitions for prefetching"""
        self.prefetcher.record_query(query)
        
    def _update_stats(self, latency: float):
        """Update metrics average latency"""
        n = self.stats['total_queries']
        self.stats['avg_latency'] = (self.stats['avg_latency'] * (n - 1) + latency) / n

    def put(
        self,
        query: str,
        response: str,
        embedding: Optional[np.ndarray] = None,
        conversation_id: Optional[str] = None
    ):
        """Store response in all relevant cache levels"""
        # L1: Store in exact cache
        self._put_in_exact_cache(query, response)
        
        # L2: Store in semantic cache
        if embedding is not None:
            self._put_in_semantic_cache(query, response, embedding)
        
        # L3: Store in KV cache
        if conversation_id:
            self._put_in_kv_cache(conversation_id, query, response)
            
    def _put_in_exact_cache(self, query: str, response: str):
        """Store in exact match cache"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        
        # Store in Redis if enabled
        if self.redis_client:
            try:
                self.redis_client.setex(
                    f"exact:{query_hash}",
                    3600,  # 1 hour TTL
                    json.dumps(response)
                )
            except Exception:
                pass
        
        # Store in local cache
        self.exact_cache[query_hash] = response
        
        # Evict if size exceeded
        while len(self.exact_cache) > self.config['exact_cache_size']:
            self.exact_cache.popitem(last=False)
            
    def _put_in_semantic_cache(self, query: str, response: str, embedding: np.ndarray):
        """Store in semantic FAISS index"""
        embedding = embedding.reshape(1, -1).astype(np.float32)
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        self.semantic_cache.add(embedding)
        self.semantic_queries.append(query)
        self.semantic_responses.append(response)

    def _put_in_kv_cache(self, conversation_id: str, query: str, response: str):
        """Store in conversation-specific L3 KV cache"""
        if conversation_id not in self.kv_cache:
            self.kv_cache[conversation_id] = {}
        self.kv_cache[conversation_id][query] = response
        
        # Evict LRU conversation if budget exceeded
        if len(self.kv_cache) > self.config['kv_cache_size']:
            first_id = next(iter(self.kv_cache))
            del self.kv_cache[first_id]
