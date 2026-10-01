"""
LEO / HYPER Universal Computation Elimination Package
=====================================================
The unified software-only contract-driven computation elimination framework.
"""

from .contracts import UniversalContract, ContractClass, VerificationStatus, ParityTier, UniversalContractEngine
from .workload import OpNode, ComputationGraph, WorkloadAnalyzer
from .ir import IROperation, WorkloadIR
from .necessity import NecessityClass, NecessityMap, NecessityAnalyzer
from .information import InformationRequirementAnalyzer
from .dependency import DependencyAnalyzer
from .elimination import ComputationEliminationEngine
from .reuse import MemoizationEngine
from .cache import ContractAwareCache
from .sparsity import SparsityEngine
from .low_rank import LowRankEngine
from .compression import CompressionEngine
from .precision import PrecisionEngine
from .sensitivity import PrecisionTier, SensitivityEngine
from .prediction import PredictionEngine
from .residual import ResidualComputationEngine
from .reconstruction import ReconstructionEngine
from .temporal import TemporalComputationEngine
from .spatial import SpatialComputationEngine
from .hierarchical import HierarchicalComputationEngine
from .algorithms import AlgorithmicReformulationEngine
from .communication import CommunicationMetrics, CommunicationAvoidanceEngine
from .compiler import KernelFusionEngine
from .vectorization import VectorizationEngine
from .kernels import AVX2TilingKernel
from .microtask import MicroTask, MicroTaskScheduler
from .resource import MemoryPool, ResourceManager
from .memory import MemoryEngine
from .thermal import ThermalEngine
from .power import PowerEngine
from .autotuning import AutotuningEngine
from .learning import StrategyEntry, StrategyDatabase
from .search import MetaOptimizer
from .scheduler import HeterogeneousScheduler
from .cpu import CpuAffinityGovernor
from .igpu import OpenVINOBridge
from .verification import VerificationEngine
from .proof import ProofCarryingRecord
from .fallback import AdaptiveFallbackEngine
from .firewall import ExactnessType, ExactnessViolationError, ExactnessFirewall
from .profiling import ThermalProfiler
from .telemetry import ProvenanceLedger
from .ablation import AblationEngine
from .adversarial import AdversarialFalsificationSuite
from .defense import ContaminationDefenseEngine
from .research import ResearchDatabase
from .security import ExecutionWatchdog
from .regression import RegressionDetector
from .reporting import ScientificReportGenerator
from .benchmark import MasterWorkloadSuite, run_master_benchmarks

# Universal Exact Semantic Replacement Engine Canonical Architecture
from .universal_ir import Opcode, UniversalOp, UniversalIRProgram
from .semantics import DataType, TensorType, ExactnessLevel, VerificationVerdict
from .executor import UniversalReferenceExecutor, UniversalExactExecutor
from .verifier import DifferentialVerifier, UniversalTruthGate
from .escape import UniversalSearchBrain, EscapeCandidate
from .router import UniversalRouter, RouterResult, RouterOutcome
from .coverage import CoverageEngine, LiveCoverageMetrics
from .evidence import Evidence, EvidenceStatus, EvidenceLedger
from .certificates import CertificateEngine, HyperCertificate, CertificateStore
from .workloads import CanonicalWorkloadCorpus, CanonicalWorkload
from .backends import CpuBackend, IntelUhdBackend
from .frontends import (
    FrontendRegistry,
    CIRFrontend,
    TensorGraphFrontend,
    CUDALikeFrontend,
    OpenCLFrontend,
    SYCLFrontend,
    SemanticNormalizer,
    UnsupportedSemanticError,
)
from .semantics.aliasing import MemoryAliasAnalyzer, MemoryRegion, AliasVerdict
from .semantics.control_flow import StructuredLoop, StructuredBranch, LoopKind
from .escape.necessary_work import NecessaryWorkGraph, NodeNecessity

__version__ = "10.0.0"

