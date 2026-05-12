import json
import os
import hashlib
from typing import List, Dict

# DETERMINISTIC OFFLINE PIPELINE

class PrecomputePipeline:
    def __init__(self, data_source: str, output_dir: str):
        self.data_source = data_source
        self.output_dir = output_dir
        self.mphf_map = {}

    def run(self):
        print("Starting Gatekeeper Precomputation...")
        
        # 1. Load & Normalize
        raw_data = self._load_data()
        
        # 2. Generate Result JSONs (CDN Assets)
        for entry in raw_data:
            canonical_key = self._generate_canonical_key(entry)
            result_id = self._generate_mphf_id(canonical_key)
            
            # Save static result
            self._save_cdn_asset(result_id, entry)
            self.mphf_map[canonical_key] = result_id

        # 3. Save MPHF Metadata
        self._save_metadata()
        print(f"Pipeline Complete. Generated {len(self.mphf_map)} assets.")

    def _load_data(self) -> List[Dict]:
        # Mock loading
        return [
            {"domain": "finance", "entity": "revenue", "metric": "total", "value": 5000000},
            {"domain": "ops", "entity": "latency", "metric": "p99", "value": 120}
        ]

    def _generate_canonical_key(self, entry: Dict) -> str:
        # Strict ordering: domain|entity|metric
        return f"{entry['domain']}|{entry['entity']}|{entry['metric']}|none|none".lower()

    def _generate_mphf_id(self, key: str) -> str:
        # Deterministic ID generation
        return hashlib.md5(key.encode()).hexdigest()[:8]

    def _save_cdn_asset(self, asset_id: str, data: Dict):
        path = os.path.join(self.output_dir, f"results/{asset_id}.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f)

    def _save_metadata(self):
        path = os.path.join(self.output_dir, "metadata/mphf.json")
        with open(path, 'w') as f:
            json.dump(self.mphf_map, f)

if __name__ == "__main__":
    pipeline = PrecomputePipeline("raw_data.csv", "public/cdn")
    pipeline.run()
