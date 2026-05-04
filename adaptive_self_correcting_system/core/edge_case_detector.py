class EdgeCaseDetector:
    """
    4️⃣ EDGE-CASE DETECTION ENGINE
    - Rare patterns
    - Out-of-distribution (OOD)
    - Adversarial patterns
    """
    def is_edge_case(self, user_input: str) -> bool:
        # 1. Rare pattern check (mock)
        is_rare = "anomaly" in user_input.lower()
        
        # 2. OOD check (mock)
        is_ood = len(user_input) > 1000
        
        # 3. Adversarial check (mock)
        is_adversarial = "ignore all previous instructions" in user_input.lower()
        
        return is_rare or is_ood or is_adversarial
吐
