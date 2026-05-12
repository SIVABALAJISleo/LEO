from typing import Dict, Any, List

class InputContractEngine:
    """
    1️⃣ INPUT CONTRACT ENGINE
    Detect: Missing data, Invalid formats, Low-confidence inputs
    """
    def __init__(self):
        self.required_fields = ["intent", "context"]

    def validate(self, user_input: str) -> Dict[str, Any]:
        # 1. Missing data check
        missing = [f for f in self.required_fields if f not in user_input.lower()]
        
        # 2. Format check
        is_valid_format = len(user_input) > 10
        
        # 3. Confidence check (simulated OOD)
        is_ood = "????" in user_input
        
        if missing:
            return {"status": "INSUFFICIENT_DATA", "missing": missing}
        if not is_valid_format:
            return {"status": "INVALID_FORMAT", "reason": "Input too short or malformed."}
        if is_ood:
            return {"status": "LOW_CONFIDENCE_INPUT", "reason": "Pattern not recognized by input contract."}
            
        return {"status": "VALID"}

