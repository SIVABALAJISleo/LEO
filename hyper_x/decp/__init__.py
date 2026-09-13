"""
hyper_x.decp
============
Deterministic Exact-Compute & Parity Layer (HYPER-DECP).
"""

from .manifest import FrozenExecutionManifest
from .comparator import CrossHardwareComparator
from .engine import DECPEngine

__all__ = [
    "FrozenExecutionManifest",
    "CrossHardwareComparator",
    "DECPEngine",
]
