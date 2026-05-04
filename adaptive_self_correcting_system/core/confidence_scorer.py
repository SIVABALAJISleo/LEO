from ..models.schemas import LeoSpec, ReasoningPath, VerificationReport

class ConfidenceScorer:
    """
    7. CONFIDENCE MODEL
    Score based on:
    - input clarity
    - agreement
    - verification success
    """
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold

    def calculate(self, 
                  spec: LeoSpec, 
                  agreement: bool, 
                  verification: VerificationReport,
                  clarification_needed: bool) -> float:
        
        score = 1.0
        
        # Penalty for lack of agreement
        if not agreement:
            score -= 0.3
            
        # Penalty for verification failure/partial success
        if not verification.success:
            score *= (verification.score / 100.0 if verification.score > 0 else 0.5)
            
        # Penalty for unclear input (missing fields)
        if clarification_needed:
            score -= 0.15
            
        # Penalty for lack of constraints
        if not spec.constraints:
            score -= 0.1
            
        return max(0.0, min(1.0, score))
