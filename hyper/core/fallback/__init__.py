"""
hyper/core/fallback/__init__.py
Fallback execution engine and fallback event logging.
"""
from hyper.core.fallback.engine import CanonicalFallbackEngine, FallbackEvent

__all__ = ["CanonicalFallbackEngine", "FallbackEvent"]
