"""
hyper_v2/cache/residency_cache.py
Persistent hardware residency manager keeping recurring models and static BVH lattices pinned in memory.
"""

from typing import Dict, Any, Optional


class MemoryResidencyCache:
    """Pins static scene BVHs, model weights, and embedding indexes across frames."""

    _resident_objects: Dict[str, Any] = {}

    @classmethod
    def pin(cls, key: str, data: Any):
        cls._resident_objects[key] = data

    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        return cls._resident_objects.get(key)

    @classmethod
    def has(cls, key: str) -> bool:
        return key in cls._resident_objects

    @classmethod
    def clear(cls):
        cls._resident_objects.clear()
