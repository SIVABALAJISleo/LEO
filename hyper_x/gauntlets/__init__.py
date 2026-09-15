"""
hyper_x/gauntlets/__init__.py
=============================
Package exports for HYPER gauntlets:
- Exact Compute Gauntlet (Part 36)
- Reduced-Work Escape Gauntlet (Part 37)
- Anti-Structure Falsification Gauntlet (Part 32)
"""

from .exact_gauntlet import HyperExactGauntlet, ExactGauntletResult
from .escape_gauntlet import HyperEscapeGauntlet, EscapeGauntletResult
from .anti_structure import AntiStructureGauntlet, AntiStructureResult

__all__ = [
    "HyperExactGauntlet",
    "ExactGauntletResult",
    "HyperEscapeGauntlet",
    "EscapeGauntletResult",
    "AntiStructureGauntlet",
    "AntiStructureResult",
]
