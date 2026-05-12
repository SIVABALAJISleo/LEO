import numpy as np

class RuntimeVerificationLayer:
    """
    Module 13 — Runtime Verification Layer
    Prevents approximation drift by enforcing exact verification fallbacks on uncertainty.
    """
    def __init__(self, confidence_threshold=0.85):
        self.confidence_threshold = confidence_threshold
        
    def evaluate_confidence(self, approximate_output):
        """
        Estimates the structural confidence of an approximated output.
        """
        variance = np.var(approximate_output)
        if variance < 1e-3 or variance > 1e3:
            return 0.4 # Low confidence
        return 0.95 # High confidence
        
    def execute_with_verification(self, input_data, approximate_fn, exact_fn):
        """
        approximate-first, verify-on-uncertainty.
        """
        approx_out = approximate_fn(input_data)
        confidence = self.evaluate_confidence(approx_out)
        
        if confidence >= self.confidence_threshold:
            return approx_out, "APPROXIMATION_ACCEPTED"
            
        exact_out = exact_fn(input_data)
        return exact_out, "EXACT_FALLBACK_TRIGGERED"
