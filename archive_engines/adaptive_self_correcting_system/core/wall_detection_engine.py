
class WallDetectionEngine:
    """
    3️⃣ WALL DETECTION ENGINE
    A. COMPUTE COMPLEXITY (HIGH vs NORMAL)
    B. CHAOS DETECTION (STABLE, MODERATE, CHAOTIC)
    C. PREDICTABILITY CHECK (HIGH vs LOW)
    """
    def detect_zone(self, user_input: str) -> str:
        input_lower = user_input.lower()
        
        # A. Compute Complexity
        is_high_complexity = any(p in input_lower for p in ["train", "rendering", "dense matrix", "pixel processing"])
        
        # B. Chaos Detection (Mock ratio)
        # Assuming stable for standard text
        chaos_state = "STABLE"
        if "video" in input_lower or "dynamic" in input_lower:
            chaos_state = "MODERATE"
            
        # C. Predictability Check
        is_low_predictability = "random" in input_lower or "unknown" in input_lower
        
        # FINAL WALL DECISION
        if is_high_complexity or chaos_state == "CHAOTIC" or is_low_predictability:
            return "WALL_ZONE"
            
        return "SAFE_ZONE"

