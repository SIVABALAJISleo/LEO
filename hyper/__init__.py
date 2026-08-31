"""
LEO / HYPER Universal Computation Elimination Package
=====================================================
The unified software-only contract-driven computation elimination framework.
"""

from .contracts import UniversalContract, ContractClass, VerificationStatus, ParityTier, UniversalContractEngine
from .workload import OpNode, ComputationGraph, WorkloadAnalyzer
from .dependency import DependencyAnalyzer
from .information import InformationRequirementAnalyzer
from .elimination import ComputationEliminationEngine
from .reuse import MemoizationEngine
from .cache import ContractAwareCache
from .sparsity import SparsityEngine
from .low_rank import LowRankEngine
from .compression import CompressionEngine
from .precision import PrecisionEngine
from .prediction import PredictionEngine
from .reconstruction import ReconstructionEngine
from .temporal import TemporalComputationEngine
from .spatial import SpatialComputationEngine
from .algorithms import AlgorithmicReformulationEngine
from .compiler import KernelFusionEngine
from .kernels import AVX2TilingKernel
from .scheduler import HeterogeneousScheduler
from .cpu import CpuAffinityGovernor
from .igpu import OpenVINOBridge
from .verification import VerificationEngine
from .fallback import AdaptiveFallbackEngine
from .profiling import ThermalProfiler
from .telemetry import ProvenanceLedger
from .research import ResearchDatabase
from .adversarial import AdversarialFalsificationSuite
from .reporting import ScientificReportGenerator
from .benchmark import MasterWorkloadSuite, run_master_benchmarks

__version__ = "10.0.0"
