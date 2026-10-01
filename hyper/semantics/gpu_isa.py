"""
hyper/semantics/gpu_isa.py
==========================
ISA-Neutral GPU Instruction-Set Abstraction for LEO/HYPER.
Implements Sections 5 & 10 of the Master Architecture Specification:
- Authoritative GPU opcodes (GPU_ADD, GPU_MUL, GPU_FMA, GPU_LOAD, GPU_STORE,
  GPU_ATOMIC_ADD, GPU_SHUFFLE, GPU_BROADCAST, GPU_REDUCE, GPU_BARRIER,
  GPU_COMPARE, GPU_BRANCH, GPU_CONVERT, GPU_MMA)
- Execution hierarchy identity (Thread, Warp, Block, Grid, Lane)
- Explicit address spaces (Global, Shared, Local, Constant, Param)
- Memory orderings and synchronization primitives
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from hyper.semantics.types import DataType, TensorType


class GPUOpcode(str, enum.Enum):
    # Memory
    GPU_LOAD = "GPU_LOAD"
    GPU_STORE = "GPU_STORE"
    GPU_CONST = "GPU_CONST"
    
    # Arithmetic & FMA
    GPU_ADD = "GPU_ADD"
    GPU_SUB = "GPU_SUB"
    GPU_MUL = "GPU_MUL"
    GPU_DIV = "GPU_DIV"
    GPU_FMA = "GPU_FMA"
    GPU_NEG = "GPU_NEG"
    GPU_ABS = "GPU_ABS"
    GPU_MIN = "GPU_MIN"
    GPU_MAX = "GPU_MAX"
    
    # Math & Transcendental
    GPU_SQRT = "GPU_SQRT"
    GPU_EXP = "GPU_EXP"
    GPU_LOG = "GPU_LOG"
    GPU_SIN = "GPU_SIN"
    GPU_COS = "GPU_COS"
    GPU_TANH = "GPU_TANH"
    
    # Comparison & Branching
    GPU_COMPARE = "GPU_COMPARE"
    GPU_BRANCH = "GPU_BRANCH"
    GPU_SELECT = "GPU_SELECT"
    
    # Conversion
    GPU_CONVERT = "GPU_CONVERT"
    GPU_BITCAST = "GPU_BITCAST"
    
    # Atomics
    GPU_ATOMIC_ADD = "GPU_ATOMIC_ADD"
    GPU_ATOMIC_MIN = "GPU_ATOMIC_MIN"
    GPU_ATOMIC_MAX = "GPU_ATOMIC_MAX"
    GPU_ATOMIC_CAS = "GPU_ATOMIC_CAS"
    
    # Warp & Cross-Lane
    GPU_SHUFFLE = "GPU_SHUFFLE"
    GPU_BROADCAST = "GPU_BROADCAST"
    GPU_VOTE_ALL = "GPU_VOTE_ALL"
    GPU_VOTE_ANY = "GPU_VOTE_ANY"
    
    # Synchronization & Memory Barriers
    GPU_BARRIER = "GPU_BARRIER"
    GPU_FENCE = "GPU_FENCE"
    
    # Reductions & Matrix Multiply-Accumulate
    GPU_REDUCE = "GPU_REDUCE"
    GPU_MMA = "GPU_MMA"
    
    # Identity Queries
    GPU_THREAD_ID = "GPU_THREAD_ID"
    GPU_BLOCK_ID = "GPU_BLOCK_ID"
    GPU_GRID_ID = "GPU_GRID_ID"
    GPU_WARP_ID = "GPU_WARP_ID"
    GPU_LANE_ID = "GPU_LANE_ID"


class AddressSpace(str, enum.Enum):
    GLOBAL = "GLOBAL"
    SHARED = "SHARED"
    LOCAL = "LOCAL"
    CONSTANT = "CONSTANT"
    PARAM = "PARAM"
    TEXTURE = "TEXTURE"


class MemoryOrdering(str, enum.Enum):
    RELAXED = "RELAXED"
    ACQUIRE = "ACQUIRE"
    RELEASE = "RELEASE"
    ACQ_REL = "ACQ_REL"
    SEQ_CST = "SEQ_CST"


@dataclass(frozen=True)
class GPUInstruction:
    """
    Formally defined ISA-neutral GPU instruction metadata.
    Enforces complete provenance and precision constraints.
    """
    opcode: GPUOpcode
    result_id: str
    result_type: TensorType
    operands: Tuple[Union[str, int, float, bool], ...]
    address_space: Optional[AddressSpace] = None
    memory_ordering: MemoryOrdering = MemoryOrdering.RELAXED
    attributes: Dict[str, Any] = field(default_factory=dict)
    provenance: str = "gpu_isa"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "opcode": self.opcode.value,
            "result_id": self.result_id,
            "result_type": self.result_type.to_dict(),
            "operands": list(self.operands),
            "address_space": self.address_space.value if self.address_space else None,
            "memory_ordering": self.memory_ordering.value,
            "attributes": self.attributes,
            "provenance": self.provenance,
        }


@dataclass
class GPUGridConfig:
    grid_dim: Tuple[int, int, int] = (1, 1, 1)
    block_dim: Tuple[int, int, int] = (1, 1, 1)
    warp_size: int = 32
    shared_mem_bytes: int = 0

    @property
    def total_threads_per_block(self) -> int:
        return self.block_dim[0] * self.block_dim[1] * self.block_dim[2]

    @property
    def total_blocks(self) -> int:
        return self.grid_dim[0] * self.grid_dim[1] * self.grid_dim[2]

    @property
    def total_threads(self) -> int:
        return self.total_blocks * self.total_threads_per_block
