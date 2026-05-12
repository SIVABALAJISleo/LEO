from typing import Dict, Any

class ReframingEngine:
    """
    3️⃣ REFRAME / SIMPLIFY ENGINE
    - Convert heavy problems into CPU-friendly ones
    - Generate -> Retrieve + compose
    - Full search -> Top-K retrieval
    """
    def reframe(self, user_input: str) -> Dict[str, Any]:
        task_lower = user_input.lower()
        
        # Simulation -> Lookup / approximation
        if "simulate" in task_lower:
            return {"task": "LOOKUP_APPROXIMATION", "original": user_input}
            
        # Generate -> Retrieve + compose
        if "generate" in task_lower or "write" in task_lower:
            return {"task": "RETRIEVE_COMPOSE", "original": user_input}
            
        # Full search -> Top-K
        if "search" in task_lower or "find all" in task_lower:
            return {"task": "TOP_K_RETRIEVAL", "original": user_input}
            
        return {"task": "DIRECT_SOLVE", "original": user_input}

