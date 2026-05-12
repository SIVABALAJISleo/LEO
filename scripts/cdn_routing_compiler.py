import json
import os
import hashlib

class CDNRoutingCompiler:
    """
    Offline Compiler for the CDN-based Semantic Router.
    Generates /data/{hash}.json files for absolute zero-backend compute.
    """
    def __init__(self, output_dir: str = "dist/cdn_data"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def compile(self, routing_map: dict):
        """
        Input: Map of {canonical_query: data}
        Workflow: Compute SimHash -> Write Static JSON
        """
        print(f"--- CDN Routing Compiler (SimHash-64) ---")
        
        for query, content in routing_map.items():
            # For this script, we'll use a mocked SimHash (First 16 chars of SHA256)
            h_str = hashlib.sha256(query.lower().strip().encode()).hexdigest()
            h_val = int(h_str[:16], 16)
            
            file_path = os.path.join(self.output_dir, f"{h_val}.json")
            
            payload = {
                "hash": h_val,
                "canonical": query,
                "data": content,
                "metadata": {
                    "v": 1,
                    "type": "semantic_route"
                }
            }
            
            with open(file_path, "w") as f:
                json.dump(payload, f, indent=2)
            
            print(f"Compiled: {query} -> {h_val}.json")

if __name__ == "__main__":
    routes = {
        "system status check": {"status": "nominal", "cpu": "2%"},
        "reboot engine alpha": {"status": "pending", "auth": "required"},
        "emergency shutdown core": {"status": "critical", "action": "HALT"}
    }
    
    compiler = CDNRoutingCompiler()
    compiler.compile(routes)
