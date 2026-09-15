"""
hyper_x/leaf/__init__.py
========================
LEAF Computational Escape Engine Package.

Architecture:
- contract: Formal contract bounds (EXACT, NUMERICAL, BOUNDED, PERCEPTUAL, PREDICTIVE)
- observable: Output observable specifications
- information_boundary: Upstream dependency and work bounding
- symbolic: EFSC (Execution-Free Symbolic Collapse)
- implicit: Mathematical implicit representation and fields
- neural: NIR (Neural Implicit Resolution)
- discovery: Computational escape search, candidate generation, multi-score ranking
- runtime: Heterogeneous CPU + Intel UHD co-processing
- verification: Multi-tier verification (DECP, Numerical, Contract, Adversarial, Holdout)
- telemetry: Nanosecond latency, CCR work accounting, L3 working set, and provenance
"""

from .contract import LeafContract, ContractTier
from .observable import ObservableSpec, ObservableType
from .information_boundary import InformationBoundaryEngine, BoundaryReport

from .symbolic import (
    SymExpr,
    OpType,
    AlgebraicSimplifier,
    ClosedFormSolver,
    ClosedFormResult,
    EquivalenceProver,
)
from .implicit import (
    ImplicitField,
    PolynomialField,
    FourierFeatureField,
    LowRankImplicitMatrix,
    ImplicitEncoder,
    ImplicitDecoder,
    ErrorBoundVerifier,
)
from .neural import (
    NeuralImplicitField,
    NIRTrainer,
    NIRCostReport,
    NIRGeneralizationVerifier,
    NeuralSurrogate,
)
from .discovery import (
    EscapeCandidate,
    BreakthroughLevel,
    CandidateRanker,
    CandidateMultiScore,
    EscapeGenerator,
    EscapeSearchEngine,
)
from .runtime import (
    LeafCPURuntime,
    LeafiGPURuntime,
    LeafHybridRuntime,
    LeafHeterogeneousScheduler,
)
from .verification import (
    DECPVerifier,
    DECPCertificate,
    NumericalVerifier,
    ContractVerifier,
    AntiStructureFalsifier,
    BlindHoldoutEvaluator,
)
from .telemetry import (
    ExecutionTimer,
    ComputationalCompressionLedger,
    MemoryWorkingSetReport,
    ProvenanceClass,
)

__all__ = [
    "LeafContract",
    "ContractTier",
    "ObservableSpec",
    "ObservableType",
    "InformationBoundaryEngine",
    "BoundaryReport",
    "SymExpr",
    "OpType",
    "AlgebraicSimplifier",
    "ClosedFormSolver",
    "ClosedFormResult",
    "EquivalenceProver",
    "ImplicitField",
    "PolynomialField",
    "FourierFeatureField",
    "LowRankImplicitMatrix",
    "ImplicitEncoder",
    "ImplicitDecoder",
    "ErrorBoundVerifier",
    "NeuralImplicitField",
    "NIRTrainer",
    "NIRCostReport",
    "NIRGeneralizationVerifier",
    "NeuralSurrogate",
    "EscapeCandidate",
    "BreakthroughLevel",
    "CandidateRanker",
    "CandidateMultiScore",
    "EscapeGenerator",
    "EscapeSearchEngine",
    "LeafCPURuntime",
    "LeafiGPURuntime",
    "LeafHybridRuntime",
    "LeafHeterogeneousScheduler",
    "DECPVerifier",
    "DECPCertificate",
    "NumericalVerifier",
    "ContractVerifier",
    "AntiStructureFalsifier",
    "BlindHoldoutEvaluator",
    "ExecutionTimer",
    "ComputationalCompressionLedger",
    "MemoryWorkingSetReport",
    "ProvenanceClass",
]
