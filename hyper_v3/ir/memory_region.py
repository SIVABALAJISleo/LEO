"""
hyper_v3/ir/memory_region.py
Represents memory buffers, residency states, and pooling metadata.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MemoryRegion:
    region_id: str
    size_bytes: int
    alignment: int = 64
    current_device: str = "CPU"
    is_dirty: bool = False
    is_pooled: bool = False
    pool_id: Optional[str] = None
