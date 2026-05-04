from typing import List, Callable, Any

class LazyEngine:
    """
    1. LAZY EXECUTION (MANDATORY)
    - Convert task into thunks
    - Execute ONLY next required step
    """
    def __init__(self):
        self.thunks: List[Callable] = []

    def add_step(self, func: Callable, *args, **kwargs):
        self.thunks.append(lambda: func(*args, **kwargs))

    def execute_next(self) -> Any:
        if not self.thunks: return None
        thunk = self.thunks.pop(0)
        return thunk()

    def has_next(self) -> bool:
        return len(self.thunks) > 0

