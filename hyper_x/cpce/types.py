"""
hyper_x/cpce/types.py
=====================
Structure-Preserving Tagged Matrix and Tensor Representations for CPCE.
Avoids accidental full densification and preserves mathematical properties
(Identity, Zero, Diagonal, Sparse, Low-Rank) from creation through execution.
"""

from __future__ import annotations

import abc
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


class MatrixStructure(str, Enum):
    """Enumeration of recognized mathematical tensor structures."""
    DENSE = "DENSE"
    IDENTITY = "IDENTITY"
    ZERO = "ZERO"
    DIAGONAL = "DIAGONAL"
    SPARSE = "SPARSE"
    LOW_RANK = "LOW_RANK"


class TaggedMatrix(abc.ABC):

    """Abstract base class for all structure-preserving tagged matrix representations."""

    @property
    @abc.abstractmethod
    def shape(self) -> Tuple[int, int]:
        """Returns (rows, cols) shape."""
        pass

    @property
    @abc.abstractmethod
    def dtype(self) -> str:
        """Returns data type name, e.g. 'float32'."""
        pass

    @property
    @abc.abstractmethod
    def structure_type(self) -> str:
        """Returns structure tag: DENSE, IDENTITY, ZERO, DIAGONAL, SPARSE, LOW_RANK."""
        pass

    @abc.abstractmethod
    def to_dense(self) -> np.ndarray:
        """Materializes full dense NumPy array when explicitly required."""
        pass

    @abc.abstractmethod
    def matmul(self, other: Union[TaggedMatrix, np.ndarray]) -> TaggedMatrix:
        """Computes matrix multiplication with another matrix, preserving structure where possible."""
        pass

    @abc.abstractmethod
    def scalar_mul(self, scalar: float) -> TaggedMatrix:
        """Multiplies matrix by a scalar value."""
        pass

    @property
    @abc.abstractmethod
    def nbytes(self) -> int:
        """Returns actual in-memory bytes occupied by this representation."""
        pass

    def __array__(self, dtype=None) -> np.ndarray:
        """NumPy array interface: materializes dense representation when coerced."""
        arr = self.to_dense()
        if dtype is not None:
            return arr.astype(dtype)
        return arr



class DenseMatrix(TaggedMatrix):
    """Standard dense matrix backed by a contiguous NumPy array."""

    def __init__(self, data: np.ndarray):
        assert data.ndim == 2, f"DenseMatrix requires 2D array, got {data.ndim}D"
        self._data = np.ascontiguousarray(data)

    @property
    def shape(self) -> Tuple[int, int]:
        return (int(self._data.shape[0]), int(self._data.shape[1]))

    @property
    def dtype(self) -> str:
        return str(self._data.dtype)

    @property
    def structure_type(self) -> str:
        return "DENSE"

    @property
    def nbytes(self) -> int:
        return int(self._data.nbytes)

    @property
    def data(self) -> np.ndarray:
        return self._data

    def to_dense(self) -> np.ndarray:
        return self._data

    def matmul(self, other: Union[TaggedMatrix, np.ndarray]) -> TaggedMatrix:
        if isinstance(other, IdentityMatrix):
            assert self.shape[1] == other.shape[0], f"Shape mismatch: {self.shape} vs {other.shape}"
            return self

        if isinstance(other, ZeroMatrix):
            assert self.shape[1] == other.shape[0], f"Shape mismatch: {self.shape} vs {other.shape}"
            return ZeroMatrix((self.shape[0], other.shape[1]), dtype=self.dtype)

        if isinstance(other, DiagonalMatrix):
            assert self.shape[1] == other.shape[0], f"Shape mismatch: {self.shape} vs {other.shape}"
            # Row-wise scaling by diagonal elements: A * diag
            res = self._data * other.diagonal
            return DenseMatrix(res)

        other_arr = other.to_dense() if isinstance(other, TaggedMatrix) else np.asarray(other)
        assert self.shape[1] == other_arr.shape[0], f"Shape mismatch: {self.shape} vs {other_arr.shape}"
        res = np.matmul(self._data, other_arr)
        return DenseMatrix(res)

    def scalar_mul(self, scalar: float) -> TaggedMatrix:
        return DenseMatrix(self._data * scalar)


class IdentityMatrix(TaggedMatrix):
    """
    Structure-preserving Identity Matrix I_n.
    Eliminates all O(N^3) arithmetic in matrix multiplications:
    I * B = B, A * I = A.
    """

    def __init__(self, n: int, dtype: str = "float32"):
        assert n > 0, "Dimension n must be positive"
        self._n = int(n)
        self._dtype = dtype

    @property
    def shape(self) -> Tuple[int, int]:
        return (self._n, self._n)

    @property
    def dtype(self) -> str:
        return self._dtype

    @property
    def structure_type(self) -> str:
        return "IDENTITY"

    @property
    def nbytes(self) -> int:
        # Constant space: 8 bytes for dimension integer
        return 8

    def to_dense(self) -> np.ndarray:
        return np.eye(self._n, dtype=self._dtype)

    def matmul(self, other: Union[TaggedMatrix, np.ndarray]) -> TaggedMatrix:
        if isinstance(other, TaggedMatrix):
            assert self._n == other.shape[0], f"Shape mismatch: {self.shape} vs {other.shape}"
            return other
        other_arr = np.asarray(other)
        assert self._n == other_arr.shape[0], f"Shape mismatch: {self.shape} vs {other_arr.shape}"
        return DenseMatrix(other_arr.copy())

    def scalar_mul(self, scalar: float) -> TaggedMatrix:
        if scalar == 0.0:
            return ZeroMatrix(self.shape, dtype=self._dtype)
        if scalar == 1.0:
            return self
        diag = np.full(self._n, scalar, dtype=self._dtype)
        return DiagonalMatrix(diag)


class ZeroMatrix(TaggedMatrix):
    """
    Structure-preserving Zero Matrix 0_{M, N}.
    Eliminates all arithmetic in matrix multiplications:
    0 * B = 0, A * 0 = 0.
    """

    def __init__(self, shape: Union[Tuple[int, int], int], cols: Optional[int] = None, dtype: str = "float32"):
        if isinstance(shape, int):
            assert cols is not None and cols > 0, f"ZeroMatrix requires positive cols when rows is int, got {cols}"
            self._shape = (int(shape), int(cols))
        else:
            assert len(shape) == 2 and shape[0] > 0 and shape[1] > 0, f"Invalid shape: {shape}"
            self._shape = (int(shape[0]), int(shape[1]))
        self._dtype = dtype


    @property
    def shape(self) -> Tuple[int, int]:
        return self._shape

    @property
    def dtype(self) -> str:
        return self._dtype

    @property
    def structure_type(self) -> str:
        return "ZERO"

    @property
    def nbytes(self) -> int:
        # Constant space: 16 bytes for shape tuple
        return 16

    def to_dense(self) -> np.ndarray:
        return np.zeros(self._shape, dtype=self._dtype)

    def matmul(self, other: Union[TaggedMatrix, np.ndarray]) -> TaggedMatrix:
        other_cols = other.shape[1] if isinstance(other, TaggedMatrix) else other.shape[1]
        assert self._shape[1] == (other.shape[0] if isinstance(other, TaggedMatrix) else other.shape[0]), "Shape mismatch"
        return ZeroMatrix((self._shape[0], other_cols), dtype=self._dtype)

    def scalar_mul(self, scalar: float) -> TaggedMatrix:
        return self


class DiagonalMatrix(TaggedMatrix):
    """
    Structure-preserving Diagonal Matrix diag(v).
    Reduces O(N^3) matrix multiplication to O(N^2) scaling operations:
    diag(v) * B = v[:, None] * B.
    """

    def __init__(self, diagonal: np.ndarray):
        assert diagonal.ndim == 1, f"Diagonal must be 1D vector, got {diagonal.ndim}D"
        self._diag = np.ascontiguousarray(diagonal)
        self._n = len(self._diag)

    @property
    def diagonal(self) -> np.ndarray:
        return self._diag

    @property
    def shape(self) -> Tuple[int, int]:
        return (self._n, self._n)

    @property
    def dtype(self) -> str:
        return str(self._diag.dtype)

    @property
    def structure_type(self) -> str:
        return "DIAGONAL"

    @property
    def nbytes(self) -> int:
        return int(self._diag.nbytes)

    def to_dense(self) -> np.ndarray:
        return np.diag(self._diag)

    def matmul(self, other: Union[TaggedMatrix, np.ndarray]) -> TaggedMatrix:
        if isinstance(other, IdentityMatrix):
            assert self._n == other.shape[0], f"Shape mismatch: {self.shape} vs {other.shape}"
            return self

        if isinstance(other, ZeroMatrix):
            assert self._n == other.shape[0], f"Shape mismatch: {self.shape} vs {other.shape}"
            return ZeroMatrix((self._n, other.shape[1]), dtype=self.dtype)

        if isinstance(other, DiagonalMatrix):
            assert self._n == other.shape[0], f"Shape mismatch: {self.shape} vs {other.shape}"
            # Two diagonal matrices multiply elementwise: diag(u * v)
            return DiagonalMatrix(self._diag * other.diagonal)

        other_arr = other.to_dense() if isinstance(other, TaggedMatrix) else np.asarray(other)
        assert self._n == other_arr.shape[0], f"Shape mismatch: {self.shape} vs {other_arr.shape}"
        # Diagonal multiplication is broadcast row-scaling: O(N^2) instead of O(N^3)
        res = self._diag[:, np.newaxis] * other_arr
        return DenseMatrix(res)

    def scalar_mul(self, scalar: float) -> TaggedMatrix:
        if scalar == 0.0:
            return ZeroMatrix(self.shape, dtype=self.dtype)
        return DiagonalMatrix(self._diag * scalar)


class SparseMatrix(TaggedMatrix):
    """
    Structure-preserving Compressed Sparse Row (CSR) matrix representation.
    Preserves sparsity without allocating memory for zero elements.
    """

    def __init__(
        self,
        data: np.ndarray,
        indices: np.ndarray,
        indptr: np.ndarray,
        shape: Tuple[int, int],
    ):
        self._data = np.ascontiguousarray(data)
        self._indices = np.ascontiguousarray(indices, dtype=np.int32)
        self._indptr = np.ascontiguousarray(indptr, dtype=np.int32)
        self._shape = (int(shape[0]), int(shape[1]))

    @property
    def shape(self) -> Tuple[int, int]:
        return self._shape

    @property
    def dtype(self) -> str:
        return str(self._data.dtype)

    @property
    def structure_type(self) -> str:
        return "SPARSE"

    @property
    def nnz(self) -> int:
        return len(self._data)

    @property
    def sparsity(self) -> float:
        total = self._shape[0] * self._shape[1]
        return 1.0 - (self.nnz / max(1, total))

    @property
    def nbytes(self) -> int:
        return int(self._data.nbytes + self._indices.nbytes + self._indptr.nbytes)

    @classmethod
    def from_dense(cls, arr: np.ndarray, threshold: float = 1e-7) -> SparseMatrix:
        """Converts dense array to CSR sparse representation."""
        rows, cols = arr.shape
        data_list: List[float] = []
        indices_list: List[int] = []
        indptr = [0]

        for i in range(rows):
            for j in range(cols):
                val = arr[i, j]
                if abs(val) > threshold:
                    data_list.append(float(val))
                    indices_list.append(j)
            indptr.append(len(data_list))

        return cls(
            data=np.array(data_list, dtype=arr.dtype),
            indices=np.array(indices_list, dtype=np.int32),
            indptr=np.array(indptr, dtype=np.int32),
            shape=(rows, cols),
        )

    def to_dense(self) -> np.ndarray:
        out = np.zeros(self._shape, dtype=self.dtype)
        for i in range(self._shape[0]):
            start = self._indptr[i]
            end = self._indptr[i + 1]
            for idx in range(start, end):
                col = self._indices[idx]
                out[i, col] = self._data[idx]
        return out

    def matmul(self, other: Union[TaggedMatrix, np.ndarray]) -> TaggedMatrix:
        other_arr = other.to_dense() if isinstance(other, TaggedMatrix) else np.asarray(other)
        assert self._shape[1] == other_arr.shape[0], f"Shape mismatch: {self._shape} vs {other_arr.shape}"

        # Sparse-dense matrix multiplication: O(nnz * K) instead of O(M * N * K)
        M, _ = self._shape
        K = other_arr.shape[1] if other_arr.ndim == 2 else 1
        out = np.zeros((M, K), dtype=self.dtype)

        for i in range(M):
            start = self._indptr[i]
            end = self._indptr[i + 1]
            for idx in range(start, end):
                col = self._indices[idx]
                val = self._data[idx]
                out[i, :] += val * other_arr[col, :]

        return DenseMatrix(out)

    def scalar_mul(self, scalar: float) -> TaggedMatrix:
        if scalar == 0.0:
            return ZeroMatrix(self._shape, dtype=self.dtype)
        return SparseMatrix(
            data=self._data * scalar,
            indices=self._indices.copy(),
            indptr=self._indptr.copy(),
            shape=self._shape,
        )


class LowRankMatrix(TaggedMatrix):
    """
    Structure-preserving Low-Rank representation A = U * V^T where rank k << min(M, N).
    Reduces matrix-vector evaluation from O(M * N) to O(k * (M + N)).
    """

    def __init__(self, U: np.ndarray, V: np.ndarray):
        assert U.ndim == 2 and V.ndim == 2, "U and V must be 2D matrices"
        assert U.shape[1] == V.shape[1], f"Rank dimension mismatch: {U.shape[1]} vs {V.shape[1]}"
        self._U = np.ascontiguousarray(U)
        self._V = np.ascontiguousarray(V)
        self._M = U.shape[0]
        self._N = V.shape[0]
        self._k = U.shape[1]

    @property
    def shape(self) -> Tuple[int, int]:
        return (self._M, self._N)

    @property
    def dtype(self) -> str:
        return str(self._U.dtype)

    @property
    def structure_type(self) -> str:
        return "LOW_RANK"

    @property
    def rank(self) -> int:
        return self._k

    @property
    def nbytes(self) -> int:
        return int(self._U.nbytes + self._V.nbytes)

    def to_dense(self) -> np.ndarray:
        return np.matmul(self._U, self._V.T)

    def matmul(self, other: Union[TaggedMatrix, np.ndarray]) -> TaggedMatrix:
        other_arr = other.to_dense() if isinstance(other, TaggedMatrix) else np.asarray(other)
        assert self._N == other_arr.shape[0], f"Shape mismatch: {self.shape} vs {other_arr.shape}"

        # Associative factorization: U * (V^T * B) reduces operations
        vt_b = np.matmul(self._V.T, other_arr)
        res = np.matmul(self._U, vt_b)
        return DenseMatrix(res)

    def scalar_mul(self, scalar: float) -> TaggedMatrix:
        return LowRankMatrix(self._U * scalar, self._V.copy())
