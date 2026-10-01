"""
hyper/semantics/types.py
========================
Authoritative Type System for HYPER Universal Semantic Model.
Covers fixed-width integer types, IEEE 754 & Brain floating-point types,
boolean, bitvector, tensor layouts, alignments, strides, and memory spaces.
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Tuple, Optional, Any, Dict
import numpy as np


class MemorySpace(str, enum.Enum):
    GLOBAL = "GLOBAL"
    SHARED = "SHARED"
    LOCAL = "LOCAL"
    CONSTANT = "CONSTANT"
    HOST = "HOST"
    DEVICE = "DEVICE"


class MemoryLayout(str, enum.Enum):
    ROW_MAJOR = "ROW_MAJOR"
    COL_MAJOR = "COL_MAJOR"
    STRIDED = "STRIDED"
    SPARSE_CSR = "SPARSE_CSR"
    SPARSE_CSC = "SPARSE_CSC"
    SPARSE_COO = "SPARSE_COO"


class ExactnessLevel(str, enum.Enum):
    EXACT_BITWISE = "EXACT_BITWISE"
    EXACT_SEMANTIC = "EXACT_SEMANTIC"
    NUMERIC_TOLERANCE = "NUMERIC_TOLERANCE"
    APPROXIMATE = "APPROXIMATE"
    PREDICTIVE = "PREDICTIVE"
    CACHED_EXACT = "CACHED_EXACT"


class VerificationVerdict(str, enum.Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"


class DataType(str, enum.Enum):
    # Signed Integers
    INT8 = "INT8"
    INT16 = "INT16"
    INT32 = "INT32"
    INT64 = "INT64"

    # Unsigned Integers
    UINT8 = "UINT8"
    UINT16 = "UINT16"
    UINT32 = "UINT32"
    UINT64 = "UINT64"

    # Floating Point
    FP16 = "FP16"
    BF16 = "BF16"
    FP32 = "FP32"
    FP64 = "FP64"
    FLOAT16 = "FP16"
    FLOAT32 = "FP32"
    FLOAT64 = "FP64"

    # Complex & Special
    COMPLEX64 = "COMPLEX64"
    COMPLEX128 = "COMPLEX128"
    VOID = "VOID"

    # Boolean & Bitvector
    BOOL = "BOOL"
    BITVECTOR = "BITVECTOR"

    @property
    def byte_size(self) -> int:
        sizes = {
            DataType.INT8: 1,
            DataType.UINT8: 1,
            DataType.INT16: 2,
            DataType.UINT16: 2,
            DataType.INT32: 4,
            DataType.UINT32: 4,
            DataType.INT64: 8,
            DataType.UINT64: 8,
            DataType.FP16: 2,
            DataType.BF16: 2,
            DataType.FP32: 4,
            DataType.FP64: 8,
            DataType.BOOL: 1,
            DataType.BITVECTOR: 1,
        }
        return sizes.get(self, 4)

    @property
    def is_integer(self) -> bool:
        return self in {
            DataType.INT8, DataType.INT16, DataType.INT32, DataType.INT64,
            DataType.UINT8, DataType.UINT16, DataType.UINT32, DataType.UINT64,
        }

    @property
    def is_signed(self) -> bool:
        return self in {
            DataType.INT8, DataType.INT16, DataType.INT32, DataType.INT64,
        }

    @property
    def is_floating_point(self) -> bool:
        return self in {
            DataType.FP16, DataType.BF16, DataType.FP32, DataType.FP64,
        }

    def to_numpy_dtype(self) -> np.dtype:
        mapping = {
            DataType.INT8: np.int8,
            DataType.UINT8: np.uint8,
            DataType.INT16: np.int16,
            DataType.UINT16: np.uint16,
            DataType.INT32: np.int32,
            DataType.UINT32: np.uint32,
            DataType.INT64: np.int64,
            DataType.UINT64: np.uint64,
            DataType.FP16: np.float16,
            DataType.BF16: np.float32,  # BF16 emulation via FP32 container
            DataType.FP32: np.float32,
            DataType.FP64: np.float64,
            DataType.COMPLEX64: np.complex64,
            DataType.COMPLEX128: np.complex128,
            DataType.VOID: np.float32,
            DataType.BOOL: np.bool_,
            DataType.BITVECTOR: np.uint8,
        }
        return np.dtype(mapping[self])

    @classmethod
    def from_numpy_dtype(cls, dt: np.dtype) -> DataType:
        np_dt = np.dtype(dt)
        if np_dt == np.int8:
            return cls.INT8
        elif np_dt == np.uint8:
            return cls.UINT8
        elif np_dt == np.int16:
            return cls.INT16
        elif np_dt == np.uint16:
            return cls.UINT16
        elif np_dt == np.int32:
            return cls.INT32
        elif np_dt == np.uint32:
            return cls.UINT32
        elif np_dt == np.int64:
            return cls.INT64
        elif np_dt == np.uint64:
            return cls.UINT64
        elif np_dt == np.float16:
            return cls.FP16
        elif np_dt == np.float32:
            return cls.FP32
        elif np_dt == np.float64:
            return cls.FP64
        elif np_dt == np.bool_:
            return cls.BOOL
        return cls.FP32


@dataclass(frozen=True)
class TensorType:
    dtype: DataType
    shape: Tuple[int, ...]
    strides: Optional[Tuple[int, ...]] = None
    layout: MemoryLayout = MemoryLayout.ROW_MAJOR
    memory_space: MemorySpace = MemorySpace.GLOBAL
    alignment: int = 64
    endianness: str = "little"

    def __post_init__(self) -> None:
        if self.strides is None and self.shape is not None:
            # Default row-major dense strides (in elements)
            strides = []
            acc = 1
            for dim in reversed(self.shape):
                strides.append(acc)
                acc *= max(1, dim)
            object.__setattr__(self, "strides", tuple(reversed(strides)))

    @property
    def element_count(self) -> int:
        count = 1
        for dim in self.shape:
            count *= dim
        return count

    @property
    def total_bytes(self) -> int:
        return self.element_count * self.dtype.byte_size

    @property
    def is_contiguous(self) -> bool:
        if self.strides is None:
            return True
        expected_acc = 1
        for dim, stride in zip(reversed(self.shape), reversed(self.strides)):
            if stride != expected_acc:
                return False
            expected_acc *= max(1, dim)
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dtype": self.dtype.value,
            "shape": list(self.shape),
            "strides": list(self.strides) if self.strides else None,
            "layout": self.layout.value,
            "memory_space": self.memory_space.value,
            "alignment": self.alignment,
            "endianness": self.endianness,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> TensorType:
        return cls(
            dtype=DataType(d["dtype"]),
            shape=tuple(d["shape"]),
            strides=tuple(d["strides"]) if d.get("strides") else None,
            layout=MemoryLayout(d.get("layout", MemoryLayout.ROW_MAJOR.value)),
            memory_space=MemorySpace(d.get("memory_space", MemorySpace.GLOBAL.value)),
            alignment=d.get("alignment", 64),
            endianness=d.get("endianness", "little"),
        )
