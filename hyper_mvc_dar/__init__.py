"""
HYPER MVC-DAR: Autonomous Minimum Verified Computation + Dynamic Algorithmic Reconfiguration Package.
"""

from .ir import DataType, OpType, TensorDescriptor, OpNode, ComputationGraph
from .contract import ContractClass, ExecutionTrack, ExecutionContract
from .sufficiency import InformationSufficiencyEngine
from .necessity import NecessityStatus, NecessityProofEngine
from .redundancy import RedundancyEngine
from .dead_work import DeadWorkEliminator
from .exact_transforms import ExactTransformationEngine
from .complexity import ComplexityReplacementEngine
from .sparsity import SparsityEngine
from .low_rank import LowRankEngine
from .representations import RepresentationType, RepresentationDiscoveryEngine
from .precision import PrecisionEngine
from .memory_engine import MemoryEngine
from .heterogeneous_fabric import HeterogeneousFabric
from .hardware_profiler import HardwareProfiler
from .prediction_verifier import PredictVerifyAcceptEngine
from .adaptive import AdaptiveComputeEngine
from .error_budget import ErrorBudgetTracker
from .algorithm_discovery import StrategyGenome, StrategySearchEngine
from .strategy_memory import StrategyMemory
from .irreducibility import IrreducibilityCertificate, IrreducibilityEngine
from .fallback_ladder import FallbackLevel, FallbackLadder
from .independent_verifier import IndependentVerifier
from .work_ledger import WorkLedgerEntry, WorkLedger
from .suite_15 import BenchmarkSuite15
from .engine import HyperMVCDAREngine

__version__ = "1.0.0-mvc-dar"
__all__ = [
    "DataType",
    "OpType",
    "TensorDescriptor",
    "OpNode",
    "ComputationGraph",
    "ContractClass",
    "ExecutionTrack",
    "ExecutionContract",
    "InformationSufficiencyEngine",
    "NecessityStatus",
    "NecessityProofEngine",
    "RedundancyEngine",
    "DeadWorkEliminator",
    "ExactTransformationEngine",
    "ComplexityReplacementEngine",
    "SparsityEngine",
    "LowRankEngine",
    "RepresentationType",
    "RepresentationDiscoveryEngine",
    "PrecisionEngine",
    "MemoryEngine",
    "HeterogeneousFabric",
    "HardwareProfiler",
    "PredictVerifyAcceptEngine",
    "AdaptiveComputeEngine",
    "ErrorBudgetTracker",
    "StrategyGenome",
    "StrategySearchEngine",
    "StrategyMemory",
    "IrreducibilityCertificate",
    "IrreducibilityEngine",
    "FallbackLevel",
    "FallbackLadder",
    "IndependentVerifier",
    "WorkLedgerEntry",
    "WorkLedger",
    "BenchmarkSuite15",
    "HyperMVCDAREngine",
]
