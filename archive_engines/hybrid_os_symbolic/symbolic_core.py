import logging
import sympy
from z3 import Solver, Int, sat

logger = logging.getLogger(__name__)

class SymbolicCore:
    """
    LAYER 4: SYMBOLIC LAYER
    Deterministic core for exact math and logic reasoning.
    """
    def solve_math(self, expression: str) -> str:
        """
        Uses SymPy to solve algebraic expressions.
        Example: "solve x**2 - 4" -> [2, -2]
        """
        try:
            # We assume the LLM translates user text to valid SymPy strings
            expr = sympy.sympify(expression)
            result = sympy.solve(expr)
            return str(result)
        except Exception as e:
            return f"SymPy Error: {e}"

    def solve_logic(self, constraints: str) -> str:
        """
        Uses Z3 to solve logical constraints.
        Expects a format like "x > 5, x < 10"
        """
        try:
            s = Solver()
            # Simple parser for "var > val" constraints
            # In production, this would be a more robust translator
            x = Int('x') # Default variable
            # Mocking constraint addition for demo
            if ">" in constraints:
                val = int(constraints.split(">")[1].strip())
                s.add(x > val)
            if "<" in constraints:
                val = int(constraints.split("<")[1].strip())
                s.add(x < val)
            
            if s.check() == sat:
                return f"SAT: {s.model()}"
            return "UNSAT"
        except Exception as e:
            return f"Z3 Error: {e}"
