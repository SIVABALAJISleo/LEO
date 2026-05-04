from typing import Tuple, Dict, Any
from ..models.schemas import RiskLevel

class RiskEngine:
    """
    STAGE 0 — DOMAIN + RISK PRECHECK
    """
    def __init__(self):
        self.allowed_domains = ["finance", "system", "code"]
        self.critical_keywords = ["delete", "transfer", "root", "admin"]

    def precheck(self, user_input: str) -> Tuple[bool, RiskLevel, str]:
        # Domain check
        domain_match = any(d in user_input.lower() for d in self.allowed_domains)
        if not domain_match:
            return False, RiskLevel.LOW, "OUT_OF_SCOPE: Input does not map to a verified domain."
            
        # Risk check
        is_high_risk = any(k in user_input.lower() for k in self.critical_keywords)
        risk = RiskLevel.HIGH if is_high_risk else RiskLevel.LOW
        
        return True, risk, "Domain and Risk precheck passed."

