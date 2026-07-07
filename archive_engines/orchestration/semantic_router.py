import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class SemanticRouter:
    """
    Module 45: SEMANTIC ROUTING HUB (SimHash + Validation)
    - Receives 64-bit SimHash from client.
    - Performs Nearest-Match (Hamming) retrieval.
    - Enforces MANDATORY Validation Layer.
    """
    def __init__(self, threshold: int = 5):
        self.threshold = threshold # Hamming max distance
        self.registry: Dict[int, str] = {} # Hash -> Canonical Query
        self.knowledge_base: Dict[int, Any] = {} # Hash -> Response Data
        
    def add_route(self, raw_query: str, hash_val: int, data: Any):
        self.registry[hash_val] = raw_query.lower()
        self.knowledge_base[hash_val] = data

    def route(self, client_hash: int, raw_query: str) -> Optional[Dict[str, Any]]:
        """
        Main Routing Logic:
        1. Exact Match
        2. Hamming Match (Top-K)
        3. Validation Layer (Keyword Overlap)
        """
        # 1. Exact Match (The sub-1ms path)
        if client_hash in self.knowledge_base:
            return self._validate_and_return(client_hash, raw_query, "EXACT_LOCK")

        # 2. Candidate Retrieval (Hamming Distance)
        candidates = []
        for reg_hash in self.knowledge_base.keys():
            dist = self._hamming_distance(client_hash, reg_hash)
            if dist <= self.threshold:
                candidates.append((dist, reg_hash))
        
        if not candidates:
            return None # Fail Fast
            
        # Sort by distance
        candidates.sort(key=lambda x: x[0])
        best_dist, best_hash = candidates[0]
        
        return self._validate_and_return(best_hash, raw_query, f"HAMMING_APPROX_{best_dist}")

    def _validate_and_return(self, matched_hash: int, raw_query: str, method: str) -> Optional[Dict[str, Any]]:
        """
        CRITICAL VALIDATION LAYER
        Ensures the matched canonical query actually relates to the input.
        """
        canonical = self.registry[matched_hash]
        input_keywords = set(raw_query.lower().split())
        canonical_keywords = set(canonical.split())
        
        # Keyword Overlap check (Zero guessing rule)
        overlap = input_keywords.intersection(canonical_keywords)
        if len(overlap) < 1:
            logger.warning(f"Validation Failed: '{raw_query}' matched '{canonical}' but zero keyword overlap.")
            return None
            
        return {
            "data": self.knowledge_base[matched_hash],
            "telemetry": {
                "routing_method": method,
                "confidence": len(overlap) / len(canonical_keywords),
                "deterministic": True
            }
        }

    def _hamming_distance(self, h1: int, h2: int) -> int:
        return bin(h1 ^ h2).count('1')

if __name__ == "__main__":
    router = SemanticRouter(threshold=10)
    
    # Pre-populate registry (Simulated Offline Batch)
    # Query: "How is the system status" -> Hash: 12345
    router.add_route("system status nominal", 12345, {"message": "All systems OK"})
    router.add_route("reboot core alpha", 67890, {"message": "Reboot sequence initiated"})

    # Test Case 1: Exact Match
    print("\nTest 1: Exact Match")
    print(router.route(12345, "system status"))

    # Test Case 2: Similar Phrase (Hamming)
    # Input has slight variation, hash will be close to 12345
    # For simulation, we'll use 12346 (dist 1)
    print("\nTest 2: Semantic Match (Distance 1)")
    print(router.route(12346, "system status check"))

    # Test Case 3: Ambiguous/Bad Match (Validation Failure)
    # Hash might be close by luck, but keywords don't match
    print("\nTest 3: Security Validation Fail (Wrong keywords)")
    print(router.route(12346, "weather in london"))
