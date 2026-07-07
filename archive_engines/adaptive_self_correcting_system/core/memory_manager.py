from typing import List, Dict, Optional
from ..models.schemas import MemoryEntry

class LeoAdaptiveMemory:
    """
    7) ADAPTIVE MEMORY (CONTROLLED)
    - Store correction ONLY if seen >=2 times
    - Never overwrite base logic
    - Decay stale patterns
    """
    def __init__(self, capacity: int = 1000):
        self.fast_memory: List[MemoryEntry] = []
        self.correction_counts: Dict[str, int] = {} # failure -> count
        self.correction_patterns: Dict[str, str] = {} # failure -> correction
        self.capacity = capacity

    def store_correction(self, failure_signature: str, correction: str):
        # 7) Controlled memory logic
        count = self.correction_counts.get(failure_signature, 0) + 1
        self.correction_counts[failure_signature] = count
        
        if count >= 2:
            if len(self.correction_patterns) >= self.capacity:
                self.correction_patterns.pop(next(iter(self.correction_patterns)))
            self.correction_patterns[failure_signature] = correction

    def get_correction(self, input_text: str) -> Optional[str]:
        for failure, correction in self.correction_patterns.items():
            if failure in input_text:
                return correction
        return None

    def store_entry(self, entry: MemoryEntry):
        if len(self.fast_memory) >= self.capacity:
            self.fast_memory.pop(0)
        self.fast_memory.append(entry)
