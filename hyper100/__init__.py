"""
HYPER-100: Universal Contract-Driven Computational Elimination Runtime
======================================================================
Target: Intel Core i5-12450H + Intel UHD Graphics (48 EU) + 16GB RAM + Windows 11
Philosophy: "Do not make weak hardware imitate powerful hardware.
             Make the powerful hardware's workload irrelevant."
"""

from .contract_engine import ExecutionContract, ContractExactness, VerificationStatus, ContractViolationError
from .workload_analyzer import WorkloadAnalyzer, ComputationGraph, ComputationNode, WorkloadProfile
from .information_reduction import InformationReductionEngine, InformationProfile
from .redundancy_discovery import RedundancyDiscoveryEngine, RedundancyReport
from .elimination_engine import ComputationEliminationEngine, EliminationReport
from .cache_reuse_engine import CacheReuseEngine, CacheMode, CacheLookupResult
from .sparsity_engine import SparsityEngine, SparseFormat, SparsityReport
from .low_rank_engine import LowRankEngine, LowRankDecomposition, LowRankReport
from .precision_engine import PrecisionEngine, PrecisionFormat, PrecisionReport
from .prediction_engine import PredictionEngine, PredictionMode, PredictionReport
from .algorithmic_reformulation import AlgorithmicReformulationEngine, ReformulationReport
from .heterogeneous_scheduler import HeterogeneousScheduler, DeviceTarget, DeviceAllocation
from .verification_engine import VerificationEngine, VerificationReport
from .adaptive_fallback import AdaptiveFallbackEngine, FallbackTrace
from .optimization_search import OptimizationSearchEngine, OptimizationStrategy
from .proof_carrying_record import ProofCarryingRecord, ProvenanceLedger
from .runtime import Hyper100Runtime
from .universal_orchestrator import UniversalOrchestrator

__version__ = "100.0.0"
__all__ = [
    "ExecutionContract",
    "ContractExactness",
    "VerificationStatus",
    "ContractViolationError",
    "WorkloadAnalyzer",
    "ComputationGraph",
    "ComputationNode",
    "WorkloadProfile",
    "InformationReductionEngine",
    "InformationProfile",
    "RedundancyDiscoveryEngine",
    "RedundancyReport",
    "ComputationEliminationEngine",
    "EliminationReport",
    "CacheReuseEngine",
    "CacheMode",
    "CacheLookupResult",
    "SparsityEngine",
    "SparseFormat",
    "SparsityReport",
    "LowRankEngine",
    "LowRankDecomposition",
    "LowRankReport",
    "PrecisionEngine",
    "PrecisionFormat",
    "PrecisionReport",
    "PredictionEngine",
    "PredictionMode",
    "PredictionReport",
    "AlgorithmicReformulationEngine",
    "ReformulationReport",
    "HeterogeneousScheduler",
    "DeviceTarget",
    "DeviceAllocation",
    "VerificationEngine",
    "VerificationReport",
    "AdaptiveFallbackEngine",
    "FallbackTrace",
    "OptimizationSearchEngine",
    "OptimizationStrategy",
    "ProofCarryingRecord",
    "ProvenanceLedger",
    "Hyper100Runtime",
    "UniversalOrchestrator",
]
