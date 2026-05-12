from typing import List, Any, Tuple

class FallbackCascade:
    """
    5️⃣ FALLBACK CASCADE SYSTEM
    - if A fails: try B
    - if B fails: try C
    - if all fail: ABSTAIN
    """
    def execute(self, solvers: List[callable], user_input: str) -> Tuple[bool, Any, float, str]:
        results = []
        for solver in solvers:
            try:
                success, output, conf = solver(user_input)
                if success and conf > 0.85:
                    return True, output, conf, solver.__name__
                results.append((output, conf, solver.__name__))
            except Exception:
                continue
                
        # If no single solver is dominant, return the best effort for consensus
        return False, None, 0.0, "CASCADE_EXHAUSTED"

