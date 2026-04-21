import json
import os
import hashlib

class GSFPrecompiler:
    """
    Offline Compiler for Zero-Compute GSF Engine.
    Generates deterministic data shards for the CDN.
    """
    def __init__(self, salt: str = "rotating_hyper_salt_q4", output_dir: str = "dist/gsf_v2"):
        self.salt = salt
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        # Canonical Prime Mapping
        self.prime_map = {
            "profit": 2, "loss": 3, "q1": 5, "q2": 7, "q3": 11, "q4": 13,
            "status": 17, "system": 19
        }

    def compile_intent(self, canonical_tokens: list, payload: dict):
        """
        Computes Prime Product -> Salted Hash -> Static JSON
        """
        product = 1
        for t in canonical_tokens:
            product *= self.prime_map[t]
        
        # Salted SHA256 ensures CDN security
        h_str = f"{product}:{self.salt}"
        h_key = hashlib.sha256(h_str.encode()).hexdigest()
        
        file_path = os.path.join(self.output_dir, f"{h_key}.json")
        
        data = {
            "id": h_key,
            "prime_product": product,
            "composition": canonical_tokens,
            "data": payload,
            "runtime_metadata": {
                "hash_v": "sha256_gsf_v2",
                "security": "rotating_salt_active"
            }
        }
        
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
            
        print(f"Compiled: {' '.join(canonical_tokens)} -> {h_key[:12]}.json")

if __name__ == "__main__":
    compiler = GSFPrecompiler()
    
    # Precompiling common business intents
    compiler.compile_intent(["profit", "q3", "system"], {"result": "Up 12.4%", "context": "Nominal"})
    compiler.compile_intent(["status", "system"], {"result": "ACTIVE", "cores": 128})
    compiler.compile_intent(["loss", "q2"], {"result": "-$0.4M", "warning": "Low Margin"})
