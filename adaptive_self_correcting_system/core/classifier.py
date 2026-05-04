from ..models.schemas import TaskComplexity

class TaskClassifier:
    """
    3. TASK CLASSIFICATION
    - LOW → direct response
    - MEDIUM → 2 reasoning paths
    - HIGH → full verification loop
    """
    def __init__(self):
        pass

    async def classify(self, user_input: str) -> TaskComplexity:
        # Heuristic-based classification
        # HIGH: Complexity keywords or multi-step logic
        # MEDIUM: Solving specific problems
        # LOW: General information or simple transformations
        
        words = user_input.lower().split()
        length = len(words)
        
        high_complexity_markers = ["build", "system", "architect", "validate", "verify", "optimize"]
        medium_complexity_markers = ["solve", "calculate", "write", "parse", "format"]
        
        if any(m in words for m in high_complexity_markers) or length > 50:
            return TaskComplexity.HIGH
        elif any(m in words for m in medium_complexity_markers) or length > 20:
            return TaskComplexity.MEDIUM
        else:
            return TaskComplexity.LOW
