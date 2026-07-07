import json
import os
import hashlib
import re

"""
OFFLINE SIMHASH COMPILER
Builds bucketted CDN structure with Stable routing.
"""

class SimHashCompiler:
    def __init__(self, bucket_dir="./cdn_simhash"):
        self.bucket_dir = bucket_dir
        self.noise = {"the", "a", "an", "is", "are", "do", "how", "what", "of", "in", "on", "for", "check"}
        
    def _fnv1a(self, s):
        h = 0xcbf29ce484222325
        for char in s:
            h ^= ord(char)
            h = (h * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
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
                "domain": item.get("domain", "GENERAL"),
                "context": context,
                "response": item["response"],
                "tags": item.get("tags", []),
                "sh": f"0x{sh:016x}"
            }
            
            with open(path, "w") as f:
                json.dump(blob, f, indent=2)
            
            ctx_label = f"Ctx: {context}" if context else "Ctx: NONE"
            print(f"Compiled: {query} ({ctx_label}) -> {path}")

if __name__ == "__main__":
    compiler = SimHashCompiler()
    
if __name__ == "__main__":
    compiler = SimHashCompiler()
    
    dataset_path = "msr_dataset_500.json"
    if os.path.exists(dataset_path):
        with open(dataset_path, "r") as f:
            data = json.load(f)
        print(f"Loading {len(data)} training samples...")
        compiler.build_cdn(data)
    else:
        print("Error: msr_dataset_500.json not found. Run msr_trainer.py first.")
