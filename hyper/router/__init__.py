"""
hyper/router/__init__.py
========================
Fail-Closed Universal Router Package for LEO/HYPER.
"""

from hyper.router.universal_router import (
    UniversalRouter,
    RouterResult,
    RouterOutcome,
)

__all__ = [
    "UniversalRouter",
    "RouterResult",
    "RouterOutcome",
]
