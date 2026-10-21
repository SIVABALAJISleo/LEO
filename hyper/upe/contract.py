"""
hyper/upe/contract.py
=====================
ENGINE 1: Contract Intelligence.

Provides rigorous, typed, and verifiable mathematical contracts for computational workloads.
Every workload contract defines:
- Validation Mode: EXACT, TOLERANCE_BASED, or APPROXIMATE
- Input/output schemas, shapes, dimensions, and numerical constraints
- Floating-point tolerances (absolute and relative)
- Determinism requirements
- Resource ceilings (memory and latency budgets)
- Supported input domain and explicit unsupported boundaries
- Reference implementation baseline
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np


class ValidationMode(str, Enum):
    """The three formal validation modes required by Engine 1."""
    EXACT = "EXACT"                         # Bitwise exact or exact integer/discrete equivalence
    TOLERANCE_BASED = "TOLERANCE_BASED"     # Numerical tolerance |y_hat - y_ref| <= atol + rtol * |y_ref|
    APPROXIMATE = "APPROXIMATE"             # Quality-bounded approximation (cosine similarity >= threshold)


class ExactnessRequirement(str, Enum):
    BITWISE_EXACT = "BITWISE_EXACT"
    MATHEMATICAL_EXACT = "MATHEMATICAL_EXACT"
    IEEE754_STRICT = "IEEE754_STRICT"
    EPSILON_TOLERANT = "EPSILON_TOLERANT"
    COSINE_BOUNDED = "COSINE_BOUNDED"


@dataclasses.dataclass
class TensorSpec:
    """Specification of a tensor or array operand."""
    name: str
    shape: Optional[Tuple[Optional[int], ...]] = None
    dtype: str = "float32"
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allow_nan: bool = False
    allow_inf: bool = False
    sparsity_hint: Optional[float] = None

    def validate(self, data: Any) -> Tuple[bool, Optional[str]]:
        """Validates that real data matches the tensor specification."""
        if not isinstance(data, np.ndarray):
            # Attempt to inspect as array-like
            try:
                arr = np.asarray(data)
            except Exception as e:
                return False, f"Expected ndarray or array-like for '{self.name}', got {type(data).__name__}: {e}"
        else:
            arr = data

        if self.shape is not None and arr.ndim != len(self.shape):
            return False, f"Tensor '{self.name}' rank mismatch: expected {len(self.shape)}, got {arr.ndim}"

        if self.shape is not None:
            for dim_idx, (expected_dim, actual_dim) in enumerate(zip(self.shape, arr.shape)):
                if expected_dim is not None and expected_dim != actual_dim:
                    return False, f"Tensor '{self.name}' dimension {dim_idx} mismatch: expected {expected_dim}, got {actual_dim}"

        if not self.allow_nan and np.isnan(arr).any():
            return False, f"Tensor '{self.name}' contains NaN values (contract disallows NaNs)"

        if not self.allow_inf and np.isinf(arr).any():
            return False, f"Tensor '{self.name}' contains Infinite values (contract disallows Infs)"

        if self.min_value is not None and np.min(arr) < self.min_value:
            return False, f"Tensor '{self.name}' min value {np.min(arr)} < allowed {self.min_value}"

        if self.max_value is not None and np.max(arr) > self.max_value:
            return False, f"Tensor '{self.name}' max value {np.max(arr)} > allowed {self.max_value}"

        return True, None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "shape": list(self.shape) if self.shape else None,
            "dtype": self.dtype,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "allow_nan": self.allow_nan,
            "allow_inf": self.allow_inf,
            "sparsity_hint": self.sparsity_hint,
        }


@dataclasses.dataclass
class WorkloadContract:
    """
    Formal computational contract for a workload.
    """
    workload_id: str
    version: str = "v1.0-upe"
    validation_mode: ValidationMode = ValidationMode.TOLERANCE_BASED
    exactness_requirement: ExactnessRequirement = ExactnessRequirement.EPSILON_TOLERANT
    max_absolute_error: float = 1e-4
    max_relative_error: float = 1e-4
    min_cosine_similarity: float = 0.99
    deterministic: bool = True
    memory_budget_mb: float = 512.0
    latency_deadline_ms: Optional[float] = None
    input_specs: List[TensorSpec] = dataclasses.field(default_factory=list)
    output_spec: Optional[TensorSpec] = None
    supported_input_domain: str = "Real-valued finite matrices/tensors"
    unsupported_cases: List[str] = dataclasses.field(default_factory=lambda: [
        "Unbounded dynamic allocation exceeding memory budget",
        "Non-reproducible external side effects",
    ])
    reference_implementation: str = "numpy_standard_baseline"
    description: str = ""

    def validate_inputs(self, inputs: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate all supplied input tensors against declared specs."""
        errors: List[str] = []
        for spec in self.input_specs:
            if spec.name not in inputs:
                errors.append(f"Missing required input tensor '{spec.name}'")
                continue
            ok, err = spec.validate(inputs[spec.name])
            if not ok and err:
                errors.append(err)
        return len(errors) == 0, errors

    def check_output_compliance(
        self,
        candidate_output: Any,
        reference_output: Any,
    ) -> Tuple[bool, str, Dict[str, float]]:
        """
        Validates candidate output against reference output according to the contract's validation mode.
        Returns: (passed, status_label, metrics_dict).
        """
        cand = np.asarray(candidate_output)
        ref = np.asarray(reference_output)

        if cand.shape != ref.shape:
            return (
                False,
                f"Shape mismatch: candidate shape {cand.shape} != reference shape {ref.shape}",
                {"shape_error": 1.0},
            )

        if self.validation_mode == ValidationMode.EXACT:
            # Must match bitwise or exact integer equality
            if np.issubdtype(cand.dtype, np.integer) or np.issubdtype(cand.dtype, np.bool_):
                is_exact = bool(np.array_equal(cand, ref))
                return (
                    is_exact,
                    "PASS_EXACT" if is_exact else "FAIL_EXACT_MISMATCH",
                    {"mismatched_elements": float(np.sum(cand != ref))},
                )
            else:
                # Floating-point bitwise exact
                diff = np.abs(cand - ref)
                max_diff = float(np.max(diff))
                is_exact = max_diff == 0.0
                return (
                    is_exact,
                    "PASS_EXACT" if is_exact else "FAIL_EXACT_MISMATCH",
                    {"max_abs_diff": max_diff},
                )

        elif self.validation_mode == ValidationMode.TOLERANCE_BASED:
            abs_diff = np.abs(cand - ref)
            max_abs_err = float(np.max(abs_diff)) if abs_diff.size > 0 else 0.0
            
            denom = np.abs(ref)
            denom[denom == 0] = 1.0
            rel_diff = abs_diff / denom
            max_rel_err = float(np.max(rel_diff)) if rel_diff.size > 0 else 0.0

            passed = (max_abs_err <= self.max_absolute_error) or (max_rel_err <= self.max_relative_error)
            status = "PASS_WITHIN_TOLERANCE" if passed else "FAIL_TOLERANCE_EXCEEDED"
            return (
                passed,
                status,
                {"max_abs_err": max_abs_err, "max_rel_err": max_rel_err},
            )

        elif self.validation_mode == ValidationMode.APPROXIMATE:
            # Evaluate cosine similarity on flattened vectors
            cand_flat = cand.ravel().astype(np.float64)
            ref_flat = ref.ravel().astype(np.float64)
            norm_cand = np.linalg.norm(cand_flat)
            norm_ref = np.linalg.norm(ref_flat)

            if norm_cand == 0.0 and norm_ref == 0.0:
                cosine_sim = 1.0
            elif norm_cand == 0.0 or norm_ref == 0.0:
                cosine_sim = 0.0
            else:
                cosine_sim = float(np.dot(cand_flat, ref_flat) / (norm_cand * norm_ref))

            passed = cosine_sim >= self.min_cosine_similarity
            status = "PASS_APPROXIMATE_BOUNDED" if passed else "FAIL_APPROXIMATION_POOR"
            return (
                passed,
                status,
                {"cosine_similarity": cosine_sim, "min_required": self.min_cosine_similarity},
            )

        return False, "UNSUPPORTED_VALIDATION_MODE", {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "version": self.version,
            "validation_mode": self.validation_mode.value,
            "exactness_requirement": self.exactness_requirement.value,
            "max_absolute_error": self.max_absolute_error,
            "max_relative_error": self.max_relative_error,
            "min_cosine_similarity": self.min_cosine_similarity,
            "deterministic": self.deterministic,
            "memory_budget_mb": self.memory_budget_mb,
            "latency_deadline_ms": self.latency_deadline_ms,
            "input_specs": [s.to_dict() for s in self.input_specs],
            "output_spec": self.output_spec.to_dict() if self.output_spec else None,
            "supported_input_domain": self.supported_input_domain,
            "unsupported_cases": self.unsupported_cases,
            "reference_implementation": self.reference_implementation,
            "description": self.description,
        }


class ContractRegistry:
    """Registry of pre-verified and user-submitted workload contracts."""

    def __init__(self) -> None:
        self._contracts: Dict[str, WorkloadContract] = {}
        self._register_canonical_contracts()

    def register(self, contract: WorkloadContract) -> None:
        self._contracts[contract.workload_id] = contract

    def get(self, workload_id: str) -> Optional[WorkloadContract]:
        return self._contracts.get(workload_id)

    def list_contracts(self) -> List[Dict[str, Any]]:
        return [c.to_dict() for c in self._contracts.values()]

    def _register_canonical_contracts(self) -> None:
        """Seeds canonical contracts for core mathematical & machine learning primitives."""
        # 1. Horner Polynomial Evaluation
        self.register(WorkloadContract(
            workload_id="horner_polynomial",
            version="v1.0-exact",
            validation_mode=ValidationMode.EXACT,
            exactness_requirement=ExactnessRequirement.MATHEMATICAL_EXACT,
            description="Evaluates high-degree polynomials using Horner's O(N) rule instead of naive O(N^2) evaluation.",
            supported_input_domain="1D real coefficients and scalar query point",
            reference_implementation="naive_polynomial_powers",
        ))

        # 2. Prefix-Sum Range Query
        self.register(WorkloadContract(
            workload_id="prefix_sum_queries",
            version="v1.0-exact",
            validation_mode=ValidationMode.EXACT,
            exactness_requirement=ExactnessRequirement.BITWISE_EXACT,
            description="Transforms K repeated interval sum queries from O(K*N) to O(1) per query via prefix table.",
            supported_input_domain="1D numerical array and interval pairs [L, R]",
            reference_implementation="iterative_range_slice_sum",
        ))

        # 3. Dense Matrix Multiplication (GEMM)
        self.register(WorkloadContract(
            workload_id="dense_gemm",
            version="v1.0-tol",
            validation_mode=ValidationMode.TOLERANCE_BASED,
            exactness_requirement=ExactnessRequirement.EPSILON_TOLERANT,
            max_absolute_error=1e-4,
            max_relative_error=1e-4,
            description="Matrix multiplication of 2D real matrices with cache blocking / tiling.",
            supported_input_domain="2D finite floating-point matrices",
            reference_implementation="numpy_matmul",
        ))

        # 4. Fused GEMM + Bias + ReLU
        self.register(WorkloadContract(
            workload_id="fused_gemm_bias_relu",
            version="v1.0-fused",
            validation_mode=ValidationMode.TOLERANCE_BASED,
            exactness_requirement=ExactnessRequirement.EPSILON_TOLERANT,
            max_absolute_error=1e-4,
            max_relative_error=1e-4,
            description="Fused matrix multiplication, bias vector addition, and ReLU activation.",
            supported_input_domain="2D matrices A, B, and 1D bias vector",
            reference_implementation="numpy_gemm_plus_bias_relu",
        ))

        # 5. Sparse Matrix-Vector (SpMV)
        self.register(WorkloadContract(
            workload_id="sparse_spmv",
            version="v1.0-sparse",
            validation_mode=ValidationMode.TOLERANCE_BASED,
            exactness_requirement=ExactnessRequirement.EPSILON_TOLERANT,
            max_absolute_error=1e-4,
            max_relative_error=1e-4,
            description="Exploits sparsity >= 20% using CSR / 2:4 structured patterns.",
            supported_input_domain="Sparsity >= 20% in weight matrix",
            reference_implementation="dense_matrix_vector_dot",
        ))

        # 6. Streaming Out-of-Core GEMV
        self.register(WorkloadContract(
            workload_id="streaming_gemv",
            version="v1.0-stream",
            validation_mode=ValidationMode.TOLERANCE_BASED,
            exactness_requirement=ExactnessRequirement.EPSILON_TOLERANT,
            max_absolute_error=1e-4,
            max_relative_error=1e-4,
            memory_budget_mb=64.0,
            description="Bounded-memory chunked matrix-vector product for large out-of-core datasets.",
            supported_input_domain="Large row-chunked matrix stream and input vector",
            reference_implementation="monolithic_dense_gemv",
        ))

        # 7. BitNet 1.58b Ternary Linear
        self.register(WorkloadContract(
            workload_id="bitnet_ternary_linear",
            version="v1.0-approx",
            validation_mode=ValidationMode.APPROXIMATE,
            exactness_requirement=ExactnessRequirement.COSINE_BOUNDED,
            min_cosine_similarity=0.98,
            description="Ternary weights {-1, 0, +1} converting FP32 multiplies into additions and subtractions.",
            supported_input_domain="Weights with bounded dynamic range",
            reference_implementation="fp32_dense_linear",
        ))
