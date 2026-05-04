from typing import List, Any

class StrategySelector:
    """
    6️⃣ EXECUTION STRATEGY SELECTOR
    - retrieval, decomposition, approximation, cache
    """
    def select(self, task_type: str) -> str:
        if "RETRIEVAL" in task_type:
            return "use_retrieval"
        if "DECOMPOSE" in task_type:
            return "split_and_solve"
        if "APPROX" in task_type:
            return "use_approximation"
        return "use_small_model"

