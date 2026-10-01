"""
hyper/obligation
================
Computational Obligation Elimination & Minimal Sufficient Computation Engine.
Fulfills Sections 9, 10, 11, 12, 13 of the Breakthrough Master Architecture.
"""

from hyper.obligation.coa import (
    ComputationalObligationAnalyzer,
    ComputationalObligationGraph,
    ObligationClassification,
    ObligationNode,
    ObligationEdge,
    DependencyType,
)
from hyper.obligation.msc import (
    MinimalSufficientComputationEngine,
    MinimalComputationResult,
    ComputationalObligationScore,
)

__all__ = [
    "ComputationalObligationAnalyzer",
    "ComputationalObligationGraph",
    "ObligationClassification",
    "ObligationNode",
    "ObligationEdge",
    "DependencyType",
    "MinimalSufficientComputationEngine",
    "MinimalComputationResult",
    "ComputationalObligationScore",
]
