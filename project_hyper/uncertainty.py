class UncertaintyHandler:
    """LAYER 8 — UNCERTAINTY HANDLING"""
    def __init__(self):
        pass
        
    def evaluate(self, response: str) -> float:
        """Assign a confidence score to the LLM's raw output."""
        confidence = 1.0
        uncertain_phrases = ["i think", "maybe", "not sure", "possibly", "i don't know"]
        
        lower_resp = response.lower()
        for phrase in uncertain_phrases:
            if phrase in lower_resp:
                confidence -= 0.3
                
        return max(0.0, confidence)
        
    def handle(self, response: str, confidence: float):
        if confidence < 0.6:
            return f"[UNCERTAINTY TRIGGERED - Confidence {confidence:.2f}]\nClarification needed or fallback required. Raw output: {response}"
        return response
