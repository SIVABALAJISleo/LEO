"""
hyper/universal/information/__init__.py
=======================================
Information Boundary and Redundancy Analysis Subsystem.
"""

from .entropy_analyzer import EntropyAnalyzer
from .dependency_pruner import DependencyPruner
from .boundary_engine import InformationBoundaryEngine, InformationBoundaryProfile

__all__ = [
    "EntropyAnalyzer",
    "DependencyPruner",
    "InformationBoundaryEngine",
    "InformationBoundaryProfile",
]
