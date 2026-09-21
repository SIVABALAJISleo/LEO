"""
hyper/universal/parity/cache_discipline.py
==========================================
Enforces Section 25 (Cache Discipline) & Section 24 (No Benchmark Cheating).
Labels execution state: COLD, WARM, CACHED, MEMOIZED, PRECOMPUTED, INCREMENTAL.
Rejects mismatched comparisons (e.g. comparing cached HYPER to cold RTX) as INVALID_COMPARISON.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional


class CacheState(str, Enum):
    COLD = "COLD"
    WARM = "WARM"
    CACHED = "CACHED"
    MEMOIZED = "MEMOIZED"
    PRECOMPUTED = "PRECOMPUTED"
    INCREMENTAL = "INCREMENTAL"


class CacheDisciplineValidator:
    """Guarantees fair, uncorrupted comparative benchmarking."""

    @staticmethod
    def validate_comparison(
        hyper_cache_state: CacheState,
        reference_cache_state: CacheState,
    ) -> tuple[bool, Optional[str]]:
        # Comparing a cached or precomputed result against a cold baseline is cheating
        if hyper_cache_state in (CacheState.CACHED, CacheState.MEMOIZED, CacheState.PRECOMPUTED) and reference_cache_state == CacheState.COLD:
            return False, "INVALID_COMPARISON: Cannot benchmark cached/memoized HYPER result against COLD reference baseline."

        return True, None
