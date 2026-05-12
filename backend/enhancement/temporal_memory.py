"""
Temporal Memory
Stores last N responses per user to ensure continuity without LLM history passes.
"""
from collections import deque

class TemporalMemory:
    def __init__(self, capacity: int = 5):
        self.history = {}  # user_id -> deque of last N strings
        self.capacity = capacity

    def store(self, user_id: str, answer: str):
        if user_id not in self.history:
            self.history[user_id] = deque(maxlen=self.capacity)
        self.history[user_id].append(answer)

    def get_context(self, user_id: str) -> str:
        """Returns a summarized string of recent interactions."""
        if user_id not in self.history:
            return ""
        recent = list(self.history[user_id])
        return " | ".join(recent[-2:]) # Return last two for brevity

global_temporal_memory = TemporalMemory()
