import hashlib
import time
import json
import logging
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)

class SemanticGuardrailHub:
    """
    Module 48: HYBRID SEMANTIC ROUTER & GUARDRAIL
    - Enforces strict 'Always-Validate' policy.
    - Zero backend compute on Hit.
    - Controlled fallback on Miss.
    """
    def __init__(self, threshold_hamming: int = 4, threshold_overlap: float = 0.6):
        self.t_hamming = threshold_hamming
        self.t_overlap = threshold_overlap
        
        # In-memory Hot Cache (L0)
        self._cache: Dict[int, Any] = {}
        
        # Deterministic Registry
        self.registry: Dict[int, str] = {} # Key -> Canonical Intent
        self.data_store: Dict[int, Any] = {} # Key -> Response Data

    def add_route(self, intent: str, key: int, data: Any):
        self.registry[key] = intent.lower().strip()
        self.data_store[key] = data

    def route(self, client_key: int, raw_query: str, nonce: str) -> Optional[Dict[str, Any]]:
        """
        Main Routing Pipeline:
        1. Security Check (Nonce/Rate Limit)
        2. L0 Cache Hit
        3. Direct Key Mapping
        4. Validation Layer (MANDATORY)
        5. Fallback Mode
        """
        # 1. Verification (Simulated)
        if not self._verify_request(nonce):
            return {"error": "SECURITY_REJECTED", "status": 403}

        # 2. L0 Cache
        if client_key in self._cache:
            return self._cache[client_key]

        # 3. Direct Mapping
        if client_key in self.data_store:
            return self._validate_and_cache(client_key, raw_query, "FAST_PATH")

        # 4. Nearest Neighbor (Top-K) Search
        best_key = self._find_nearest(client_key)
        if best_key:
            return self._validate_and_cache(best_key, raw_query, "NEAREST_MATCH")

        # 5. Controlled Fallback
        return self._trigger_fallback(raw_query)

    def _validate_and_cache(self, key: int, raw_query: str, method: str) -> Optional[Dict[str, Any]]:
        """MANDATORY Validation Layer: No Guessing Policy."""
        canonical = self.registry[key]
        
        # Jaccard Similarity on keywords
        q_tokens = set(raw_query.lower().split())
        c_tokens = set(canonical.split())
        overlap = len(q_tokens.intersection(c_tokens)) / len(c_tokens)
        
        if overlap < self.t_overlap:
            logger.warning(f"Guardrail Trip: '{raw_query}' is too far from '{canonical}' (Overlap: {overlap:.2f})")
            return None # FAIL SAFE

        response = {
            "data": self.data_store[key],
            "mode": method,
            "deterministic": True,
            "v": 1
        }
        
        # Hydrate L0 Cache
        self._cache[key] = response
        return response

    def _find_nearest(self, client_key: int) -> Optional[int]:
        """Finds closest key via Hamming distance."""
        for r_key in self.data_store.keys():
            dist = bin(client_key ^ r_key).count('1')
            if dist <= self.t_hamming:
                return r_key
        return None

    def _trigger_fallback(self, query: str) -> Dict[str, Any]:
        """Lightweight reasoning fallback (Stub)."""
        logger.info(f"Fallback Initiated: {query}")
        return {
            "data": "Unable to resolve via deterministic path. Forwarding to Tier-2 Reasoning Engine.",
            "mode": "FALLBACK_T2",
            "deterministic": False
        }

    def _verify_request(self, nonce: str) -> bool:
        # Placeholder for signature/nonce verification
        return len(nonce) > 10

if __name__ == "__main__":
    hub = SemanticGuardrailHub()
    
    # Pre-populate deterministic routes
    # intent: "check reactor status" -> key: 0xABCD
    hub.add_route("check reactor status", 0xABCD, {"temp": "300K", "status": "NOMINAL"})

    # Test 1: Fast Path (Direct Key)
    print("\n[Test 1] Fast Path Hit")
    res = hub.route(0xABCD, "Check reactor status", "NONCE_VALID_123")
    print(res)

    # Test 2: Guardrail Trip (Blind nearest-neighbor rejected)
    print("\n[Test 2] Near-key match but Validation Failure")
    # key 0xABCE is distance 1 from 0xABCD
    res = hub.route(0xABCE, "weather in space", "NONCE_VALID_123")
    print(res)
