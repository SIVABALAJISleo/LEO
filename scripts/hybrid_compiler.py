import json
import os
import hashlib

class HybridDataCompiler:
    """
    Offline compiler for Hybrid-GSF Engine.
    Pre-renders deterministic semantic shards for CDN hosting.
    """
    def __init__(self, salt: str = "daily_rotating_salt_0421", output_dir: str = "dist/hybrid_gsf"):
        self.salt = salt
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        # Canonical Vocabulary
        self.prime_map = {
            "status": 2, "system": 3, "reboot": 5, "alpha": 7, "beta": 11
        }

    def compile(self, intent_bundles: list):
        """
        Input: [([tokens], payload)]
        Process: Product -> Hash -> JSON
        """
        print(f"--- Hybrid-GSF Offline Compiler ---")
        for tokens, payload in intent_bundles:
            product = 1
            for t in tokens:
                product *= self.prime_map[t]
            
            # Salted Hash for CDN Security
            h_str = f"{product}:{self.salt}"
            final_hash = hashlib.sha256(h_str.encode()).hexdigest()
            
            file_path = os.path.join(self.output_dir, f"{final_hash}.json")
            
            data = {
                "id": final_hash,
                "prime_product": product,
                "keywords": tokens,
                "data": payload,
                "metadata": {
                    "v": "3.0.H",
                    "caching": "immutable",
                    "authoritative": True
                }
            }
            
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            
            print(f"Compiled: {' '.join(tokens)} -> {final_hash[:16]}.json")

if __name__ == "__main__":
    # Canonical knowledge bundles
    bundles = [
        (["status", "system"], {"health": 100, "status": "ACTIVE"}),
        (["reboot", "alpha"], {"action": "NODE_RESTART", "target": "ALPHA"}),
        (["status", "beta"], {"health": 92, "status": "NOMINAL"})
    ]
    
    compiler = HybridDataCompiler()
    compiler.compile(bundles)
