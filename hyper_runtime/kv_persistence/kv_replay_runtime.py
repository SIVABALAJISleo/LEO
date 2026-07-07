import time
import numpy as np
from .kv_store import PersistentKVCache
from .kv_compression import quantize_kv

class KVReplayRuntime:
    def __init__(self):
        self.kv_store = PersistentKVCache()
        
    def process_prompt(self, session_id, tokens):
        start = time.time()
        keys, values, cached_tokens = self.kv_store.load_kv(session_id)
        
        prefix_match_len = 0
        if cached_tokens is not None:
            # Find longest matching prefix
            for i in range(min(len(tokens), len(cached_tokens))):
                if tokens[i] == cached_tokens[i]:
                    prefix_match_len += 1
                else:
                    break
                    
        if prefix_match_len > 0:
            print(f"KV Cache Hit: Recovered {prefix_match_len} tokens for session {session_id}")
            # In a real llama.cpp binding, we would inject the KVs here
            latency = time.time() - start
            return prefix_match_len, latency
            
        print(f"KV Cache Miss for session {session_id}")
        
        # Simulate compute
        time.sleep(0.1 * len(tokens)) 
        
        # Simulate saving KV
        mock_k = np.random.randn(len(tokens), 32, 128).astype(np.float32)
        mock_v = np.random.randn(len(tokens), 32, 128).astype(np.float32)
        
        # Compress before saving
        q_k, min_k, scale_k = quantize_kv(mock_k)
        
        self.kv_store.save_kv(session_id, mock_k, mock_v, tokens)
        
        latency = time.time() - start
        return 0, latency
