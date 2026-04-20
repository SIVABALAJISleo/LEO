class ValidationLayer:
    """
    Module V: SYMBOLIC CONSTRAINT GATE
    - Strict logical validation.
    - Deterministic rule enforcement.
    """
    def __init__(self):
        self.forbidden_patterns = ["cmd", "bin/sh", "eval", "exec"]
        self.security_threshold = 0.85

    def check_validity(self, query: str, confidence: float) -> bool:
        """
        No-loop check for fast rejection.
        """
        # 1. Probability threshold
        if confidence < self.security_threshold:
            return False
            
        # 2. Pattern rejection (Fast check)
        query_lower = query.lower()
        for p in self.forbidden_patterns:
            if p in query_lower:
                return False
                
        return True
