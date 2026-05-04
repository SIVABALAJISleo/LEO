from typing import Optional, Dict, Any

class DSLParser:
    """
    1) INPUT GATE (STRICT DSL)
    - strict grammar
    - strict types
    - bounded size
    """
    def __init__(self, allowed_domains: List[str] = ["MATH", "LOGIC", "CODE_TRANSFORM"]):
        self.allowed_domains = allowed_domains

    def parse(self, user_input: str) -> Optional[Dict[str, Any]]:
        # Mock DSL parsing logic
        if len(user_input) > 1000: return None
        
        # Simulated parsing: {domain}: {command}
        if ":" not in user_input: return None
        
        domain, command = user_input.split(":", 1)
        domain = domain.strip().upper()
        
        if domain not in self.allowed_domains:
            return None
            
        return {
            "domain": domain,
            "command": command.strip()
        }
吐
