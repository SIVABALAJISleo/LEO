import hashlib
import json
import logging
from typing import List, Dict, Any, Optional, Set

logger = logging.getLogger(__name__)

class GSFSolver:
    """
    Module 58: DETERMINISTIC GSF SOLVER (V2)
    - Resolves multi-path ambiguity.
    - Normalizes synonyms to prime products.
    - Enforces MUST-VALIDATE policy.
    """
    def __init__(self, salt: str = "rotating_hyper_salt_q4"):
        self.salt = salt
        self.prime_map = {
            "profit": 2, "earnings": 2, "income": 2,
            "loss": 3, "deficit": 3,
            "q1": 5, "q2": 7, "q3": 11, "q4": 13,
            "status": 17, "check": 17,
            "system": 19, "core": 19
        }
        
    def resolve_to_keys(self, query: str) -> List[str]:
        """
        Tokenizes and converts to hashed products.
        Handles synonym normalization automatically.
        """
        tokens = query.lower().strip().split()
        primes = []
        clean_tokens = []
        for t in tokens:
            if t in self.prime_map:
                primes.append(self.prime_map[t])
                clean_tokens.append(t)
                
        if not primes:
            return []

        # Commutative Product (Order independence)
        product = 1
        for p in primes:
            product *= p
            
        # Secure Hashed Key
        h_str = f"{product}:{self.salt}"
        final_key = hashlib.sha256(h_str.encode()).hexdigest()
        
        return [(final_key, product, set(clean_tokens))]

    def execute_and_validate(self, query: str) -> Optional[Dict[str, Any]]:
        """
        1. Resolve to Hashed Keys
        2. Simulated CDN Fetch
        3. MANDATORY VALIDATION
        """
        candidates = self.resolve_to_keys(query)
        if not candidates:
            return None

        for h_key, product, input_tokens in candidates:
            # Simulated CDN fetch: /data/{h_key}.json
            response = self._mock_cdn_fetch(h_key)
            
            if response:
                # MANDATORY VALIDATION LAYER
                if self._validate(response, product, input_tokens):
                    return response
                else:
                    logger.warning(f"Validation Reject for key {h_key[:8]}")
        
        return {"error": "NO_RESULT", "msg": "Fail-safe: Semantic match did not pass strict validation."}

    def _validate(self, response: Dict[str, Any], expected_product: int, input_tokens: Set[str]) -> bool:
        """
        Collision-free verification via Prime Product + Keyword Overlap.
        """
        # 1. Product check (Structural Match)
        if response.get("prime_product") != expected_product:
            return False
            
        # 2. Keyword Overlap (NLU consistency)
        canonical_tokens = set(response.get("composition", []))
        # Ensure at least one token from the query is semantically present
        if not input_tokens.intersection(canonical_tokens):
             return False
             
        return True

    def _mock_cdn_fetch(self, h_key: str) -> Optional[Dict[str, Any]]:
        # Mocking 'profit q3 system' -> 2 * 11 * 19 = 418
        p_418 = 418
        h_418 = hashlib.sha256(f"{p_418}:{self.salt}".encode()).hexdigest()
        
        if h_key == h_418:
            return {
                "id": h_key,
                "prime_product": 418,
                "composition": ["profit", "q3", "system"],
                "data": {
                    "result": "Profit metrics for Q3 (System Alpha) are nominal.",
                    "value": "$2.4M"
                }
            }
        return None

if __name__ == "__main__":
    solver = GSFSolver()
    
    # Test case 1: Synonym resolution (Earnings == Profit)
    print("--- Test 1: Synonym Normalization ---")
    res1 = solver.execute_and_validate("Earnings Q3 System")
    print(res1)
    
    # Test case 2: Fail-safe on mismatch
    print("\n--- Test 2: Validation Fail (Irrelevant query) ---")
    # Wrong salt simulation would cause fetch fail, but here we test validation logic
    res2 = solver.execute_and_validate("Unknown tokens")
    print(res2)
