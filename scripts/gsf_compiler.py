import json
import os
import hashlib
from itertools import combinations

class GSFDataCompiler:
    """
    Offline Compiler for GSF-Core.
    Generates exact-match semantic files via prime products.
    """
    def __init__(self, salt: str = "daily_hyper_salt_v1", output_dir: str = "dist/gsf_data"):
        self.salt = salt
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        # Token to Prime (Must match orchestrator)
        self.prime_map = {
            "status": 2, "check": 3, "alpha": 5, "beta": 7, "system": 11, "reboot": 13
        }

    def compile_combinations(self, combos: list):
        """
        Input: List of word sets
        Action: Product -> Hash -> JSON
        """
        print(f"--- GSF-Core Offline Compiler ---")
        for words, payload in combos:
            # 1. Product
            product = 1
            for w in words:
                product *= self.prime_map[w]
            
            # 2. Hash
            h_str = f"{product}:{self.salt}"
            final_hash = hashlib.sha256(h_str.encode()).hexdigest()
            
            # 3. Write JSON
            file_path = os.path.join(self.output_dir, f"{final_hash}.json")
            
            data = {
                "id": final_hash,
                "prime_product": product,
                "composition": words,
                "data": payload,
                "metadata": {
                    "source": "deterministic_gsf_v1",
                    "hash_type": "sha256_salted"
                }
            }
            
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            
            print(f"Compiled: {' '.join(words)} -> {final_hash[:16]}...json")

if __name__ == "__main__":
    # Define semantic training sets
    training_sets = [
        (["status", "check", "system"], {"msg": "System nominal check complete."}),
        (["reboot", "alpha"], {"msg": "Alpha node reboot scheduled."}),
        (["status", "alpha"], {"health": 99, "role": "primary"})
    ]
    
    compiler = GSFDataCompiler()
    compiler.compile_combinations(training_sets)
