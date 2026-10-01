"""
hyper/backends/__init__.py
==========================
Execution Backends for LEO/HYPER: Optimized CPU and Genuine Intel UHD Graphics.
"""

from hyper.backends.cpu_backend import CpuBackend
from hyper.backends.igpu_backend import IntelUhdBackend

__all__ = [
    "CpuBackend",
    "IntelUhdBackend",
]
