"""
hyper_v3/frontend/workload_loader.py
Loads and validates standardized computation workloads.
"""

from typing import Dict, Any, Callable, Optional


class WorkloadLoader:
    """Registry and loader for standard computational workloads."""
    _registry: Dict[str, Callable[[], Dict[str, Any]]] = {}

    @classmethod
    def register(cls, name: str, factory: Callable[[], Dict[str, Any]]):
        cls._registry[name] = factory

    @classmethod
    def load(cls, name: str) -> Optional[Dict[str, Any]]:
        if name in cls._registry:
            return cls._registry[name]()
        return None

    @classmethod
    def list_workloads(cls) -> list:
        return list(cls._registry.keys())
