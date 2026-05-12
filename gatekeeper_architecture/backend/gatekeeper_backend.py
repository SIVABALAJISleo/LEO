import json
import os
import hashlib
import time

"""
GATEKEEPER BACKEND - THE DETERMINISTIC CORE
Zero Interpretation. Pure Alignment.
"""

class GatekeeperBackend:
    def __init__(self, cdn_path="./cdn"):
        self.cdn_path = cdn_path
        self.mphf_table = {}
        self.n = 0
        self.g = []
        self.load_mphf_config()

    def load_mphf_config(self):
        config_path = os.path.join(self.cdn_path, "mphf_config.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)
                self.g = config["g"]
                self.n = config["n"]
                print(f"Loaded MPHF Routing Table (Keys: {self.n})")

    def canonicalize(self, query_obj):
        """
        LAYER 3: LOGIC VALIDATOR
        Strict conversion of JSON -> CANONICAL_STRING
        """
        required = ["DOMAIN", "ENTITY", "METRIC", "TIME", "FILTER"]
        for field in required:
            if field not in query_obj:
                return None, f"MISSING_FIELD: {field}"
        
        # Build canonical form
        canonical = "|".join([
            query_obj["DOMAIN"],
            query_obj["ENTITY"],
            query_obj["METRIC"],
            query_obj["TIME"],
            query_obj["FILTER"]
        ])
        return canonical, None

    def get_id(self, key):
        """
        LAYER 4: MPHF ROUTING
        O(1) Perfect Hash Lookup
        """
        if not self.g: return -1
        
        # h1 and h2 (must match compiler)
        h1 = int(hashlib.md5(key.encode()).hexdigest(), 16) % len(self.g)
        h2 = int(hashlib.sha1(key.encode()).hexdigest(), 16) % self.n
        
        d = self.g[h1]
        idx = (h2 + d) % self.n
        return idx

    def execute(self, query_json):
        """
        THE GATEKEEPER PIPELINE
        """
        start = time.perf_counter()
        
        # 1. Parse JSON
        try:
            query_obj = json.loads(query_json)
        except:
            return self._fail("INVALID_JSON", start)

        # 2. Canonicalize & Fast Reject
        canonical, error = self.canonicalize(query_obj)
        if error:
            return self._fail(error, start)

        # 3. MPHF Routing
        target_id = self.get_id(canonical)
        
        # 4. CDN Fetch (O(1))
        # The ID is used directly as the filename
        target_path = os.path.join(self.cdn_path, f"{target_id}.json")
        
        if not os.path.exists(target_path):
            return self._fail("NOT_SUPPORTED_COMBINATION", start)

        with open(target_path, "r") as f:
            data = json.load(f)
        
        # 5. Strict Verification (Double Check)
        if data.get("canonical_key") != canonical:
            return self._fail("MPHF_COLLISION_OR_INVALID_ENTRY", start)

        duration = (time.perf_counter() - start) * 1000
        
        return {
            "status": "SUCCESS",
            "id": target_id,
            "latency": f"{duration:.4f}ms",
            "result": data["content"]
        }

    def _fail(self, code, start):
        duration = (time.perf_counter() - start) * 1000
        return {
            "status": "ERROR",
            "error_code": code,
            "latency": f"{duration:.4f}ms"
        }

if __name__ == "__main__":
    # Test valid query
    valid_query = json.dumps({
        "DOMAIN": "SYSTEM",
        "ENTITY": "ALPHA_NODE",
        "METRIC": "STATUS",
        "TIME": "REALTIME",
        "FILTER": "NONE"
    })
    
    # Test invalid query (Missing field)
    invalid_query = json.dumps({
        "DOMAIN": "SYSTEM",
        "ENTITY": "ALPHA_NODE"
    })

    backend = GatekeeperBackend(cdn_path="./cdn_gatekeeper")
    print("\n[GATEKEEPER PROCESS: VALID]")
    print(backend.execute(valid_query))
    
    print("\n[GATEKEEPER PROCESS: INVALID]")
    print(backend.execute(invalid_query))
