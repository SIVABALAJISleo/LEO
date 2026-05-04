from typing import Tuple

class ComplexityEngine:
    """
    2️⃣ COMPLEXITY ESTIMATION (CRITICAL)
    HIGH: large matrix ops, real-time video, large-scale training, full rendering
    NORMAL: everything else
    """
    def estimate(self, user_input: str) -> str:
        input_lower = user_input.lower()
        
        # GPU-dominant patterns
        high_compute_patterns = [
            "matrix multiplication", "video processing", "train model",
            "ray tracing", "3d rendering", "molecular dynamics",
            "massive data analysis"
        ]
        
        if any(p in input_lower for p in high_compute_patterns) or len(user_input) > 5000:
            return "HIGH"
            
        return "NORMAL"

