"""
hyper/universal_ir/opcodes.py
=============================
Authoritative Opcode Definitions for HYPER Universal Computation IR.
Declares all standard opcodes for arithmetic, linear algebra, memory, control flow,
parallelism, synchronization, and atomic operations.
"""

from enum import Enum, auto


class Opcode(str, Enum):
    # Memory and Data Transfer
    CONST = "CONST"
    LOAD = "LOAD"
    STORE = "STORE"
    COPY = "COPY"
    ALLOC = "ALLOC"
    FREE = "FREE"
    MEMORY_ALLOC = "MEMORY_ALLOC"
    MEMORY_FREE = "MEMORY_FREE"

    # Basic Arithmetic
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    FMA = "FMA"
    NEG = "NEG"
    ABS = "ABS"
    MIN = "MIN"
    MAX = "MAX"

    # Math / Transcendental / Powers
    SQRT = "SQRT"
    EXP = "EXP"
    LOG = "LOG"
    SIN = "SIN"
    COS = "COS"
    TAN = "TAN"
    POW = "POW"

    # Activations / Non-linearities
    RELU = "RELU"
    GELU = "GELU"
    SILU = "SILU"
    SIGMOID = "SIGMOID"
    TANH = "TANH"
    SOFTMAX = "SOFTMAX"

    # Comparison and Selection
    CMP = "CMP"
    SELECT = "SELECT"

    # Type Conversion
    CAST = "CAST"
    BITCAST = "BITCAST"

    # Parallel Reductions and Scans
    REDUCE = "REDUCE"
    REDUCE_SUM = "REDUCE_SUM"
    REDUCE_MEAN = "REDUCE_MEAN"
    REDUCE_MAX = "REDUCE_MAX"
    REDUCE_MIN = "REDUCE_MIN"
    REDUCE_NORM = "REDUCE_NORM"
    SCAN = "SCAN"

    # Linear Algebra & Tensor Operations
    MATMUL = "MATMUL"
    BATCH_MATMUL = "BATCH_MATMUL"
    GEMM = "GEMM"
    GEMV = "GEMV"
    TRANSPOSE = "TRANSPOSE"
    PERMUTE = "PERMUTE"
    RESHAPE = "RESHAPE"
    SLICING = "SLICING"
    CONCAT = "CONCAT"
    SPLIT = "SPLIT"

    # Convolutions
    CONV1D = "CONV1D"
    CONV2D = "CONV2D"
    CONV3D = "CONV3D"

    # Signal & Fast Transforms
    FFT = "FFT"
    IFFT = "IFFT"
    FFT2D = "FFT2D"
    IFFT2D = "IFFT2D"

    # Special / Domain / Fused
    ATTENTION = "ATTENTION"
    FUSED_GEMM_ADD = "FUSED_GEMM_ADD"
    FUSED_CONV_RELU = "FUSED_CONV_RELU"
    FUSED_GEMM_RELU = "FUSED_GEMM_RELU"
    HASH_SHA256 = "HASH_SHA256"
    ODE_EULER_STEP = "ODE_EULER_STEP"

    # Indexing and Data Movement
    GATHER = "GATHER"
    SCATTER = "SCATTER"
    SCATTER_ADD = "SCATTER_ADD"

    # Ordering and Selection
    SORT = "SORT"
    TOPK = "TOPK"

    # Atomics
    ATOMIC_ADD = "ATOMIC_ADD"
    ATOMIC_MIN = "ATOMIC_MIN"
    ATOMIC_MAX = "ATOMIC_MAX"
    ATOMIC_CAS = "ATOMIC_CAS"

    # Synchronization
    BARRIER = "BARRIER"
    FENCE = "FENCE"
    SHUFFLE = "SHUFFLE"

    # Control Flow Primitives
    LOOP = "LOOP"
    LOOP_INIT = "LOOP_INIT"
    LOOP_CONDITION = "LOOP_CONDITION"
    LOOP_BODY = "LOOP_BODY"
    LOOP_UPDATE = "LOOP_UPDATE"
    BRANCH = "BRANCH"
    IF = "IF"
    ELSE = "ELSE"
    MERGE = "MERGE"
    PHI = "PHI"

    # Execution Hierarchy Identity
    THREAD_ID = "THREAD_ID"
    BLOCK_ID = "BLOCK_ID"
    GRID_ID = "GRID_ID"

    # Custom & Extension
    CUSTOM = "CUSTOM"
    IDENTITY = "IDENTITY"


class MemorySpace(str, Enum):
    GLOBAL = "GLOBAL"
    SHARED = "SHARED"
    LOCAL = "LOCAL"
    CONSTANT = "CONSTANT"
    HOST = "HOST"
    DEVICE = "DEVICE"


class MemoryLayout(str, Enum):
    ROW_MAJOR = "ROW_MAJOR"
    COL_MAJOR = "COL_MAJOR"
    STRIDED = "STRIDED"
    SPARSE_CSR = "SPARSE_CSR"
    SPARSE_CSC = "SPARSE_CSC"
    SPARSE_COO = "SPARSE_COO"


# Authoritative aliases
UniversalOpcode = Opcode
CIROpcode = Opcode
