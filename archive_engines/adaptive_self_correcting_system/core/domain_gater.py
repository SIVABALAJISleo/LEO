from typing import List, Tuple
from ..models.schemas import DomainStatus

class DomainGater:
    """
    1. DOMAIN GATING
    - Allowed domains must be explicitly defined
    - If input ∉ domain → REJECT
    """
    def __init__(self, allowed_domains: List[str] = ["coding", "math", "structured data"]):
        self.allowed_domains = allowed_domains

    async def validate(self, user_input: str) -> Tuple[DomainStatus, str]:
        # In a production system, this would use a small classifier LLM
        # For now, we use keyword-based detection as a heuristic
        input_lower = user_input.lower()
        
        # Coding keywords
        coding_kw = ["python", "code", "function", "write", "program", "script", "test", "debug"]
        # Math keywords
        math_kw = ["calculate", "solve", "formula", "equation", "math", "sum", "integral"]
        # Data keywords
        data_kw = ["json", "csv", "xml", "parse", "data", "format", "schema"]
        
        detected_domains = []
        if any(kw in input_lower for kw in coding_kw): detected_domains.append("coding")
        if any(kw in input_lower for kw in math_kw): detected_domains.append("math")
        if any(kw in input_lower for kw in data_kw): detected_domains.append("structured data")
        
        # Check intersection
        valid = any(domain in self.allowed_domains for domain in detected_domains)
        
        if valid:
            return DomainStatus.PASS, f"Detected domain(s): {', '.join(detected_domains)}"
        else:
            return DomainStatus.FAIL, f"Input does not fall into allowed domains: {', '.join(self.allowed_domains)}"
