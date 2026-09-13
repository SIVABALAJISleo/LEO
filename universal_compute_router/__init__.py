"""
Universal Compute Router package for LEO / HYPER.
Provides heterogeneous dispatch and hardware-aware task routing.
"""
from .adaptive_dispatch import AdaptiveDispatchRouter

__all__ = ["AdaptiveDispatchRouter"]
