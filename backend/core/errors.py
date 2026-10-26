"""
backend/core/errors.py
Core error hierarchies and strict ledger constraints for Project LEO.
"""

class MockFallbackForbiddenError(RuntimeError):
    """
    Raised when HYPER_STRICT_LEDGER=1 is enabled and an unverified mock fallback
    or simulated object is invoked instead of a real native CPU/iGPU calculation.
    """
    pass
