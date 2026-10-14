"""
hyper/six_engines/__init__.py
=============================
HYPER-GODMODE Ω∞ Six-Engine Universal Optimization System.

Exports:
- Engine 1: IntelligentMemoryEngine, MmapArrayStreamer, OutOfCoreChunkedExecutor, TinyStoriesStreamingModel
- Engine 2: ComputationEliminationEngine, AlgebraicReformulator, IncrementalComputeEngine
- Engine 3: DataReuseAndLocalityEngine, CacheAwareTiledMatmul, FusedKernelEngine, TemporalCoherenceEngine
- Engine 4: AdaptiveHeterogeneousScheduler, BackendDevice, HardwareCapabilityDetector
- Engine 5: PathwayDiscoveryEngine, WorkloadBottleneckClassifier, BottleneckKind
- Engine 6: ExactDifferentialVerifier, RigorousBenchmarkRunner, FallbackRouter
- Models: WorkloadContract, OptimizationCandidate, BenchmarkRecord, PathwayStatus, ParityScorecard
- Unified: SixEngineUniversalOptimizer, PipelineExecutionResult
"""

from .models import (
    BenchmarkRecord,
    CorrectnessMode,
    OptimizationCandidate,
    ParityScorecard,
    PathwayStatus,
    TransformationClass,
    WorkloadContract,
)
from .engine1_memory_streaming import (
    AsynchronousPrefetchBuffer,
    BoundedBufferPool,
    CostAwareLRUCache,
    IntelligentMemoryEngine,
    MemoryBudgetEnforcer,
    MmapArrayStreamer,
    OutOfCoreChunkedExecutor,
    QuantizedStorageCodec,
    StreamingMetrics,
    TinyStoriesStreamingModel,
    WorkloadMemoryEstimator,
)
from .engine2_computation_elimination import (
    AlgebraicReformulator,
    ComputationEliminationEngine,
    DependencyGraph,
    DependencyNode,
    IncrementalComputeEngine,
    TransformationEvidence,
)
from .engine3_data_reuse_locality import (
    BlockTiledFlashAttentionEngine,
    CacheAwareTiledMatmul,
    CacheHierarchyProfile,
    DataReuseAndLocalityEngine,
    FusedKernelEngine,
    LocalityMetrics,
    StencilPingPongEngine,
    TemporalCoherenceEngine,
)
from .engine4_adaptive_scheduler import (
    AdaptiveHeterogeneousScheduler,
    BackendDevice,
    HardwareCapabilityDetector,
    SchedulerExecutionRecord,
)
from .engine5_pathway_discovery import (
    BottleneckKind,
    PathwayDiscoveryEngine,
    WorkloadBottleneckClassifier,
)
from .engine6_verification_benchmark import (
    ExactDifferentialVerifier,
    FallbackRouter,
    RigorousBenchmarkRunner,
    VerificationReport,
)
from .unified_pipeline import (
    PipelineExecutionResult,
    SixEngineUniversalOptimizer,
)

__all__ = [
    "BenchmarkRecord",
    "CorrectnessMode",
    "OptimizationCandidate",
    "ParityScorecard",
    "PathwayStatus",
    "TransformationClass",
    "WorkloadContract",
    "AsynchronousPrefetchBuffer",
    "BoundedBufferPool",
    "CostAwareLRUCache",
    "IntelligentMemoryEngine",
    "MemoryBudgetEnforcer",
    "MmapArrayStreamer",
    "OutOfCoreChunkedExecutor",
    "QuantizedStorageCodec",
    "StreamingMetrics",
    "TinyStoriesStreamingModel",
    "WorkloadMemoryEstimator",
    "AlgebraicReformulator",
    "ComputationEliminationEngine",
    "DependencyGraph",
    "DependencyNode",
    "IncrementalComputeEngine",
    "TransformationEvidence",
    "BlockTiledFlashAttentionEngine",
    "CacheAwareTiledMatmul",
    "CacheHierarchyProfile",
    "DataReuseAndLocalityEngine",
    "FusedKernelEngine",
    "LocalityMetrics",
    "StencilPingPongEngine",
    "TemporalCoherenceEngine",
    "AdaptiveHeterogeneousScheduler",
    "BackendDevice",
    "HardwareCapabilityDetector",
    "SchedulerExecutionRecord",
    "BottleneckKind",
    "PathwayDiscoveryEngine",
    "WorkloadBottleneckClassifier",
    "ExactDifferentialVerifier",
    "FallbackRouter",
    "RigorousBenchmarkRunner",
    "VerificationReport",
    "PipelineExecutionResult",
    "SixEngineUniversalOptimizer",
]
