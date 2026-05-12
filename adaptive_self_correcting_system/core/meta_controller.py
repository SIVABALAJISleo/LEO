from typing import List, Tuple

class MetaUncertaintyController:
    """
    16. META-UNCERTAINTY CONTROLLER
    - if system_instability or calibration_error: ABSTAIN
    """
    def __init__(self, stability_threshold: float = 0.95):
        self.stability_threshold = stability_threshold

    def check_system_integrity(self, model_latencies: List[float], error_rate: float) -> Tuple[bool, str]:
        # Mock stability check
        # Sudden spike in error rate or latency indicates instability
        if error_rate > 0.05:
            return False, "SYSTEM_UNTRUSTED: Error rate exceeded safety threshold."
            
        if any(l > 5000 for l in model_latencies):
            return False, "SYSTEM_UNTRUSTED: Compute instability / latency spike detected."
            
        return True, "SYSTEM_STABLE"

