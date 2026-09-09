"""
hyper_x/wormhole_compiler/schemas.py
=============================================================================
HYPER-X Wormhole Compiler: Core Schemas and Data Models
=============================================================================
Defines unified, versioned, immutable schemas for:
- Contracts, Observables, and Dependency Graphs
- Counterfactual Hypotheses and Representation Spaces
- Algorithm Grammar Expressions and Discovery Candidates
- Cost Vectors, Proof Records, and Falsification Reports
- Multi-Metric Parity Scores and Telemetry Data
"""

from __future__ import annotations
import enum
import time
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple, Callable, Set, Union
import numpy as np


class CorrectnessRequirement(str, enum.Enum):
    EXACT = "EXACT"
    NUMERICAL_TOLERANCE = "NUMERICAL_TOLERANCE"
    PERCEPTUAL = "PERCEPTUAL"
    STATISTICAL = "STATISTICAL"
    TOP_K = "TOP_K"
    CONTRACT_CONSTRAINED = "CONTRACT_CONSTRAINED"


class CachePolicy(str, enum.Enum):
    COLD = "COLD"
    WARM = "WARM"
    STREAMING = "STREAMING"
    FORBIDDEN = "FORBIDDEN"


class ExecutionTrack(str, enum.Enum):
    EXACT = "EXACT"
    NUMERICALLY_APPROXIMATE = "NUMERICALLY_APPROXIMATE"
    APPLICATION_CONTRACT = "APPLICATION_CONTRACT"


class NecessityClass(str, enum.Enum):
    INDISPENSABLE = "INDISPENSABLE"
    CONDITIONALLY_REQUIRED = "CONDITIONALLY_REQUIRED"
    REDUNDANT = "REDUNDANT"
    REUSABLE = "REUSABLE"
    PREDICTABLE = "PREDICTABLE"
    APPROXIMABLE = "APPROXIMABLE"
    COMPRESSIBLE = "COMPRESSIBLE"
    REORDERABLE = "REORDERABLE"
    REPLACEABLE = "REPLACEABLE"
    UNOBSERVED = "UNOBSERVED"


class MutationType(str, enum.Enum):
    REMOVE = "REMOVE"
    PARTIAL_EXECUTE = "PARTIAL_EXECUTE"
    PREDICT = "PREDICT"
    REUSE = "REUSE"
    REPRESENTATION_CHANGE = "REPRESENTATION_CHANGE"
    REORDER = "REORDER"
    FACTORIZE = "FACTORIZE"
    COMPRESS = "COMPRESS"
    OUTPUT_PROJECT = "OUTPUT_PROJECT"
    EVENT_TRIGGER = "EVENT_TRIGGER"
    CORRECTION_TERM = "CORRECTION_TERM"
    LOWER_PRECISION_CORRECT = "LOWER_PRECISION_CORRECT"
    SUFFICIENT_STATISTIC = "SUFFICIENT_STATISTIC"
    RECONSTRUCT = "RECONSTRUCT"
    HIDDEN_STRUCTURE = "HIDDEN_STRUCTURE"
    RECURSE = "RECURSE"
    DOMAIN_TRANSFORM = "DOMAIN_TRANSFORM"
    DELTA_COMPUTE = "DELTA_COMPUTE"
    DECOMPOSE_REGIONS = "DECOMPOSE_REGIONS"
    ELIMINATE_COMMUNICATION = "ELIMINATE_COMMUNICATION"
    ELIMINATE_MEMORY_MOVEMENT = "ELIMINATE_MEMORY_MOVEMENT"
    COMPUTE_FOR_MEMORY = "COMPUTE_FOR_MEMORY"
    MEMORY_FOR_COMPUTE = "MEMORY_FOR_COMPUTE"
    LEARNED_PREDICT_VERIFY = "LEARNED_PREDICT_VERIFY"


class RepresentationType(str, enum.Enum):
    DENSE = "DENSE"
    SPARSE = "SPARSE"
    SPARSE_CSR = "SPARSE_CSR"
    BLOCK_SPARSE = "BLOCK_SPARSE"
    LOW_RANK = "LOW_RANK"
    FACTORED = "FACTORED"
    TENSOR_TRAIN = "TENSOR_TRAIN"
    QUANTIZED = "QUANTIZED"
    BINARY = "BINARY"
    TERNARY = "TERNARY"
    COMPRESSED = "COMPRESSED"
    DELTA_ENCODED = "DELTA_ENCODED"
    EVENT_DRIVEN = "EVENT_DRIVEN"
    HIERARCHICAL = "HIERARCHICAL"
    TILED = "TILED"
    MORTON_Z = "MORTON_Z"
    FREQUENCY_DOMAIN = "FREQUENCY_DOMAIN"
    WAVELET_DOMAIN = "WAVELET_DOMAIN"
    POLYNOMIAL = "POLYNOMIAL"
    LOOKUP_TABLE = "LOOKUP_TABLE"
    INTERPOLATION = "INTERPOLATION"
    SKETCH = "SKETCH"
    RANDOM_PROJECTION = "RANDOM_PROJECTION"
    SUFFICIENT_STATISTIC = "SUFFICIENT_STATISTIC"
    GRAPH_REPRESENTATION = "GRAPH_REPRESENTATION"
    SYMBOLIC_REPRESENTATION = "SYMBOLIC_REPRESENTATION"
    FACTORED_REPRESENTATION = "FACTORED_REPRESENTATION"
    RECURSIVE_REPRESENTATION = "RECURSIVE_REPRESENTATION"
    STREAMING_REPRESENTATION = "STREAMING_REPRESENTATION"


class GrammarOperator(str, enum.Enum):
    DENSE = "DENSE"
    SPARSE = "SPARSE"
    LOW_RANK = "LOW_RANK"
    BLOCK = "BLOCK"
    TILE = "TILE"
    REORDER = "REORDER"
    FACTOR = "FACTOR"
    DELTA = "DELTA"
    CACHE = "CACHE"
    PREDICT = "PREDICT"
    APPROXIMATE = "APPROXIMATE"
    QUANTIZE = "QUANTIZE"
    SKETCH = "SKETCH"
    FFT = "FFT"
    WAVELET = "WAVELET"
    MULTIGRID = "MULTIGRID"
    RECURSE = "RECURSE"
    EVENT_DRIVEN = "EVENT_DRIVEN"
    CONDITIONAL = "CONDITIONAL"
    STREAM = "STREAM"
    COMPRESS = "COMPRESS"
    DECOMPRESS = "DECOMPRESS"
    REUSE = "REUSE"
    SPECULATE = "SPECULATE"
    CORRECT = "CORRECT"
    FUSE = "FUSE"
    SPLIT = "SPLIT"
    PIPELINE = "PIPELINE"
    COMMUNICATION_AVOID = "COMMUNICATION_AVOID"
    MEMORY_AVOID = "MEMORY_AVOID"
    OUTPUT_PROJECT = "OUTPUT_PROJECT"
    SUFFICIENT_STATISTIC = "SUFFICIENT_STATISTIC"


class ProofClass(str, enum.Enum):
    DETERMINISTIC_EXACT = "DETERMINISTIC_EXACT"
    FORMAL_REWRITE = "FORMAL_REWRITE"
    SYMBOLIC = "SYMBOLIC"
    ALGEBRAIC = "ALGEBRAIC"
    RANDOMIZED_PROBABILISTIC = "RANDOMIZED_PROBABILISTIC"
    NUMERICAL = "NUMERICAL"
    EMPIRICAL = "EMPIRICAL"


class FailureCategory(str, enum.Enum):
    CORRECTNESS = "CORRECTNESS"
    NUMERICAL = "NUMERICAL"
    PERFORMANCE = "PERFORMANCE"
    MEMORY = "MEMORY"
    TRANSFER = "TRANSFER"
    QUALITY = "QUALITY"
    CONTRACT = "CONTRACT"
    HARDWARE = "HARDWARE"
    REPRODUCIBILITY = "REPRODUCIBILITY"
    VERIFICATION = "VERIFICATION"
    HOLDOUT = "HOLDOUT"


class PowerTelemetryType(str, enum.Enum):
    MEASURED_POWER = "MEASURED_POWER"
    ESTIMATED_POWER = "ESTIMATED_POWER"
    POWER_NOT_MEASURED = "POWER_NOT_MEASURED"


@dataclass
class WorkloadContract:
    workload_id: str
    operation: str
    input_shape: Tuple[int, ...]
    output_shape: Tuple[int, ...]
    dtype: str = "float32"
    correctness: CorrectnessRequirement = CorrectnessRequirement.NUMERICAL_TOLERANCE
    tolerance: float = 1e-4
    latency_slo_ms: float = 100.0
    throughput_slo: float = 0.0
    memory_limit_mb: float = 4096.0
    power_limit_watts: Optional[float] = None
    quality_requirement: float = 1.0
    determinism: bool = True
    reproducibility: bool = True
    acceptable_approximations: List[str] = field(default_factory=list)
    forbidden_approximations: List[str] = field(default_factory=list)
    cache_policy: CachePolicy = CachePolicy.COLD
    execution_track: ExecutionTrack = ExecutionTrack.APPLICATION_CONTRACT
    hardware_constraints: Dict[str, Any] = field(default_factory=dict)
    external_dependencies: List[str] = field(default_factory=list)

    @property
    def min_ssim(self) -> float:
        return self.quality_requirement

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["correctness"] = self.correctness.value
        d["cache_policy"] = self.cache_policy.value
        d["execution_track"] = self.execution_track.value
        return d

    def compute_contract_hash(self) -> str:
        s = f"{self.workload_id}|{self.operation}|{self.input_shape}|{self.output_shape}|{self.tolerance}|{self.latency_slo_ms}|{self.cache_policy.value}"
        return hashlib.sha256(s.encode()).hexdigest()[:16]


@dataclass
class ObservableRequirement:
    observable_id: str
    description: str
    output_type: str                  # "FULL_MATRIX", "VECTOR", "TOP_K", "COORDINATES", "THRESHOLD_BOOLEAN", "STATISTIC", "PIXELS"
    dimension_reduction_ratio: float  # e.g., 0.001 if only top-k or scalar output required
    extractor_fn_name: str
    tolerance: float = 1e-4
    is_decision_relevant_only: bool = False
    is_user_visible_only: bool = False


@dataclass
class DependencyNode:
    node_id: str
    operation: str
    estimated_cost: float
    memory_cost: int
    dependencies: List[str]
    output_shape: Tuple[int, ...]
    precision: str
    reuse_probability: float
    observability: float              # [0.0, 1.0]
    necessity: NecessityClass = NecessityClass.INDISPENSABLE
    approximation_sensitivity: float = 1.0
    is_observable_target: bool = False

    @property
    def necessity_class(self) -> NecessityClass:
        return self.necessity


@dataclass
class CounterfactualHypothesis:
    hypothesis_id: str
    target_node_id: str
    mutation: MutationType
    question: str
    proposed_transformation: str
    expected_work_reduction: float    # [0.0, 1.0]
    expected_memory_reduction: float  # [0.0, 1.0]
    applicable_conditions: List[str] = field(default_factory=list)
    estimated_risk: float = 0.5


@dataclass
class RepresentationSpec:
    representation_type: RepresentationType
    transformation_cost_flops: float
    inverse_cost_flops: float
    approximation_error: float
    exactness_conditions: List[str]
    memory_bytes: int
    applicability_conditions: List[str]
    expected_benefit: str
    verification_strategy: str


@dataclass
class GrammarExpression:
    expression_id: str
    operators: List[GrammarOperator]
    parameters: Dict[str, Any] = field(default_factory=dict)
    canonical_repr: str = ""

    def __post_init__(self):
        if not self.canonical_repr:
            self.canonical_repr = " + ".join(op.value for op in self.operators)


@dataclass
class CostVector:
    arithmetic_cost: float = 0.0
    memory_traffic_bytes: float = 0.0
    cache_miss_estimate: float = 0.0
    synchronization_overhead: float = 0.0
    branch_divergence_cost: float = 0.0
    vectorization_efficiency: float = 1.0
    cpu_utilization: float = 0.0
    igpu_utilization: float = 0.0
    transfer_overhead_ms: float = 0.0
    kernel_launch_overhead_ms: float = 0.0
    communication_cost: float = 0.0
    preprocessing_overhead_ms: float = 0.0
    postprocessing_overhead_ms: float = 0.0
    verification_overhead_ms: float = 0.0
    correction_overhead_ms: float = 0.0
    total_latency_ms: float = 0.0
    estimated_energy_joules: float = 0.0

    def compute_weighted_scalar(
        self,
        wc: float = 1.0,
        wm: float = 0.5,
        wl: float = 2.0,
        we: float = 0.1,
        wq: float = 5.0,
        wr: float = 0.5,
        wx: float = 1.0,
        quality_penalty: float = 0.0
    ) -> float:
        return (
            wc * (self.arithmetic_cost / 1e9) +
            wm * (self.memory_traffic_bytes / 1e9) +
            wl * (self.total_latency_ms) +
            we * (self.estimated_energy_joules) +
            wq * (quality_penalty) +
            wr * (self.verification_overhead_ms) +
            wx * (self.communication_cost)
        )


@dataclass
class ProofRecord:
    proof_id: str
    candidate_id: str
    proof_type: ProofClass
    verified: bool
    quality_score: float
    numerical_error: float
    tolerance_applied: float
    seed: Optional[int]
    input_hash: str
    reference_hash: str
    candidate_hash: str
    verification_time_ms: float
    verification_backend: str
    proof_details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CandidateAlgorithmRecord:
    candidate_id: str
    parent_ids: List[str]
    grammar_expression: str
    representation: str
    target_operation: str
    contract_hash: str
    correctness_class: str
    numerical_error: float
    latency_ms: float
    throughput: float
    memory_mb: float
    work_elimination_ratio: float
    wormhole_score: float
    gpu_advantage_erased_pct: float
    verification_status: bool
    falsification_status: bool
    holdout_status: bool
    hardware_fingerprint_hash: str
    compiler_version: str = "1.0.0"
    source_hash: str = ""
    is_novel_composition: bool = False
    timestamp: float = field(default_factory=time.time)
