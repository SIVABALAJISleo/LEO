import logging
from contextlib import contextmanager
from typing import Set

logger = logging.getLogger(__name__)

class LocalityViolation(Exception):
    pass

class LocalityManager:
    """
    Module D: LOCALITY GUARANTEE
    - Any interaction affects ONLY local state.
    - Zero global recomputation allowed.
    - Enforce strict spatial + logical isolation.
    """
    
    def __init__(self):
        self._active_context: Set[str] = set()
        self._is_locked = False

    @contextmanager
    def isolation_chamber(self, allowed_region_ids: Set[str]):
        """
        Context manager that defines the ONLY allowed regions for write access.
        """
        if self._is_locked:
            raise RuntimeError("Nested isolation chambers are not allowed.")
        
        self._is_locked = True
        self._active_context = allowed_region_ids
        try:
            yield
        finally:
            self._is_locked = False
            self._active_context = set()

    def assert_write_access(self, region_id: str):
        """
        Throw exception if writing to a region not in the current active context.
        """
        if not self._is_locked:
            # If no chamber is active, we assume UNSAFE global access (or we block it)
            # For strictness, we block it.
            raise LocalityViolation("Write attempted outside of Isolation Chamber.")
            
        if region_id not in self._active_context:
            raise LocalityViolation(f"Illegal Global Write: Attempted to write to {region_id} which is outside local context {self._active_context}")
        
    def check_access(self, region_id: str) -> bool:
        if not self._is_locked: return False
        return region_id in self._active_context
