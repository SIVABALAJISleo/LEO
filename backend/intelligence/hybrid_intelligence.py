"""
backend/intelligence/hybrid_intelligence.py
Subsystem 7: Hybrid Intelligence Engine.
Combines symbolic rules, classical algorithms, and deterministic logic
to answer queries without neural inference whenever possible.
"""

import re
import math
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class RuleEngine:
    """
    Symbolic rule engine. Pattern-match based deterministic responses.
    Zero neural inference cost.
    """
    def __init__(self):
        self.rules: List[Dict[str, Any]] = []

    def add_rule(self, pattern: str, handler, description: str = ""):
        """Register a regex pattern with a handler function."""
        self.rules.append({
            "pattern": re.compile(pattern, re.IGNORECASE),
            "handler": handler,
            "description": description
        })

    def evaluate(self, query: str) -> Optional[str]:
        """Returns the first matching rule's answer, or None."""
        for rule in self.rules:
            m = rule["pattern"].search(query)
            if m:
                try:
                    result = rule["handler"](m, query)
                    logger.info(f"Rule Engine matched: {rule['description']}")
                    return str(result)
                except Exception as e:
                    logger.error(f"Rule handler error: {e}")
        return None


class ClassicalSolver:
    """
    Classical algorithm library: sorting, graph algorithms,
    prime detection, Fibonacci, etc. — all deterministic O-complexity.
    """

    @staticmethod
    def is_prime(n: int) -> bool:
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True

    @staticmethod
    def fibonacci(n: int) -> int:
        """O(n) iterative Fibonacci."""
        if n <= 0:
            return 0
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

    @staticmethod
    def gcd(a: int, b: int) -> int:
        while b:
            a, b = b, a % b
        return a

    @staticmethod
    def lcm(a: int, b: int) -> int:
        return abs(a * b) // ClassicalSolver.gcd(a, b)

    @staticmethod
    def sort_numbers(nums: List[float]) -> List[float]:
        return sorted(nums)


class HybridIntelligenceEngine:
    """
    Master orchestrator for Hybrid Intelligence.
    Attempts symbolic / classical solutions before routing to neural inference.
    """

    def __init__(self):
        self.rule_engine = RuleEngine()
        self.solver = ClassicalSolver()
        self._register_builtin_rules()

    def _register_builtin_rules(self):
        # Prime number rule
        def prime_handler(match, query):
            n = int(match.group(1))
            result = self.solver.is_prime(n)
            return f"{n} is {'a prime' if result else 'not a prime'} number."

        self.rule_engine.add_rule(
            r"is (\d+) (?:a )?prime",
            prime_handler,
            "Prime detection"
        )

        # Fibonacci rule
        def fib_handler(match, query):
            n = int(match.group(1))
            return f"The {n}th Fibonacci number is {self.solver.fibonacci(n)}."

        self.rule_engine.add_rule(
            r"fibonacci(?:\s+of)?\s+(\d+)|(\d+)(?:th|st|nd|rd)?\s+fibonacci",
            lambda m, q: fib_handler(m if m.group(1) else m, q),
            "Fibonacci computation"
        )

        # GCD rule
        def gcd_handler(match, query):
            a, b = int(match.group(1)), int(match.group(2))
            return f"GCD({a}, {b}) = {self.solver.gcd(a, b)}"

        self.rule_engine.add_rule(
            r"gcd\s+(?:of\s+)?(\d+)\s+(?:and\s+)?(\d+)",
            gcd_handler,
            "GCD computation"
        )

        # Square root rule
        def sqrt_handler(match, query):
            n = float(match.group(1))
            return f"√{n} = {math.sqrt(n):.6f}"

        self.rule_engine.add_rule(
            r"(?:square root|sqrt)\s+(?:of\s+)?(\d+(?:\.\d+)?)",
            sqrt_handler,
            "Square root"
        )

    def solve(self, query: str) -> Optional[str]:
        """
        Attempts deterministic symbolic resolution.
        Returns the answer string if solved, None if neural inference is required.
        """
        return self.rule_engine.evaluate(query)
