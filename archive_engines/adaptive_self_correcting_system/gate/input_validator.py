import json
from typing import Dict, Any, Optional, Tuple

class InputValidator:
    """
    1. GATE LAYER (STRICT INPUT CONTROL)
    - Build input validator using schema + grammar constraints
    - Reject out-of-domain inputs immediately
    """
    def __init__(self, dsl_schema: Dict[str, Any]):
        self.dsl_schema = dsl_schema

    def validate(self, raw_input: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        try:
            parsed = json.loads(raw_input)
            # Check domain and schema constraints
            if "intent" not in parsed or "domain" not in parsed:
                return False, None, "INVALID_FORMAT: Missing intent/domain"
            
            # Simple domain check
            if parsed["domain"] not in self.dsl_schema["allowed_domains"]:
                return False, None, f"OUT_OF_DOMAIN: {parsed['domain']}"
            
            return True, parsed, "VALID"
        except json.JSONDecodeError:
            return False, None, "INVALID_SYNTAX: Must be structured JSON/DSL"

