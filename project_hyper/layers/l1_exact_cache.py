from typing import Optional
import hashlib

class ExactCache:
    """
    Layer 1: Exact Cache
    Direct lookup for identical queries. Target: 20-40% hit rate.
    """
    def __init__(self):
        self.store = {} # In-memory dictionary as proxy for Redis

    def _get_hash(self, text: str) -> str:
        return hashlib.sha256(text.strip().lower().encode()).hexdigest()

    def get(self, query: str) -> Optional[str]:
        h = self._get_hash(query)
        return self.store.get(h)

    def set(self, query: str, response: str):
        h = self._get_hash(query)
        self.store[h] = response

if __name__ == "__main__":
    cache = ExactCache()
    cache.set("Hi", "Hello! How can I help you today?")
    print(f"Hit: {cache.get('Hi')}")
    print(f"Miss: {cache.get('Hello')}")
