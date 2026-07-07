import json
import os

"""
HYBRID ORCHESTRATOR - BRIDGE TO EDGE SYSTEM
"""

class HybridOrchestrator:
    def __init__(self, cdn_root="./cdn_mock"):
        self.cdn_root = cdn_root
        self.vocab = {}
        self.weights = {}
        self.load_config()

    def load_config(self):
        vocab_path = os.path.join(self.cdn_root, "vocab.json")
        if os.path.exists(vocab_path):
            with open(vocab_path, "r") as f:
                data = json.load(f)
                self.vocab = data["vocab"]
                self.weights = data["weights"]

    def _client_simulate(self, text):
        import re
        # Strip punctuation and tokenize
        tokens = re.findall(r'\w+', text.lower())
        
        # Map to IDs with synonym collapse
        ids = []
        seen = set()
        for t in tokens:
            cid = self.vocab.get(t, 0)
            if cid > 0 and cid not in seen:
                ids.append(cid)
                seen.add(cid)
        
        if not ids:
            return None, 0
        
        drops = 0
        while ids:
            # Hash
            h = self._compute_stable_hash(ids)
            path = os.path.join(self.cdn_root, f"0x{h:016x}")
            
            if os.path.exists(path):
                return f"0x{h:016x}", drops
            
            # Drop lowest weight
            min_w = 999
            min_id_idx = -1
            for i, cid in enumerate(ids):
                w = self.weights.get(str(cid), 10)
                if w < min_w:
                    min_w = w
                    min_id_idx = i
            
            ids.pop(min_id_idx)
            drops += 1
            
        return None, drops

    def _compute_stable_hash(self, ids):
        ids = sorted(ids)
        h = 0xcbf29ce484222325
        for cid in ids:
            h ^= cid
            h = (h * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
        return h

    def query(self, text):
        print(f"\n[QUERY] '{text}'")
        
        # 1. Edge-side resolution
        endpoint, drops = self._client_simulate(text)
        
        if endpoint:
            print(f"[EDGE] Resolved to {endpoint} (Dropped {drops} tokens)")
            # 2. CDN Fetch (Static Only)
            data_path = os.path.join(self.cdn_root, endpoint, "data.json")
            with open(data_path, "r") as f:
                result = json.load(f)
            
            # 3. Deterministic Reasoning (Micro-WASM)
            wasm_path = os.path.join(self.cdn_root, endpoint, "logic.wasm")
            if os.path.exists(wasm_path):
                print(f"[EDGE] Executing reasoning logic: {endpoint}/logic.wasm")
                # Simulated WASM execution
                result["_meta"] = "verified_via_wasm"

            return result
        else:
            # 4. Fallback (Controlled)
            print("[FALLBACK] Unknown intent. Routing to Secondary Reasoning System...")
            return {
                "status": "UNKNOWN",
                "action": "DELEGATE_TO_LLM"
            }

if __name__ == "__main__":
    # Ensure compiler has run first
    # os.system("python orchestration/semantic_compiler.py")
    
    orch = HybridOrchestrator()
    
    # Test Cases
    print(orch.query("How is the health of the system?"))    # Should drop 'how', 'is', 'the', 'of', 'the' then match 'health system'
    print(orch.query("Status report for alpha core"))        # Should match 'status primary system'
    print(orch.query("Is the engine okay?"))                 # Might match 'engine' -> drop -> 'unknown'
    print(orch.query("Tell me a joke"))                      # Unknown
