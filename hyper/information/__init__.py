"""
hyper/information
=================
Information-Theoretic Analysis Layer for LEO/HYPER.
Fulfills Section 36 of the Breakthrough Master Architecture.
"""

from .info_analyzer import InformationRequirementAnalyzer
from .entropy_analyzer import InformationTheoreticAnalyzer, InformationProfile

__all__ = [
    "InformationRequirementAnalyzer",
    "InformationTheoreticAnalyzer",
    "InformationProfile",
]

