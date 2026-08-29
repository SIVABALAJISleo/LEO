"""
hyper_ares/__init__.py
=============================================================================
HYPER-ARES: Adaptive Representation & Elimination Search Package
=============================================================================
Autonomous 20-step representation search loop that extracts application contracts,
analyzes structural invariants, generates competing representations, executes
heterogeneous CPU+iGPU plans, and verifies output independently.
"""

from hyper_ares.structure_detector import StructureDetector, StructuralProfile
from hyper_ares.representation_searcher import RepresentationSearcher, CandidateRepresentation
from hyper_ares.predictive_residual import PredictiveResidualEngine, ResidualResult
from hyper_ares.engine import HyperAresEngine, AresExecutionResult

__all__ = [
    "StructureDetector",
    "StructuralProfile",
    "RepresentationSearcher",
    "CandidateRepresentation",
    "PredictiveResidualEngine",
    "ResidualResult",
    "HyperAresEngine",
    "AresExecutionResult"
]
