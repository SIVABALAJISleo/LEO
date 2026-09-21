"""
hyper/universal/parity/__init__.py
==================================
Multi-Dimensional Parity & RTX 5090 Reference Subsystem.
"""

from .parity_vector import ParityVector, ParityClass
from .rtx5090_reference import RTX5090Model
from .cache_discipline import CacheState, CacheDisciplineValidator
from .scorecard import UniversalParityScorecard

__all__ = [
    "ParityVector",
    "ParityClass",
    "RTX5090Model",
    "CacheState",
    "CacheDisciplineValidator",
    "UniversalParityScorecard",
]
