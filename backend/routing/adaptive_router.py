import logging
import re
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class AdaptiveModelRouter:
    """
    Subsystem 8: Adaptive Model Router.
    Inference Avoidance Mechanism. Routes queries to the cheapest possible solver.
    Hierarchy: Rule Engine -> Calculator -> Search -> Tiny Model -> Medium Model -> Large Model.
    """
    def __init__(self):
        self.rules: Dict[str, str] = {
            "hello": "Hello! I am LEO AI V∞ Research Edition. How can I assist you?",
            "who are you": "I am LEO, a highly optimized artificial intelligence.",
            "what is your version": "V∞ Intelligence Resonance Architecture (IRA)."
        }
        
    def _check_calculator(self, query: str) -> Tuple[bool, str]:
        """Detects if a query is purely mathematical and can be solved by eval() safely."""
        # Simple math regex: numbers, operators, parens, spaces
        if re.match(r'^[\d\+\-\*\/\(\)\.\s]+$', query) and any(char.isdigit() for char in query):
            try:
                # In production, use a safe evaluator (like `ast.literal_eval` or custom parsing)
                # For this prototype, we use a controlled eval block inside a try-catch.
                # Safe sandbox implementation applies here.
                safe_dict = {"__builtins__": None}
                result = eval(query, safe_dict, safe_dict)
                return True, str(result)
            except Exception:
                pass
        return False, ""

    def _check_rules(self, query: str) -> Tuple[bool, str]:
        """Checks if a query matches a hardcoded, zero-compute heuristic rule."""
        q = query.lower().strip()
        # Exact match
        if q in self.rules:
            return True, self.rules[q]
        # Substring match
        for key, val in self.rules.items():
            if key in q and len(q) < 50:
                return True, val
        return False, ""

    def route_query(self, query: str) -> str:
        """
        Determines the optimal execution path for the given prompt.
        Returns the routing destination string (e.g., 'RULE_ENGINE', 'CALCULATOR', 'LARGE_MODEL').
        """
        # 1. Rule Engine (Zero Inference)
        is_rule, _ = self._check_rules(query)
        if is_rule:
            logger.info("Routing query to RULE_ENGINE (Zero-Compute).")
            return "RULE_ENGINE"
            
        # 2. Calculator (Zero Inference)
        is_math, _ = self._check_calculator(query)
        if is_math:
            logger.info("Routing query to CALCULATOR (Zero-Compute).")
            return "CALCULATOR"
            
        # 3. Simple Search / Retrieval (Low Compute)
        search_keywords = ["search", "find", "where", "lookup", "definition"]
        if any(w in query.lower() for w in search_keywords) and len(query.split()) < 15:
            logger.info("Routing query to RETRIEVAL_ENGINE (Low-Compute).")
            return "RETRIEVAL_ENGINE"
            
        # 4. Tiny Model (e.g. 100M parameter BERT for classification/short answers)
        if len(query.split()) < 20:
            logger.info("Routing query to TINY_MODEL (Medium-Compute).")
            return "TINY_MODEL"
            
        # 5. Large Model (Full Transformer - Avoid unless necessary)
        logger.info("Routing query to LARGE_MODEL (High-Compute - Unavoidable).")
        return "LARGE_MODEL"
