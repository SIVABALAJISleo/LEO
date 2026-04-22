import hashlib
import json
import os
import struct

"""
OFFLINE SEMANTIC COMPILER (REAL INTELLIGENCE)
Builds the static CDN structure and edge-side configuration blobs.
"""

class SemanticCompiler:
    def __init__(self):
        self.vocab = {}
        self.weights = {}
        self.anchors = {}
        self.next_id = 100
        self.bloom_size = 16384 # 16kb
        self.hash_count = 3

    def add_concept(self, canonical_name, synonyms, weight=10):
        # Generate stable ID for concept
        cid = self.next_id
        self.next_id += 1
        
        for s in synonyms + [canonical_name]:
            self.vocab[s] = cid
        
        self.weights[cid] = weight
        return cid

    def _compute_stable_hash(self, ids):
        # Sort for stability
        ids = sorted([i for i in ids if i > 0])
        h = 0xcbf29ce484222325
        for cid in ids:
            h ^= cid
            h = (h * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
        return h

    def add_anchor(self, tokens, response_json, wasm_module=None):
        ids = [self.vocab.get(t, 0) for t in tokens]
        if 0 in ids:
            missing = [tokens[i] for i, v in enumerate(ids) if v == 0]
            print(f"Warning: Unknown tokens in anchor {tokens}: {missing}")
        
        h = self._compute_stable_hash(ids)
        self.anchors[h] = {
            "tokens": tokens,
            "ids": ids,
            "response": response_json,
            "wasm": wasm_module
        }
        return h

    def compute_simhash(self, text, context_str=None):
        tokens = re.findall(r'\w+', text.lower())
        v = [0] * 64
        for t in tokens:
            if t in self.noise: continue
            h = self._fnv1a(t)
            weight = 2 if len(t) > 5 else 1
            for i in range(64):
                if (h >> i) & 1: v[i] += weight
                else: v[i] -= weight
        
        sh = 0
        for i in range(64):
            if v[i] > 0: sh |= (1 << i)
            
        # Context Shift
        if context_str:
            h_ctx = hashlib.sha256(context_str.encode()).digest()
            ctx_bias = int.from_bytes(h_ctx[:8], 'big')
            sh ^= ctx_bias
            
        return sh

    def build_cdn(self, dataset):
        """
        Dataset: List of { "id": str, "query": str, "context": str (optional), "response": str }
        """
        os.makedirs(self.bucket_dir, exist_ok=True)
        
        for item in dataset:
            query = item["query"]
            context = item.get("context")
            sh = self.compute_simhash(query, context)
            
            # Bucketing strategy: first 4 bits for folder (0-f)
            prefix = (sh >> 60) & 0xF 
            folder = os.path.join(self.bucket_dir, f"{prefix:x}")
            os.makedirs(folder, exist_ok=True)
            
            # Static Data Blob
            filename = f"0x{sh:016x}.json"
            path = os.path.join(folder, filename)
            
            tokens = set(re.findall(r'\w+', query.lower())) - self.noise
            
            blob = {
                "id": item["id"],
                "signature": sorted(list(tokens)),
                "context": context,
                "response": item["response"],
                "tags": item.get("tags", []),
                "sh": f"0x{sh:016x}"
            }
            
            with open(path, "w") as f:
                json.dump(blob, f, indent=2)
            
            ctx_label = f"Ctx: {context}" if context else "Ctx: NONE"
            print(f"Compiled: {query} ({ctx_label}) -> {path}")

    def generate_bloom_blob(self):
        blob = bytearray(self.bloom_size // 8)
        for h in self.anchors.keys():
            for i in range(self.hash_count):
                pos = (h + i * 0x9e3779b9) % self.bloom_size
                blob[pos // 8] |= (1 << (pos % 8))
        return blob

    def compile_cdn(self, root_path):
        os.makedirs(root_path, exist_ok=True)
        
        # 1. Write the Bloom Filter blob for the Client to download
        with open(os.path.join(root_path, "router.bin"), "wb") as f:
            f.write(self.generate_bloom_blob())
        
        # 2. Write the Vocabulary Map for the Client
        with open(os.path.join(root_path, "vocab.json"), "w") as f:
            json.dump({"vocab": self.vocab, "weights": self.weights}, f, indent=2)

        # 3. Write each Anchor endpoint (The CDN data)
        for h, data in self.anchors.items():
            anchor_dir = os.path.join(root_path, f"0x{h:016x}")
            os.makedirs(anchor_dir, exist_ok=True)
            
            # Static Data
            with open(os.path.join(anchor_dir, "data.json"), "w") as f:
                json.dump(data["response"], f, indent=2)
            
            # Optional WASM logic
            if data["wasm"]:
                with open(os.path.join(anchor_dir, "logic.wasm"), "wb") as f:
                    # In a real system, we'd copy the actual WASM binary
                    f.write(b"WASM_STUB_" + data["wasm"].encode())

        print(f"Compilation complete. CDN structure built at: {root_path}")

if __name__ == "__main__":
    compiler = SemanticCompiler()
    
    # Define Vocabulary
    compiler.add_concept("status", ["check", "health", "report"], weight=10)
    compiler.add_concept("system", ["core", "engine", "platform"], weight=2)
    compiler.add_concept("primary", ["alpha", "main"], weight=5)
    
    # Define Anchors (Valid Routes)
    compiler.add_anchor(["status", "system"], {
        "status": "OPERATIONAL",
        "load": 0.42,
        "message": "All systems nominal."
    }, wasm_module="status_checker")

    compiler.add_anchor(["status", "primary", "system"], {
        "node": "ALPHA",
        "status": "ACTIVE",
        "uptime": "99.99%"
    }, wasm_module="node_resolver")

    # Compile to local 'cdn_mock' directory
    compiler.compile_cdn("./cdn_mock")
