"""
Search Space Compiler Types: Defines structured multi-dimensional search spaces.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from hyper_universal.contract_ir import ContractIR
from hyper_universal.workload import UniversalWorkload

@dataclass
class MathematicalOption:
    name: str
    identity: str
    applicability_condition: str
    complexity_order: str

@dataclass
class AlgorithmOption:
    name: str
    paradigm: str  # divide-and-conquer, dynamic-programming, greedy, etc.
    complexity: str
    stability: str

@dataclass
class RepresentationOption:
    name: str
    data_structure: str  # dense, sparse_csr, tiled, low_rank_svd, frequency_fft
    memory_footprint: str
    conversion_cost: str

@dataclass
class ProgramOption:
    name: str
    ast_transformation: str  # loop_unroll, loop_interchange, branch_elim, kernel_fuse
    vectorization: bool

@dataclass
class CompilerOption:
    name: str
    flags: List[str]
    inlining_strategy: str

@dataclass
class ScheduleOption:
    tile_size_l1: int
    tile_size_l2: int
    thread_count: int
    pipeline_depth: int

@dataclass
class MemoryLayoutOption:
    layout: str  # row_major, col_major, blocked, packed_4bit
    alignment_bytes: int

@dataclass
class PrecisionOption:
    precision: str  # FP32, FP16, BF16, INT8, TERNARY_1_58
    quantization_scheme: Optional[str] = None

@dataclass
class ExecutionOption:
    target: str  # CPU, IGPU, HYBRID_ASYNC
    offload_threshold_ops: int

@dataclass
class CompiledSearchSpace:
    """The fully compiled multidimensional search space for a workload."""
    workload_id: str
    mathematical_space: List[MathematicalOption] = field(default_factory=list)
    algorithm_space: List[AlgorithmOption] = field(default_factory=list)
    representation_space: List[RepresentationOption] = field(default_factory=list)
    program_space: List[ProgramOption] = field(default_factory=list)
    compiler_space: List[CompilerOption] = field(default_factory=list)
    schedule_space: List[ScheduleOption] = field(default_factory=list)
    memory_layout_space: List[MemoryLayoutOption] = field(default_factory=list)
    precision_space: List[PrecisionOption] = field(default_factory=list)
    execution_space: List[ExecutionOption] = field(default_factory=list)

    def total_discrete_configurations(self) -> int:
        """Compute the combinatorial product of non-empty search space dimensions."""
        dims = [
            len(self.mathematical_space),
            len(self.algorithm_space),
            len(self.representation_space),
            len(self.program_space),
            len(self.compiler_space),
            len(self.schedule_space),
            len(self.memory_layout_space),
            len(self.precision_space),
            len(self.execution_space),
        ]
        prod = 1
        for d in dims:
            if d > 0:
                prod *= d
        return prod
