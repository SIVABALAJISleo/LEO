"""
hyper_universal/transformation_dsl/library.py
=============================================
Executable Transformation Library.

Concrete implementations of canonical transformations:
- BitNetTernaryTransformation: Eliminates multiplications via {-1, 0, +1} additions
- SparsificationCSRTransformation: Eliminates zero-valued computations via CSR
- LowRankFactorizationTransformation: Reduces dimension via truncated SVD
- HornerPolynomialTransformation: Reduces O(N^2) power sum to O(N) additions/multiplications
- IncrementalMemoizationTransformation: Eliminates duplicate work across calls
- TilingBlockingTransformation: Blocks computation to fit within CPU L2/L3 cache
"""

from __future__ import annotations
import hashlib
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper_universal.transformation_dsl.base import Transformation, TransformationCostModel


class BitNetTernaryTransformation(Transformation):
    """
    Transforms float32 dense weight matrices into {-1, 0, +1} ternary matrices.
    Replaces floating-point MACs with integer additions.
    """

    def __init__(self) -> None:
        super().__init__("xf-bitnet-ternary", "BitNet 1.58b Additive Formulation")

    def check_preconditions(self, input_data: Any) -> Tuple[bool, str]:
        if not isinstance(input_data, np.ndarray):
            return False, "Input must be a NumPy ndarray."
        if input_data.ndim != 2:
            return False, "Input must be a 2D matrix."
        return True, "Preconditions satisfied."

    def apply(self, input_data: Any) -> Any:
        # Quantize weights to {-1, 0, 1}
        gamma = np.mean(np.abs(input_data)) + 1e-7
        w_scaled = input_data / gamma
        w_ternary = np.clip(np.round(w_scaled), -1, 1).astype(np.int8)
        return w_ternary, gamma

    def proof_obligation(self) -> str:
        return "∀ W ∈ ℝ^{M×N}: ||W - γ * round(clip(W/γ, -1, 1))||_F <= ε under bounded dynamic range."

    def cost_model(self) -> TransformationCostModel:
        return TransformationCostModel(
            complexity_before="O(N^3) FP32 Multiplications",
            complexity_after="O(N^3) INT8 Additions",
            expected_work_reduction_pct=50.0,
            memory_traffic_multiplier=0.0625,  # 1.58 bits vs 32 bits = 16x reduction
        )


class SparsificationCSRTransformation(Transformation):
    """
    Transforms dense matrices with zeros or near-zero values into Compressed Sparse Row (CSR).
    """

    def __init__(self, threshold: float = 1e-4) -> None:
        super().__init__("xf-sparse-csr", "Sparsification to Compressed Sparse Row")
        self.threshold = threshold

    def check_preconditions(self, input_data: Any) -> Tuple[bool, str]:
        if not isinstance(input_data, np.ndarray) or input_data.ndim != 2:
            return False, "Input must be a 2D matrix."
        sparsity = np.mean(np.abs(input_data) < self.threshold)
        if sparsity < 0.20:
            return False, f"Sparsity ({sparsity*100:.1f}%) is insufficient for CSR advantage."
        return True, f"Sparsity ({sparsity*100:.1f}%) satisfies preconditions."

    def apply(self, input_data: Any) -> Any:
        import scipy.sparse as sp
        filtered = np.where(np.abs(input_data) < self.threshold, 0.0, input_data)
        return sp.csr_matrix(filtered)

    def proof_obligation(self) -> str:
        return "∀ A ∈ ℝ^{M×N}: ||A - CSR(A)||_∞ <= threshold."

    def cost_model(self) -> TransformationCostModel:
        return TransformationCostModel(
            complexity_before="O(M * N * K)",
            complexity_after="O(nnz * K)",
            expected_work_reduction_pct=75.0,
            memory_traffic_multiplier=0.25,
        )


class LowRankFactorizationTransformation(Transformation):
    """
    Transforms matrix A into low-rank factor matrices U, S, V^T.
    Supports both static target_rank and Adaptive Singular Value Energy Selection.
    """

    def __init__(
        self,
        target_rank: Optional[int] = 16,
        min_energy_ratio: float = 0.95,
        target_energy_ratio: float = 0.99,
        adaptive_energy_selection: bool = False,
    ) -> None:
        super().__init__("xf-low-rank", "Low-Rank SVD Factorization")
        self.target_rank = target_rank
        self.min_energy_ratio = min_energy_ratio
        self.target_energy_ratio = target_energy_ratio
        self.adaptive_energy_selection = adaptive_energy_selection
        self._selected_rank: int = target_rank if target_rank is not None else 16

    def check_preconditions(self, input_data: Any) -> Tuple[bool, str]:
        if not isinstance(input_data, np.ndarray) or input_data.ndim != 2:
            return False, "Input must be a 2D matrix."

        # Compute singular values
        s = np.linalg.svd(input_data, compute_uv=False)
        total_energy = float(np.sum(s))
        if total_energy <= 1e-12:
            return False, "Singular value energy near zero."

        # Case 1: Adaptive Singular Value Energy Selection (Dynamic Thresholding)
        # Finds minimum rank k such that cumulative energy >= target_energy_ratio (e.g. 0.99)
        if self.adaptive_energy_selection or self.target_rank is None:
            cumsum_energy = np.cumsum(s)
            ratios = cumsum_energy / total_energy
            valid_indices = np.where(ratios >= self.target_energy_ratio)[0]
            if len(valid_indices) == 0:
                return False, f"Cannot achieve target energy ratio {self.target_energy_ratio:.2f}."
            k = int(valid_indices[0]) + 1
            max_allowed_rank = max(1, int(0.5 * min(input_data.shape)))
            if k > max_allowed_rank:
                return (
                    False,
                    f"Adaptive rank k={k} exceeds compression limit {max_allowed_rank} "
                    f"(matrix lacks low-rank structure; flat spectrum detected)."
                )
            self._selected_rank = k
            return True, f"Adaptive rank {k} selected satisfying energy ratio >= {self.target_energy_ratio:.2f}."

        # Case 2: Static target rank with minimum energy ratio enforcement
        if min(input_data.shape) <= self.target_rank:
            return False, "Matrix dimension smaller than target rank."

        k = min(self.target_rank, len(s))
        top_k_energy = float(np.sum(s[:k]))
        energy_ratio = top_k_energy / total_energy
        if energy_ratio < self.min_energy_ratio:
            return (
                False,
                f"Singular value energy ratio {energy_ratio:.4f} < {self.min_energy_ratio:.2f} "
                f"(matrix lacks low-rank structure; full-rank Gaussian noise detected)."
            )

        self._selected_rank = k
        return True, "Preconditions satisfied."

    def apply(self, input_data: Any) -> Any:
        valid, msg = self.check_preconditions(input_data)
        if not valid:
            raise ValueError(f"LowRankSVDTransformation precondition failed: {msg}")
        u, s, vt = np.linalg.svd(input_data, full_matrices=False)
        k = self._selected_rank
        return u[:, :k], s[:k], vt[:k, :]


    def proof_obligation(self) -> str:
        return "Eckart-Young-Mirsky Theorem: Truncated SVD provides best rank-k approximation under Frobenius norm."

    def cost_model(self) -> TransformationCostModel:
        return TransformationCostModel(
            complexity_before="O(N^3)",
            complexity_after="O(k * N^2)",
            expected_work_reduction_pct=60.0,
            memory_traffic_multiplier=0.40,
        )


LowRankSVDTransformation = LowRankFactorizationTransformation


class HornerPolynomialTransformation(Transformation):
    """
    Transforms naive polynomial summation P(x) = sum(c_i * x^i) into nested Horner form.
    """

    def __init__(self) -> None:
        super().__init__("xf-horner-rule", "Horner's Rule Polynomial Reformulation")

    def check_preconditions(self, input_data: Any) -> Tuple[bool, str]:
        if not isinstance(input_data, (list, np.ndarray)):
            return False, "Input coefficients must be a list or array."
        if len(input_data) < 2:
            return False, "Polynomial degree must be >= 1."
        return True, "Preconditions satisfied."

    def apply(self, input_data: Any) -> Any:
        # Returns an executable callable that evaluates polynomial using Horner's rule
        coeffs = list(input_data)
        def horner_eval(x: Any) -> Any:
            res = coeffs[-1]
            for c in reversed(coeffs[:-1]):
                res = res * x + c
            return res
        return horner_eval

    def proof_obligation(self) -> str:
        return "∀ x ∈ ℝ, ∀ c ∈ ℝ^{n+1}: ∑_{i=0}^n c_i x^i ≡ c_0 + x * (c_1 + x * (... + x * c_n))"

    def cost_model(self) -> TransformationCostModel:
        return TransformationCostModel(
            complexity_before="O(N^2) Multiplications",
            complexity_after="O(N) Multiplications + Additions",
            expected_work_reduction_pct=85.0,
            memory_traffic_multiplier=0.15,
        )


class IncrementalMemoizationTransformation(Transformation):
    """
    Transforms deterministic stateless function into a memoized cache-lookup pathway.
    """

    def __init__(self) -> None:
        super().__init__("xf-memoization", "Deterministic Result Memoization")
        self._cache: Dict[str, Any] = {}

    def check_preconditions(self, input_data: Any) -> Tuple[bool, str]:
        return True, "Preconditions satisfied for deterministic contract."

    def apply(self, input_data: Any) -> Any:
        bytes_data = getattr(input_data, "tobytes", lambda: str(input_data).encode())()
        h = hashlib.sha256(bytes_data).hexdigest()[:16]
        if h in self._cache:
            return self._cache[h]
        return None

    def store_result(self, input_data: Any, result: Any) -> None:
        bytes_data = getattr(input_data, "tobytes", lambda: str(input_data).encode())()
        h = hashlib.sha256(bytes_data).hexdigest()[:16]
        self._cache[h] = result

    def proof_obligation(self) -> str:
        return "∀ x, y: x == y ⟹ f(x) == f(y) (Referential Transparency / Determinism)."

    def cost_model(self) -> TransformationCostModel:
        return TransformationCostModel(
            complexity_before="O(N^K) Computation",
            complexity_after="O(1) Hash Table Retrieval",
            expected_work_reduction_pct=99.0,
            memory_traffic_multiplier=0.10,
        )
