"""
hyper_mvc_dar/unseen: 10 Novel Software-Only Acceleration Mechanisms for HYPER MVC-DAR.
Target Hardware: Intel Core i5-12450H (4P+4E cores) + Intel UHD Graphics Xe (48EU) laptop.
"""

from .kernel_synth import (
    OpKind,
    FusionStrategy,
    KernelDSLNode,
    KernelCandidate,
    NeuralKernelSynthesizer,
)
from .layout_optimizer import (
    TensorLayout,
    LayoutCostPredictor,
    DifferentiableLayoutOptimizer,
    LayoutProfileResult,
)
from .approx_op import (
    ApproxMode,
    OperatorTelemetry,
    PIErrorController,
    ApproxOp,
)
from .router_moe import (
    ExpertTier,
    SemanticFeatureVector,
    RoutingDecision,
    TinyMoERouter,
    MoEWorkloadGator,
)
from .temporal_gate import (
    FrameType,
    TemporalTelemetry,
    TemporalChangeDetector,
    LearnedResidualPredictor,
    TemporalCoherenceEngine,
)
from .precision_scheduler import (
    DynamicPrecision,
    DPSScheduleResult,
    ContractAwarePrecisionScheduler,
    PRECISION_BITS,
    PRECISION_SPEEDUP,
)
from .schedule_compiler import (
    AutoTiledSchedule,
    HeterogeneousScheduleCompiler,
)
from .speculative_runner import (
    SpeculativeOutcome,
    SpeculativeTelemetry,
    ConfidenceEstimator,
    DynamicSLOThreshold,
    LatencyOptimizedSpeculativeRunner,
)
from .perceptual_validator import (
    PerceptualSubstitutionType,
    PerceptualValidationResult,
    PerceptualMetricCalculator,
    PerceptualEquivalenceEngine,
)
from .program_transformer import (
    TransformationRule,
    MorphingResult,
    WorkloadMorpher,
)
from .benchmark_unseen import (
    UnseenBenchmarkRecord,
    UnseenBenchmarkSuite,
    run_and_save_benchmarks,
)

__all__ = [
    # Feature 1
    "OpKind",
    "FusionStrategy",
    "KernelDSLNode",
    "KernelCandidate",
    "NeuralKernelSynthesizer",
    # Feature 2
    "TensorLayout",
    "LayoutCostPredictor",
    "DifferentiableLayoutOptimizer",
    "LayoutProfileResult",
    # Feature 3
    "ApproxMode",
    "OperatorTelemetry",
    "PIErrorController",
    "ApproxOp",
    # Feature 4
    "ExpertTier",
    "SemanticFeatureVector",
    "RoutingDecision",
    "TinyMoERouter",
    "MoEWorkloadGator",
    # Feature 5
    "FrameType",
    "TemporalTelemetry",
    "TemporalChangeDetector",
    "LearnedResidualPredictor",
    "TemporalCoherenceEngine",
    # Feature 6
    "DynamicPrecision",
    "DPSScheduleResult",
    "ContractAwarePrecisionScheduler",
    "PRECISION_BITS",
    "PRECISION_SPEEDUP",
    # Feature 7
    "AutoTiledSchedule",
    "HeterogeneousScheduleCompiler",
    # Feature 8
    "SpeculativeOutcome",
    "SpeculativeTelemetry",
    "ConfidenceEstimator",
    "DynamicSLOThreshold",
    "LatencyOptimizedSpeculativeRunner",
    # Feature 9
    "PerceptualSubstitutionType",
    "PerceptualValidationResult",
    "PerceptualMetricCalculator",
    "PerceptualEquivalenceEngine",
    # Feature 10
    "TransformationRule",
    "MorphingResult",
    "WorkloadMorpher",
    # Benchmarks
    "UnseenBenchmarkRecord",
    "UnseenBenchmarkSuite",
    "run_and_save_benchmarks",
]
