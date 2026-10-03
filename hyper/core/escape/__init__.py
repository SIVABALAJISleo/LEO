"""
hyper/core/escape/__init__.py
Breakthrough Engines A through K and Minimal Sufficient Computation.
"""
from hyper.core.escape.minimal_computation import MinimalSufficientComputation, CandidateEscapePlan
from hyper.core.escape.delta_engine import ExactDeltaEngine, ExactDeltaState
from hyper.core.escape.early_termination import CertifiedEarlyTerminationEngine
from hyper.core.escape.exact_reuse import ExactReuseEngine, SemanticCacheKey, CacheEntryState
from hyper.core.escape.structure_discovery import StructureDiscoveryEngine, StructureEvidence, MatrixStructureType
from hyper.core.escape.low_rank_engine import LowRankEngine, FactorizationType, LowRankFactorizationResult
from hyper.core.escape.slicing_engine import OutputDirectedSlicingEngine
from hyper.core.escape.information_escape import InformationTheoreticEscapeEngine, SufficientStatisticsSummary
from hyper.core.escape.speculative_engine import SpeculativeEngine, SpeculativeExecutionReport
from hyper.core.escape.temporal_engine import TemporalIncrementalEngine, TemporalWorkAccount
from hyper.core.escape.representation_escape import RepresentationEscapeEngine, RepresentationFormat
from hyper.core.escape.algorithm_substitution import AlgorithmSubstitutionEngine

__all__ = [
    "MinimalSufficientComputation",
    "CandidateEscapePlan",
    "ExactDeltaEngine",
    "ExactDeltaState",
    "CertifiedEarlyTerminationEngine",
    "ExactReuseEngine",
    "SemanticCacheKey",
    "CacheEntryState",
    "StructureDiscoveryEngine",
    "StructureEvidence",
    "MatrixStructureType",
    "LowRankEngine",
    "FactorizationType",
    "LowRankFactorizationResult",
    "OutputDirectedSlicingEngine",
    "InformationTheoreticEscapeEngine",
    "SufficientStatisticsSummary",
    "SpeculativeEngine",
    "SpeculativeExecutionReport",
    "TemporalIncrementalEngine",
    "TemporalWorkAccount",
    "RepresentationEscapeEngine",
    "RepresentationFormat",
    "AlgorithmSubstitutionEngine",
]
