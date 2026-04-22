import json
import os
import re
import numpy as np

"""
CONTEXTUAL SIMHASH ROUTING (V1)
Transforms: [Query + Prior Context] -> Deterministic CDN Path
"""

class ContextualSimHashRouter:
    def __init__(self, cdn_dir="./cdn_simhash"):
        self.cdn_dir = cdn_dir
        self.noise = {"the", "a", "an", "is", "are", "do", "how", "what", "of", "in", "on", "for", "check", "i"}
        
        # Simulated Context Lattice (128-bit context state)
        self.context_state = 0x0

    def set_context(self, context_str):
        """Sets the current operational context (e.g., 'primary_node', 'maintenance_mode')"""
        if not context_str:
            self.context_state = 0x0
            return
            
        # Deterministic context bit-bias
        h = hashlib.sha256(context_str.encode()).digest()
        self.context_state = int.from_bytes(h[:8], 'big') # 64-bit context bias

    def _get_input_tokens(self, text):
        return set(re.findall(r'\w+', text.lower())) - self.noise

    def _fnv1a(self, s):
        h = 0xcbf29ce484222325
        for char in s:
            h ^= ord(char)
            h = (h * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
        return h

    def compute_contextual_hash(self, text):
        # 1. Base SimHash
        tokens = re.findall(r'\w+', text.lower())
        v = [0] * 64
        for t in tokens:
            if t in self.noise: continue
            h = self._fnv1a(t)
            weight = 2 if len(t) > 5 else 1
            for i in range(64):
                if (h >> i) & 1: v[i] += weight
                else: v[i] -= weight
        
        base_sh = 0
        for i in range(64):
            if v[i] > 0: base_sh |= (1 << i)
            
        # 2. CONTEXT SHIFT (XOR with current context state)
        # This shifts the query into a different geometric quadrant without compute
        contextual_sh = base_sh ^ self.context_state
        return contextual_sh

    def route(self, query_text):
        sh = self.compute_contextual_hash(query_text)
        prefix = (sh >> 60) & 0xF
        print(f"[QUERY] '{query_text}' | Context: {hex(self.context_state)} | Hash: 0x{sh:016x}")
        
        # CDN Logic ... (Simplified for demo)
        return sh

if __name__ == "__main__":
    import hashlib
    router = ContextualSimHashRouter()
    
    query = "reboot it"
    
    # Scenario A: No Context
    print("--- Scenario A: No Context ---")
    router.set_context(None)
    h1 = router.route(query)
    
    # Scenario B: Context is 'alpha_node'
    print("\n--- Scenario B: Context is ALPHA ---")
    router.set_context("alpha_node")
    h2 = router.route(query)
    
    # Scenario C: Context is 'primary_system'
    print("\n--- Scenario C: Context is PRIMARY ---")
    router.set_context("primary_system")
    h3 = router.route(query)
    
    print(f"\nResult: Query '{query}' generated {len(set([h1,h2,h3]))} different hashes based on context.")
