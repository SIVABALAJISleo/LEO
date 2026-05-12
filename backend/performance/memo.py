import functools
import hashlib
import json
from typing import Any, Callable, Dict, Optional
import time

class GlobalMemo:
    """
    High-performance memoization layer for CPU-heavy tasks.
    Supports TTL and versioned cache keys.
    """
    def __init__(self, ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl

    def _make_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        # Create a stable hash for the function call
        serialized = json.dumps({"f": func_name, "a": args, "k": kwargs}, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def memoize(self, func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = self._make_key(func.__name__, args, kwargs)
            now = time.time()
            
            if key in self.cache:
                entry = self.cache[key]
                if now - entry["timestamp"] < self.ttl:
                    return entry["result"]
            
            result = func(*args, **kwargs)
            self.cache[key] = {
                "result": result,
                "timestamp": now
            }
            return result
        return wrapper

global_memo = GlobalMemo()
