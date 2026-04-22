import json
import os
import hashlib
import itertools

"""
GATEKEEPER COMPILER
Generates the Deterministic World.
"""

class GatekeeperCompiler:
    def __init__(self, output_dir="./cdn_gatekeeper"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.domains = ["SYSTEM", "NETWORK", "SECURITY", "HARDWARE"]
        self.entities = {
            "SYSTEM": ["ALPHA_NODE", "BETA_NODE", "CORE_ROUTING"],
            "NETWORK": ["GATEWAY_01", "PEERING_LNK", "DNS_RESOLVER"],
            "SECURITY": ["FIREWALL_P1", "IDS_AGENT", "AUTH_SVC"],
            "HARDWARE": ["CPU_LNK_01", "MEM_ARRAY", "DISK_VOL_0"]
        }
        self.metrics = ["STATUS", "LATENCY", "LOAD", "ERROR_RATE", "UPTIME"]
        self.times = ["LAST_1H", "LAST_24H", "REALTIME"]
        self.filters = ["NONE", "CRITICAL_ONLY", "NOMINAL_ONLY"]

    def generate_all_keys(self):
        keys = []
        for d in self.domains:
            for e in self.entities[d]:
                for m in self.metrics:
                    for t in self.times:
                        for f in self.filters:
                            keys.append(f"{d}|{e}|{m}|{t}|{f}")
        return keys

    def build_mphf(self, keys):
        n = len(keys)
        size = n + (n // 2)
        g = [0] * size
        
        buckets = [[] for _ in range(size)]
        for k in keys:
            h1 = int(hashlib.md5(k.encode()).hexdigest(), 16) % size
            buckets[h1].append(k)
        
        buckets = sorted([(len(b), i, b) for i, b in enumerate(buckets) if b], reverse=True)
        
        occupied = [False] * n
        for _, b_idx, b_keys in buckets:
            d = 1
            item_idx = 0
            while item_idx < len(b_keys):
                slot = (int(hashlib.sha1(b_keys[item_idx].encode()).hexdigest(), 16) + d) % n
                if occupied[slot] or slot in [ (int(hashlib.sha1(other.encode()).hexdigest(), 16) + d) % n for other in b_keys[:item_idx] ]:
                    d += 1
                    item_idx = 0
                else:
                    item_idx += 1
            
            g[b_idx] = d
            for k in b_keys:
                idx = (int(hashlib.sha1(k.encode()).hexdigest(), 16) + d) % n
                occupied[idx] = True
        
        return g, n

    def compile(self):
        print("1. Generating valid permutations...")
        keys = self.generate_all_keys()
        print(f"Total Canonical Keys: {len(keys)}")
        
        print("2. Building Minimal Perfect Hash table...")
        g, n = self.build_mphf(keys)
        
        print("3. Exporting MPHF config...")
        with open(os.path.join(self.output_dir, "mphf_config.json"), "w") as f:
            json.dump({"g": g, "n": n}, f)
            
        print("4. Pre-filling CDN anchors...")
        for k in keys:
            # Map key to index via MPHF
            h1 = int(hashlib.md5(k.encode()).hexdigest(), 16) % len(g)
            h2 = int(hashlib.sha1(k.encode()).hexdigest(), 16) % n
            idx = (h2 + g[h1]) % n
            
            blob = {
                "canonical_key": k,
                "timestamp": "2026-04-21T17:54Z",
                "content": f"DET_RESPONSE for {k}. Status: NOMINAL."
            }
            
            with open(os.path.join(self.output_dir, f"{idx}.json"), "w") as f:
                json.dump(blob, f)
        
        print("Compilation Complete.")

if __name__ == "__main__":
    compiler = GatekeeperCompiler()
    compiler.compile()
