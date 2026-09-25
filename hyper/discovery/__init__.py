"""
hyper.discovery
===============
Unified Verified Computational Pathway Discovery Engine.
"""

from hyper.discovery.cir import (
    CIRGraph,
    CIRNode,
    CIREdge,
    CIRTensorMeta,
    DataType,
    OpType,
    EdgeType,
)
from hyper.discovery.contract import (
    WorkloadContract,
    VerificationMode,
    ContractAuditResult,
    InputDomainSpec,
)
from hyper.discovery.search_space import (
    CandidatePathway,
    SearchSpaceCompiler,
    TransformRule,
)
from hyper.discovery.counterfactual import (
    CounterfactualEngine,
    CounterfactualAnalysisResult,
)
from hyper.discovery.verifier import (
    IndependentReferenceBackend,
    DoubleExecutionVerifier,
    VerificationRecord,
)
from hyper.discovery.search import (
    SearchEngine,
    SearchConfig,
    SearchResult,
    SearchStrategy,
    SearchTraceEntry,
)
from hyper.discovery.anticheat import (
    AntiCheatGate,
    AntiCheatViolation,
)
from hyper.discovery.adversarial import (
    AdversarialWorkloadGenerator,
    AdversarialWorkload,
    WorkloadCategory,
    AdversarialType,
)
from hyper.discovery.cost_model import (
    CostModel,
    PredictedCost,
    MeasuredCost,
)
from hyper.discovery.scheduler import (
    ResourceAwareScheduler,
    DeviceTarget,
    ExecutionSchedule,
    SchedulingDecision,
)
from hyper.discovery.proof import (
    ProofGenerator,
    ProofRecord,
    PathwayExplainer,
    HumanReadableExplanation,
)
from hyper.discovery.benchmarking import (
    BenchmarkRunner,
    BenchmarkStats,
    ReproducibilityManifest,
    NvidiaComparisonReport,
    UniversalityScorecard,
)
from hyper.discovery.engine import (
    VerifiedPathwayEngine,
    EngineExecutionReport,
)

__all__ = [
    "CIRGraph",
    "CIRNode",
    "CIREdge",
    "CIRTensorMeta",
    "DataType",
    "OpType",
    "EdgeType",
    "WorkloadContract",
    "VerificationMode",
    "ContractAuditResult",
    "InputDomainSpec",
    "CandidatePathway",
    "SearchSpaceCompiler",
    "TransformRule",
    "CounterfactualEngine",
    "CounterfactualAnalysisResult",
    "IndependentReferenceBackend",
    "DoubleExecutionVerifier",
    "VerificationRecord",
    "SearchEngine",
    "SearchConfig",
    "SearchResult",
    "SearchStrategy",
    "SearchTraceEntry",
    "AntiCheatGate",
    "AntiCheatViolation",
    "AdversarialWorkloadGenerator",
    "AdversarialWorkload",
    "WorkloadCategory",
    "AdversarialType",
    "CostModel",
    "PredictedCost",
    "MeasuredCost",
    "ResourceAwareScheduler",
    "DeviceTarget",
    "ExecutionSchedule",
    "SchedulingDecision",
    "ProofGenerator",
    "ProofRecord",
    "PathwayExplainer",
    "HumanReadableExplanation",
    "BenchmarkRunner",
    "BenchmarkStats",
    "ReproducibilityManifest",
    "NvidiaComparisonReport",
    "UniversalityScorecard",
    "VerifiedPathwayEngine",
    "EngineExecutionReport",
]
