from enum import Enum
from typing import Dict, Any

class Route(Enum):
    OPEN = "open"     # Fast, direct return
    CLOSED = "closed" # Verified, deterministic loop

class HybridRouter:
    """
    3. ROUTER
    - simple -> return directly (OPEN)
    - complex/critical -> send to CLOSED loop
    """
    def route(self, intent: str, text: str) -> Route:
        # Criticality keywords
        critical_keywords = {"code", "calculate", "sum", "math", "script", "logic", "verify"}
        
        text_lower = text.lower()
        if any(word in text_lower for word in critical_keywords) or "code" in intent:
            return Route.CLOSED
            
        # Default to OPEN for greetings and general queries
        if len(text) < 30 and intent == "general":
            return Route.OPEN
            
        return Route.CLOSED # Safety first: default to verification
