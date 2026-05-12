import re
from typing import Tuple, Optional

class InputSanitizer:
    """
    1. INPUT SANITIZATION
    - Normalize text
    - Domain classifier
    - Socratic clarification
    """
    def __init__(self):
        self.allowed_domains = ["coding", "finance", "system"]

    def sanitize(self, raw_input: str) -> Tuple[bool, str, Optional[str]]:
        # Normalize
        clean = raw_input.strip().lower()
        clean = re.sub(r'\s+', ' ', clean)
        
        # Domain check
        if not any(domain in clean for domain in self.allowed_domains):
            return False, clean, "OUT_OF_DOMAIN: Input does not map to a recognized domain."
            
        # Ambiguity check (Socratic)
        if len(clean.split()) < 3:
            return False, clean, "AMBIGUOUS: Please provide more context or specific intent."
            
        return True, clean, None

