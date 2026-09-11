"""
hyper_cco
=========
Contract-Constrained Computation Optimizer (HYPER-CCO).
An open-ended, scientific compute elimination, representation transformation,
and heterogeneous scheduling system for Intel Core i5 + Intel UHD graphics.

Core philosophy:
DO NOT ASK: "How do I make the weak hardware perform the GPU's work faster?"
ASK: "What part of the GPU's work does the application actually need?"
"""

from .contract import (
    ComputeContract,
    ExactnessClass,
    CorrectnessTaxonomy,
    EvidenceClass,
    VerificationLevel,
    VerificationStatus,
    ContractViolationError
)
from .proof_elimination import (
    ProofCarryingEliminationEngine,
    RegionEliminationCertificate,
    ProofBundle,
    EliminationMode
)
from .counterfactual import (
    CounterfactualSkipEngine,
    CounterfactualDecision,
    LipschitzEstimator
)
from .residual_engine import (
    ResidualEngine,
    ResidualResult,
    ResidualMode,
    ResidualTelemetry
)
from .contract_compiler import (
    ContractCompiler,
    CompiledPlan,
    ExecutionStrategy,
    TargetHardware
)
from .semantic_compression import (
    SemanticCompressionEngine,
    SemanticTier,
    SemanticAllocation,
    CompressionMetrics
)
from .thermal_scheduler import (
    ThermalDeadlineScheduler,
    ScheduledTarget,
    HardwareTelemetry,
    CostWeights,
    SchedulingOutcome
)
from .provenance_ledger import (
    ProvenanceLedger,
    BenchmarkProvenanceRecord,
    TruthfulnessLabel
)
from .adversarial_fuzzer import (
    AdversarialContractFuzzer,
    FailureMode,
    FuzzAttackResult
)
from .cheapest_valid_path import (
    AdaptiveCheapestValidPathEngine,
    EngineExecutionReport
)
from .exact_cache import (
    ExactFullContentCache,
    CacheMode,
    CacheLookupResult,
    CacheEntry
)
from .incremental_engine import (
    IncrementalEngine,
    DeltaType,
    DeltaAnalysis,
    IncrementalResult
)
from .residual_engine import (
    ResidualEngine,
    ResidualResult
)
from .cse_engine import (
    CommonSubexpressionEngine,
    DagNode
)
from .algebraic_engine import (
    AlgebraicReformulationEngine,
    AlgebraicTransformationRecord
)
from .low_rank_engine import (
    LowRankEngine,
    LowRankMethod,
    LowRankResult
)
from .sparsity_engine import (
    SparsityEngine,
    SparsityPattern,
    SparsityAnalysis,
    SparsityResult
)
from .precision_engine import (
    PrecisionEngine,
    PrecisionFormat,
    PrecisionResult
)
from .prediction_speculation import (
    SpeculativeEngine,
    SpeculativeResult
)
from .temporal_graphics import (
    TemporalGraphicsEngine,
    TemporalGraphicsResult
)
from .scheduler import (
    HeterogeneousScheduler,
    DeviceTarget,
    WorkloadSuitability,
    ScheduleDecision,
    KernelExecutionRecord
)
from .optimizer import (
    HyperCcoOptimizer,
    OptimizationPlan,
    CcoExecutionResult
)
from .certificate import (
    ExecutionCertificate,
    CertificateLedger,
    VerificationRecord,
    MeasurementRecord
)
from .verifier import (
    CcoVerifier
)
from .scorecard import (
    DecoupledParityScorecard,
    DimensionScore,
    ScorecardBuilder,
    FeasibleWorkloadRecord,
    ExcludedWorkloadRecord,
    ParityBoundaryCertificate,
    FeasibleSetParityCalculator,
)
from .runtime_tracer import (
    RuntimeDecisionRecord,
    RuntimeDecisionTracer,
    compute_data_hash,
)

__all__ = [
    "ComputeContract",
    "ExactnessClass",
    "EvidenceClass",
    "VerificationLevel",
    "VerificationStatus",
    "ContractViolationError",
    "ExactFullContentCache",
    "CacheMode",
    "CacheLookupResult",
    "CacheEntry",
    "IncrementalEngine",
    "DeltaType",
    "DeltaAnalysis",
    "IncrementalResult",
    "ResidualEngine",
    "ResidualResult",
    "CommonSubexpressionEngine",
    "DagNode",
    "AlgebraicReformulationEngine",
    "AlgebraicTransformationRecord",
    "LowRankEngine",
    "LowRankMethod",
    "LowRankResult",
    "SparsityEngine",
    "SparsityPattern",
    "SparsityAnalysis",
    "SparsityResult",
    "PrecisionEngine",
    "PrecisionFormat",
    "PrecisionResult",
    "SpeculativeEngine",
    "SpeculativeResult",
    "TemporalGraphicsEngine",
    "TemporalGraphicsResult",
    "HeterogeneousScheduler",
    "DeviceTarget",
    "WorkloadSuitability",
    "ScheduleDecision",
    "KernelExecutionRecord",
    "HyperCcoOptimizer",
    "OptimizationPlan",
    "CcoExecutionResult",
    "ExecutionCertificate",
    "CertificateLedger",
    "VerificationRecord",
    "MeasurementRecord",
    "CcoVerifier",
    "DecoupledParityScorecard",
    "DimensionScore",
    "ScorecardBuilder",
    "FeasibleWorkloadRecord",
    "ExcludedWorkloadRecord",
    "ParityBoundaryCertificate",
    "FeasibleSetParityCalculator",
    "RuntimeDecisionRecord",
    "RuntimeDecisionTracer",
    "compute_data_hash",
    "CorrectnessTaxonomy",
    "ProofCarryingEliminationEngine",
    "RegionEliminationCertificate",
    "ProofBundle",
    "EliminationMode",
    "CounterfactualSkipEngine",
    "CounterfactualDecision",
    "LipschitzEstimator",
    "ResidualMode",
    "ResidualTelemetry",
    "ContractCompiler",
    "CompiledPlan",
    "ExecutionStrategy",
    "TargetHardware",
    "SemanticCompressionEngine",
    "SemanticTier",
    "SemanticAllocation",
    "CompressionMetrics",
    "ThermalDeadlineScheduler",
    "ScheduledTarget",
    "HardwareTelemetry",
    "CostWeights",
    "SchedulingOutcome",
    "ProvenanceLedger",
    "BenchmarkProvenanceRecord",
    "TruthfulnessLabel",
    "AdversarialContractFuzzer",
    "FailureMode",
    "FuzzAttackResult",
    "AdaptiveCheapestValidPathEngine",
    "EngineExecutionReport",
]
