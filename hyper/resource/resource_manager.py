"""
hyper/resource/resource_manager.py
==================================
Resource Manager & Memory Pool Engine (Section 32):
Tracks CPU, RAM, Intel UHD, shared memory buffers, and queues.
Provides pre-allocated memory pools, buffer reuse, pressure detection,
and graceful degradation under tight memory limits.
"""

from typing import Dict, Any, List, Optional
import numpy as np


class MemoryPool:
    """
    Fixed-size pre-allocated buffer pool to eliminate malloc/free overhead.
    """
    def __init__(self, buffer_size_bytes: int = 1048576, pool_capacity: int = 16):
        self.buffer_size = buffer_size_bytes
        self.capacity = pool_capacity
        self._available_buffers: List[bytearray] = [bytearray(buffer_size_bytes) for _ in range(pool_capacity)]
        self._in_use = 0

    def acquire(self) -> Optional[bytearray]:
        if self._available_buffers:
            self._in_use += 1
            return self._available_buffers.pop()
        return None

    def release(self, buf: bytearray) -> None:
        if len(self._available_buffers) < self.capacity and len(buf) == self.buffer_size:
            self._available_buffers.append(buf)
            self._in_use = max(0, self._in_use - 1)


class ResourceManager:
    """
    Coordinates hardware resource allocation across CPU, RAM, and UHD.
    """
    def __init__(self, max_ram_mb: float = 8192.0):
        self.max_ram_mb = max_ram_mb
        self.pools: Dict[int, MemoryPool] = {
            1048576: MemoryPool(1048576, 16), # 1MB buffers
            4194304: MemoryPool(4194304, 8),  # 4MB buffers
        }

    def check_pressure(self, requested_bytes: int) -> bool:
        """Returns True if requested allocation is safe within budget."""
        return (requested_bytes / (1024 ** 2)) < self.max_ram_mb
