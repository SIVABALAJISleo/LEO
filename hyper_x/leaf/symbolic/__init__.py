"""
hyper_x/leaf/symbolic/__init__.py
=================================
EFSC (Execution-Free Symbolic Collapse) Package.
"""

from .expression import SymExpr, OpType
from .simplifier import AlgebraicSimplifier
from .factorizer import AlgebraicFactorizer
from .loop_collapse import LoopCollapseEngine, LoopInvariantReport
from .closed_form import ClosedFormSolver, ClosedFormResult
from .polyhedral import PolyhedralAnalyzer, PolyhedralDomain
from .equivalence import EquivalenceProver

__all__ = [
    "SymExpr",
    "OpType",
    "AlgebraicSimplifier",
    "AlgebraicFactorizer",
    "LoopCollapseEngine",
    "LoopInvariantReport",
    "ClosedFormSolver",
    "ClosedFormResult",
    "PolyhedralAnalyzer",
    "PolyhedralDomain",
    "EquivalenceProver",
]
