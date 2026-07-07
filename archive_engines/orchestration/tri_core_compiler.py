import json
import os
import re
import hashlib

"""
MPHF COMPILER (Minimal Perfect Hash Function)
Ensures O(1) collision-free routing for known intent keys.
"""

class MphfCompiler:
    def __init__(self, keys):
        self.keys = sorted(list(set(keys)))
        self.n = len(self.keys)
        self.size = self.n + (self.n // 2) # Slightly larger for easier discovery
        self.g = [0] * self.size
        self.hashes = {} # ID mapping

    def _h1(self, k):
        return int(hashlib.md5(k.encode()).hexdigest(), 16) % self.size

    def _h2(self, k):
        return int(hashlib.sha1(k.encode()).hexdigest(), 16) % self.size

    def build(self):
        # 1. Bucket keys by h1
        buckets = [[] for _ in range(self.size)]
        for k in self.keys:
            buckets[self._h1(k)].append(k)
        
        # 2. Sort buckets by size (largest first)
        buckets = sorted([(len(b), i, b) for i, b in enumerate(buckets) if b], reverse=True)
        
        occupied = [False] * self.n
        for _, b_idx, b_keys in buckets:
            d = 1
            item_idx = 0
            while item_idx < len(b_keys):
                slot = (self._h2(b_keys[item_idx]) + d) % self.n
                if occupied[slot] or slot in [ (self._h2(other) + d) % self.n for other in b_keys[:item_idx] ]:
                    d += 1
                    item_idx = 0
                else:
                    item_idx += 1
            
            self.g[b_idx] = d
            for k in b_keys:
                occupied[(self._h2(k) + d) % self.n] = True
        
        # 3. Build Final Table
        final_table = [None] * self.n
        for k in self.keys:
            idx = (self._h2(k) + self.g[self._h1(k)]) % self.n
            final_table[idx] = k
        
        print(f"MPHF Built for {self.n} keys. Zero collisions.")
        return {"g": self.g, "n": self.n, "table": final_table}

"""
TRI-CORE COMPILER (V3)
Integrates MSR, MPHF, and CDN anchor generation.
"""

class TriCoreCompilerV3:
    def __init__(self):
        self.bucket_dir = "./cdn_tricore"
        
    def compile_engine(self, dataset):
        os.makedirs(self.bucket_dir, exist_ok=True)
        
        # 1. Build MPHF for all unique queries
        queries = [item["query"] for item in dataset]
        mphf_gen = MphfCompiler(queries)
        mphf_gen.build()
        
        # 2. Generate CDN Anchors
        # We'll use the MPHF index as the ID for O(1) direct file access
        routing_table = {}
        for item in dataset:
            query = item["query"]
            idx = (mphf_gen._h2(query) + mphf_gen.g[mphf_gen._h1(query)]) % mphf_gen.n
            
            anchor_path = os.path.join(self.bucket_dir, f"{idx}.json")
            
            # Signature for validation
            tokens = set(re.findall(r'\w+', query.lower()))
            
            blob = {
                "id": idx,
                "domain": item["domain"],
                "signature": sorted(list(tokens)),
                "response": item["response"]
            }
            
            with open(anchor_path, "w") as f:
                json.dump(blob, f, indent=2)
            
            routing_table[query] = idx

        # 3. Save Engine Configuration
        config = {
            "mphf": {
                "g": mphf_gen.g,
                "n": mphf_gen.n
            }
        }
        with open(os.path.join(self.bucket_dir, "engine_config.json"), "w") as f:
            json.dump(config, f, indent=2)

if __name__ == "__main__":
    # Load 500 samples from msr_trainer.py output
    with open("msr_dataset_500.json", "r") as f:
        dataset = json.load(f)
    
    compiler = TriCoreCompilerV3()
    compiler.compile_engine(dataset)
    print(f"Tri-Core System Compiled. Anchors in {compiler.bucket_dir}")
