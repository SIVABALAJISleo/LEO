import json
import hashlib
import logging
from typing import List, Dict, Any, Optional
from .bpe_tokenizer import BPETokenizer
from .bloom_filter import SemanticBloomFilter

logger = logging.getLogger(__name__)

class HybridEdgeClient:
    """
    Module CL: HYBRID EDGE CLIENT (Runtime)
    - Zero-latency local resolution layer.
    - Implements Mip-Map Backoff for robust matching.
    """
    def __init__(self, manifest_path: str):
        with open(manifest_path, "r") as f:
            self.manifest = json.load(f)
        
        self.tokenizer = BPETokenizer()
        self.tokenizer.set_vocab(self.manifest["vocab"], {})
        self.tokenizer.canonical_map = {int(k): v for k, v in self.manifest["canonical_map"].items()}
        
        self.bloom_filter = SemanticBloomFilter(size=1024 * 8)
        self.bloom_filter.import_state(self.manifest["bloom_filter"])
        self.weights = {int(k): v for k, v in self.manifest["backoff_weights"].items()}

    def resolve(self, query: str) -> Dict[str, Any]:
        """
        Main entry point for Edge Resolution.
        Tries exact match -> backoff match -> fallback.
        """
        # 1. Tokenize & Canonicalize
        token_ids = self.tokenizer.tokenize(query)
        canonical_ids = self.tokenizer.collapse_synonyms(token_ids)
        
        # 2. Iterative Mip-Map Backoff
        # Current logic: Drop least-weight tokens one by one until hit or empty
        working_set = sorted(list(set(canonical_ids)))
        
        while len(working_set) > 0:
            # Generate deterministic key for current set
            # Sort to ensure O(1) order independence
            working_set.sort()
            key_blob = ",".join(map(str, working_set))
            test_hash = hashlib.sha256(key_blob.encode()).hexdigest()
            print(f"[CLIENT] Checking Key: {key_blob} -> Hash: {test_hash}")
            
            # 3. Check Bloom Filter (Zero Latency)
            if self.bloom_filter.check(test_hash):
                # Potential hit - request from CDN
                logger.info(f"Edge Hit detected: {test_hash}. Fetching...")
                result = self._fetch_from_cdn(test_hash)
                if result:
                    return {
                        "status": "SUCCESS",
                        "match_type": "EXACT" if len(working_set) == len(canonical_ids) else "BACKOFF",
                        "data": result,
                        "residual_entropy": len(canonical_ids) - len(working_set)
                    }
            
            # 4. Apply Backoff (Mip-Map logic)
            # Find token with lowest weight and discard it
            # (In this demo, weights are uniform, so we drop the last one)
            working_set.pop() 
            logger.info(f"Backing off. Remaining tokens: {len(working_set)}")

        # 5. Fallback - Control delegated to isolated system
        return {
            "status": "UNKNOWN",
            "message": "No deterministic anchor found after backoff.",
            "mode": "FALLBACK_TRIGGERED"
        }

    def _fetch_from_cdn(self, resource_hash: str) -> Optional[Dict[str, Any]]:
        # Mock CDN fetch logic
        # In production, this is a simple GET /data/{hash}.json
        # Here we simulate finding the file on disk
        data_path = f"c:/Users/sivab/OneDrive/Documents/HYPER/remix-of-remix-of-remix-of-nvidia-inspired-design-main/cdn_mock/data/{resource_hash}.json"
        try:
            with open(data_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"CDN Consistency Error: Hash {resource_hash} in Bloom Filter but not in Storage.")
            return None
