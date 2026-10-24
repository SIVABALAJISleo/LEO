"""
hyper/canonical/workload_registry.py
====================================
Authoritative Canonical 15-Workload Contract Registry.

Enforces unambiguous, versioned computational contracts, explicit exactness
policies, numerical tolerance semantics, input/output schemas, and fail-closed
verification checks across all 15 canonical workloads.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
import math
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


class ExactnessClass(str, Enum):
    """
    Formal exactness classes required by the verification engine.
    """
    BIT_EXACT = "BIT_EXACT"                                 # Exact identical bit representation
    INTEGER_EXACT = "INTEGER_EXACT"                         # Exact integer value equality with overflow rules
    NUMERICALLY_EQUIVALENT = "NUMERICALLY_EQUIVALENT"       # |cand - ref| <= atol + rtol * |ref|
    SEMANTICALLY_EQUIVALENT = "SEMANTICALLY_EQUIVALENT"     # Domain-specific task contract (e.g. valid permutation or hash digest)


@dataclasses.dataclass
class TensorSchema:
    """Schema specification for an input or output tensor."""
    name: str
    shape: Optional[Tuple[Optional[int], ...]] = None
    dtype: str = "float32"
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allow_nan: bool = False
    allow_inf: bool = False

    def validate(self, data: Any) -> Tuple[bool, Optional[str]]:
        """Validates that real runtime data satisfies the schema."""
        if data is None:
            return False, f"Operand '{self.name}' is None"

        if isinstance(data, (bytes, str)):
            # Byte or string payload
            if self.dtype == "bytes" and not isinstance(data, (bytes, bytearray)):
                return False, f"Expected bytes for '{self.name}', got {type(data).__name__}"
            if self.dtype == "str" and not isinstance(data, str):
                return False, f"Expected str for '{self.name}', got {type(data).__name__}"
            return True, None

        if isinstance(data, (int, float, np.number)):
            arr = np.asarray(data)
        elif isinstance(data, (list, tuple, np.ndarray)):
            arr = np.asarray(data)
        else:
            return False, f"Unsupported data type for '{self.name}': {type(data).__name__}"

        if self.shape is not None:
            if arr.ndim != len(self.shape):
                return False, f"Tensor '{self.name}' rank mismatch: expected {len(self.shape)}, got {arr.ndim}"
            for i, (exp_dim, act_dim) in enumerate(zip(self.shape, arr.shape)):
                if exp_dim is not None and exp_dim != act_dim:
                    return False, f"Tensor '{self.name}' dimension {i} mismatch: expected {exp_dim}, got {act_dim}"

        if np.iscomplexobj(arr):
            if not self.allow_nan and (np.isnan(arr.real).any() or np.isnan(arr.imag).any()):
                return False, f"Tensor '{self.name}' contains NaN components"
            if not self.allow_inf and (np.isinf(arr.real).any() or np.isinf(arr.imag).any()):
                return False, f"Tensor '{self.name}' contains Inf components"
        elif arr.dtype.kind in ("f", "c"):
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
            "shape": list(self.shape) if self.shape is not None else None,
            "dtype": self.dtype,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "allow_nan": self.allow_nan,
            "allow_inf": self.allow_inf,
        }


@dataclasses.dataclass
class CanonicalWorkloadContract:
    """
    Formal, typed, versioned workload contract governing canonical execution.
    """
    workload_id: str
    name: str
    version: str = "v2.0-canonical"
    mathematical_contract: str = ""
    input_schemas: Dict[str, TensorSchema] = dataclasses.field(default_factory=dict)
    output_schema: Optional[TensorSchema] = None
    exactness_class: ExactnessClass = ExactnessClass.NUMERICALLY_EQUIVALENT
    atol: float = 1e-4
    rtol: float = 1e-4
    determinism_required: bool = True
    reference_impl_id: str = ""
    candidate_impl_id: str = ""
    required_edge_cases: List[str] = dataclasses.field(default_factory=list)
    required_adversarial_cases: List[str] = dataclasses.field(default_factory=list)
    timeout_ms: float = 10000.0
    memory_budget_mb: float = 1024.0
    supported_backends: List[str] = dataclasses.field(default_factory=lambda: ["CPU_AVX2", "INTEL_UHD_IGPU", "FALLBACK_CPU"])
    expected_fallback_backend: str = "FALLBACK_CPU"
    verification_status: str = "CANONICAL_ACTIVE"
    evidence_links: List[str] = dataclasses.field(default_factory=list)

    def validate_inputs(self, inputs: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validates all inputs against declared schemas."""
        errors: List[str] = []
        for name, schema in self.input_schemas.items():
            if name not in inputs:
                errors.append(f"Missing required operand '{name}'")
                continue
            ok, err = schema.validate(inputs[name])
            if not ok and err:
                errors.append(err)
        return len(errors) == 0, errors

    def check_output_compliance(
        self,
        candidate_output: Any,
        reference_output: Any,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Independent verification of candidate output against reference output.
        Evaluates exactness class semantics:
        - BIT_EXACT: bitwise identical array equality or bytes match.
        - INTEGER_EXACT: integer equality with overflow boundaries.
        - NUMERICALLY_EQUIVALENT: |cand - ref| <= atol + rtol * |ref|
        - SEMANTICALLY_EQUIVALENT: task-specific contract invariant check.
        """
        # Validate output schema on candidate if present
        if self.output_schema is not None:
            ok, err = self.output_schema.validate(candidate_output)
            if not ok:
                return False, f"FAIL_OUTPUT_SCHEMA: {err}", {"schema_error": 1.0}

        # 1. Byte / String outputs (e.g. SHA-256)
        if isinstance(reference_output, (bytes, bytearray, str)):
            if candidate_output == reference_output:
                return True, "PASS_BIT_EXACT", {"exact_match": 1.0}
            return False, "FAIL_BIT_EXACT_MISMATCH", {"exact_match": 0.0}

        cand = np.asarray(candidate_output)
        ref = np.asarray(reference_output)

        # Shape consistency check
        if cand.shape != ref.shape:
            return False, f"FAIL_SHAPE_MISMATCH: candidate shape {cand.shape} != reference shape {ref.shape}", {"shape_mismatch": 1.0}

        # 2. BIT_EXACT Policy
        if self.exactness_class == ExactnessClass.BIT_EXACT:
            if cand.dtype != ref.dtype:
                return False, f"FAIL_DTYPE_MISMATCH: {cand.dtype} vs {ref.dtype}", {"dtype_mismatch": 1.0}
            is_exact = bool(np.array_equal(cand, ref))
            if not is_exact:
                diff_count = int(np.sum(cand != ref))
                return False, f"FAIL_BIT_EXACT_MISMATCH: {diff_count} differing elements", {"differing_elements": diff_count}
            return True, "PASS_BIT_EXACT", {"differing_elements": 0}

        # 3. INTEGER_EXACT Policy
        if self.exactness_class == ExactnessClass.INTEGER_EXACT:
            if not (np.issubdtype(cand.dtype, np.integer) or np.issubdtype(ref.dtype, np.integer)):
                return False, "FAIL_INTEGER_EXACT_NON_INTEGER_TYPE", {"error": 1.0}
            is_exact = bool(np.array_equal(cand, ref))
            if not is_exact:
                max_int_diff = int(np.max(np.abs(cand.astype(np.int64) - ref.astype(np.int64))))
                return False, f"FAIL_INTEGER_EXACT_MISMATCH: max diff {max_int_diff}", {"max_int_diff": max_int_diff}
            return True, "PASS_INTEGER_EXACT", {"max_int_diff": 0}

        # 4. NUMERICALLY_EQUIVALENT Policy: |cand - ref| <= atol + rtol * |ref|
        if self.exactness_class == ExactnessClass.NUMERICALLY_EQUIVALENT:
            # Handle non-finite values (NaN / Inf) explicitly
            if np.isnan(cand).any() or np.isnan(ref).any():
                nan_cand = np.isnan(cand)
                nan_ref = np.isnan(ref)
                if not np.array_equal(nan_cand, nan_ref):
                    return False, "FAIL_UNMATCHED_NAN_VALUES", {"nan_error": 1.0}
            if np.isinf(cand).any() or np.isinf(ref).any():
                inf_cand = np.isinf(cand)
                inf_ref = np.isinf(ref)
                if not np.array_equal(inf_cand, inf_ref):
                    return False, "FAIL_UNMATCHED_INF_VALUES", {"inf_error": 1.0}

            # Evaluate standard IEEE formula
            abs_diff = np.abs(cand - ref)
            abs_ref = np.abs(ref)
            tolerance_threshold = self.atol + self.rtol * abs_ref
            mask = abs_diff <= tolerance_threshold

            if not np.all(mask):
                max_violation = float(np.max(abs_diff - tolerance_threshold))
                max_abs_err = float(np.max(abs_diff))
                denom = np.where(abs_ref == 0.0, 1.0, abs_ref)
                max_rel_err = float(np.max(abs_diff / denom))
                return False, f"FAIL_NUMERICAL_TOLERANCE_EXCEEDED: max_abs={max_abs_err:.3e}, max_rel={max_rel_err:.3e}", {
                    "max_abs_err": max_abs_err,
                    "max_rel_err": max_rel_err,
                    "max_violation": max_violation,
                }

            max_abs = float(np.max(abs_diff)) if abs_diff.size > 0 else 0.0
            denom = np.where(abs_ref == 0.0, 1.0, abs_ref)
            max_rel = float(np.max(abs_diff / denom)) if abs_diff.size > 0 else 0.0
            return True, "PASS_NUMERICALLY_EQUIVALENT", {
                "max_abs_err": max_abs,
                "max_rel_err": max_rel,
                "atol": self.atol,
                "rtol": self.rtol,
            }

        # 5. SEMANTICALLY_EQUIVALENT Policy
        if self.exactness_class == ExactnessClass.SEMANTICALLY_EQUIVALENT:
            # Custom semantic check
            norm_c = float(np.linalg.norm(cand.ravel()))
            norm_r = float(np.linalg.norm(ref.ravel()))
            if norm_c == 0.0 and norm_r == 0.0:
                cos_sim = 1.0
            elif norm_c == 0.0 or norm_r == 0.0:
                cos_sim = 0.0
            else:
                cos_sim = float(np.dot(cand.ravel(), ref.ravel()) / (norm_c * norm_r))
            passed = cos_sim >= (1.0 - self.rtol)
            return passed, "PASS_SEMANTICALLY_EQUIVALENT" if passed else "FAIL_SEMANTIC_SIMILARITY", {"cosine_similarity": cos_sim}

        return False, "FAIL_UNKNOWN_EXACTNESS_CLASS", {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "name": self.name,
            "version": self.version,
            "mathematical_contract": self.mathematical_contract,
            "input_schemas": {k: v.to_dict() for k, v in self.input_schemas.items()},
            "output_schema": self.output_schema.to_dict() if self.output_schema else None,
            "exactness_class": self.exactness_class.value,
            "atol": self.atol,
            "rtol": self.rtol,
            "determinism_required": self.determinism_required,
            "reference_impl_id": self.reference_impl_id,
            "candidate_impl_id": self.candidate_impl_id,
            "required_edge_cases": self.required_edge_cases,
            "required_adversarial_cases": self.required_adversarial_cases,
            "timeout_ms": self.timeout_ms,
            "memory_budget_mb": self.memory_budget_mb,
            "supported_backends": self.supported_backends,
            "expected_fallback_backend": self.expected_fallback_backend,
            "verification_status": self.verification_status,
            "evidence_links": self.evidence_links,
        }


class CanonicalWorkloadRegistry:
    """
    Authoritative Singleton Registry for the Canonical 15 Workloads.
    Rejects incomplete or contradictory contracts before registration.
    """

    def __init__(self) -> None:
        self._contracts: Dict[str, CanonicalWorkloadContract] = {}
        self._register_canonical_15()

    def register(self, contract: CanonicalWorkloadContract) -> None:
        """Validates contract completeness before accepting registration."""
        self._validate_contract_integrity(contract)
        self._contracts[contract.workload_id] = contract

    def get(self, workload_id: str) -> Optional[CanonicalWorkloadContract]:
        return self._contracts.get(workload_id)

    def get_contract(self, workload_id: str) -> Optional[CanonicalWorkloadContract]:
        return self._contracts.get(workload_id)

    def list_workloads(self) -> List[str]:
        return list(self._contracts.keys())

    def get_all_contracts(self) -> Dict[str, CanonicalWorkloadContract]:
        return dict(self._contracts)

    def _validate_contract_integrity(self, contract: CanonicalWorkloadContract) -> None:
        """Enforces that no contract can be registered if incomplete or contradictory."""
        if not contract.workload_id or not isinstance(contract.workload_id, str):
            raise ValueError("Contract must have a non-empty stable string workload_id")
        if not contract.name:
            raise ValueError(f"Contract '{contract.workload_id}' must specify a descriptive name")
        if not contract.mathematical_contract:
            raise ValueError(f"Contract '{contract.workload_id}' must specify a mathematical contract definition")
        if not contract.reference_impl_id:
            raise ValueError(f"Contract '{contract.workload_id}' must designate an independent reference implementation")
        if not contract.candidate_impl_id:
            raise ValueError(f"Contract '{contract.workload_id}' must designate an independent candidate implementation")
        if contract.exactness_class == ExactnessClass.BIT_EXACT and (contract.atol != 0.0 or contract.rtol != 0.0):
            # Contradiction: BIT_EXACT cannot specify non-zero floating-point tolerance
            raise ValueError(f"Contradictory contract '{contract.workload_id}': BIT_EXACT cannot declare non-zero tolerance")
        if len(contract.required_edge_cases) == 0:
            raise ValueError(f"Contract '{contract.workload_id}' must specify mandatory edge cases")
        if len(contract.required_adversarial_cases) == 0:
            raise ValueError(f"Contract '{contract.workload_id}' must specify mandatory adversarial cases")

    def _register_canonical_15(self) -> None:
        """Registers the 15 canonical, authoritative workload contracts."""

        # 1. GEMM_STANDARD
        self.register(CanonicalWorkloadContract(
            workload_id="GEMM_STANDARD",
            name="Dense Matrix Multiplication (GEMM)",
            mathematical_contract="C = A @ B, where A in R^{M x K}, B in R^{K x N}, C in R^{M x N}",
            input_schemas={
                "A": TensorSchema(name="A", shape=(128, 128), dtype="float32"),
                "B": TensorSchema(name="B", shape=(128, 128), dtype="float32"),
            },
            output_schema=TensorSchema(name="C", shape=(128, 128), dtype="float32"),
            exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
            atol=1e-4,
            rtol=1e-4,
            reference_impl_id="ref_textbook_gemm_naive",
            candidate_impl_id="cand_cpce_tiled_blas_gemm",
            required_edge_cases=["zero_matrix_B", "identity_matrix_B", "single_element_1x1"],
            required_adversarial_cases=["prime_dims_37x41x47", "ill_conditioned_hilbert", "extreme_magnitudes"],
            timeout_ms=5000.0,
            memory_budget_mb=256.0,
            evidence_links=["benchmarks/hyper_omega_001_gemm.py"],
        ))

        # 2. CONV2D_STANDARD
        self.register(CanonicalWorkloadContract(
            workload_id="CONV2D_STANDARD",
            name="2D Spatial Direct Convolution",
            mathematical_contract="out[i, j] = sum_{ki, kj} image[i+ki, j+kj] * kernel[ki, kj]",
            input_schemas={
                "image": TensorSchema(name="image", shape=(64, 64), dtype="float32"),
                "kernel": TensorSchema(name="kernel", shape=(5, 5), dtype="float32"),
            },
            output_schema=TensorSchema(name="output", shape=(60, 60), dtype="float32"),
            exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
            atol=1e-4,
            rtol=1e-4,
            reference_impl_id="ref_direct_sliding_conv2d",
            candidate_impl_id="cand_winograd_fft_conv2d",
            required_edge_cases=["zero_kernel", "delta_impulse_kernel", "uniform_box_kernel"],
            required_adversarial_cases=["checkerboard_pattern", "high_frequency_noise", "subnormal_values"],
            timeout_ms=5000.0,
            memory_budget_mb=128.0,
            evidence_links=["hyper/research_engine/independent_reference.py"],
        ))

        # 3. FFT_STANDARD
        self.register(CanonicalWorkloadContract(
            workload_id="FFT_STANDARD",
            name="1D Discrete Fourier Transform (1024-Point)",
            mathematical_contract="X[k] = sum_{n=0}^{N-1} x[n] * exp(-2*pi*i*k*n / N)",
            input_schemas={
                "x": TensorSchema(name="x", shape=(1024,), dtype="complex64"),
            },
            output_schema=TensorSchema(name="output", shape=(1024,), dtype="complex64"),
            exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
            atol=1e-3,
            rtol=1e-3,
            reference_impl_id="ref_textbook_dft_matrix",
            candidate_impl_id="cand_radix2_cooley_tukey_fft",
            required_edge_cases=["dc_pure_constant", "nyquist_frequency", "dirac_delta_at_zero"],
            required_adversarial_cases=["random_phase_gaussian", "pure_imaginary_chirp", "near_zero_signal"],
            timeout_ms=5000.0,
            memory_budget_mb=128.0,
            evidence_links=["hyper/research_engine/independent_reference.py"],
        ))

        # 4. REDUCTION_SUM
        self.register(CanonicalWorkloadContract(
            workload_id="REDUCTION_SUM",
            name="Vector Sum Reduction (100,000 Elements)",
            mathematical_contract="scalar = sum_{i=0}^{N-1} x[i] via pairwise compensated accumulation",
            input_schemas={
                "x": TensorSchema(name="x", shape=(100000,), dtype="float32"),
            },
            output_schema=TensorSchema(name="scalar", shape=(), dtype="float32"),
            exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
            atol=1e-3,
            rtol=1e-3,
            reference_impl_id="ref_kahan_compensated_sum",
            candidate_impl_id="cand_avx2_pairwise_simd_reduction",
            required_edge_cases=["all_zeros", "all_ones", "alternating_positive_negative_ones"],
            required_adversarial_cases=["large_swamping_plus_eps", "denormal_floats", "sorted_descending_magnitudes"],
            timeout_ms=3000.0,
            memory_budget_mb=64.0,
            evidence_links=["hyper/research_engine/independent_reference.py"],
        ))

        # 5. SORT_STANDARD
        self.register(CanonicalWorkloadContract(
            workload_id="SORT_STANDARD",
            name="Vector Sorting (10,000 Float32 Elements)",
            mathematical_contract="out = sorted_permutation(x) where out[i] <= out[i+1] for all i",
            input_schemas={
                "x": TensorSchema(name="x", shape=(10000,), dtype="float32"),
            },
            output_schema=TensorSchema(name="output", shape=(10000,), dtype="float32"),
            exactness_class=ExactnessClass.BIT_EXACT,
            atol=0.0,
            rtol=0.0,
            reference_impl_id="ref_stable_merge_sort",
            candidate_impl_id="cand_hybrid_radix_timsort",
            required_edge_cases=["already_sorted", "reverse_sorted", "all_identical_values"],
            required_adversarial_cases=["pipe_organ_sawtooth", "plateau_with_repeated_keys", "pseudorandom_uniform"],
            timeout_ms=5000.0,
            memory_budget_mb=64.0,
            evidence_links=["hyper/research_engine/independent_reference.py"],
        ))

        # 6. PAGERANK_GRAPH
        self.register(CanonicalWorkloadContract(
            workload_id="PAGERANK_GRAPH",
            name="Iterative Graph PageRank (128-Node Adjacency)",
            mathematical_contract="v_{k+1} = (1-d)/N + d * (M @ v_k), where M is column-stochastic adjacency",
            input_schemas={
                "adj_matrix": TensorSchema(name="adj_matrix", shape=(128, 128), dtype="float32", min_value=0.0, max_value=1.0),
            },
            output_schema=TensorSchema(name="scores", shape=(128,), dtype="float32"),
            exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
            atol=1e-4,
            rtol=1e-4,
            reference_impl_id="ref_power_iteration_pagerank_naive",
            candidate_impl_id="cand_sparse_spmv_accelerated_pagerank",
            required_edge_cases=["star_graph_single_hub", "complete_graph_uniform_mesh", "disconnected_components"],
            required_adversarial_cases=["spider_trap_absorbing_cycle", "dangling_nodes_with_zero_outdegree", "bipartite_oscillator"],
            timeout_ms=5000.0,
            memory_budget_mb=128.0,
            evidence_links=["hyper/research_engine/independent_reference.py"],
        ))

        # 7. SHA256_CRYPTO
        self.register(CanonicalWorkloadContract(
            workload_id="SHA256_CRYPTO",
            name="Cryptographic SHA-256 Digest (FIPS 180-4)",
            mathematical_contract="digest = SHA256(data) returning standard 64-char lowercase hexadecimal string",
            input_schemas={
                "data": TensorSchema(name="data", dtype="bytes"),
            },
            output_schema=TensorSchema(name="digest", dtype="str"),
            exactness_class=ExactnessClass.BIT_EXACT,
            atol=0.0,
            rtol=0.0,
            reference_impl_id="ref_fips_180_4_standard_sha256",
            candidate_impl_id="cand_avx2_shani_accelerated_sha256",
            required_edge_cases=["empty_bytes", "single_null_byte", "exact_55_byte_block_boundary"],
            required_adversarial_cases=["exact_64_byte_block_boundary", "high_entropy_pseudorandom_1mb", "all_0xff_bytes"],
            timeout_ms=5000.0,
            memory_budget_mb=64.0,
            evidence_links=["hyper/research_engine/independent_reference.py"],
        ))

        # 8. NBODY_GRAVITATIONAL
        self.register(CanonicalWorkloadContract(
            workload_id="NBODY_GRAVITATIONAL",
            name="Gravitational Pairwise Step (256 Celestial Bodies)",
            mathematical_contract="pos_{t+dt} = pos_t + dt * (vel_t + dt * sum_{j!=i} G*m_j*(r_j - r_i)/|r_j - r_i|^3)",
            input_schemas={
                "positions": TensorSchema(name="positions", shape=(256, 3), dtype="float32"),
                "velocities": TensorSchema(name="velocities", shape=(256, 3), dtype="float32"),
                "masses": TensorSchema(name="masses", shape=(256,), dtype="float32", min_value=0.0),
            },
            output_schema=TensorSchema(name="positions_next", shape=(256, 3), dtype="float32"),
            exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
            atol=1e-3,
            rtol=1e-3,
            reference_impl_id="ref_o_n2_pairwise_nbody_gravity",
            candidate_impl_id="cand_barnes_hut_octree_nbody",
            required_edge_cases=["two_body_kepler_orbit", "zero_initial_velocities", "uniform_spherical_cluster"],
            required_adversarial_cases=["near_collision_singularity", "extreme_mass_disparity_1e6", "collinear_triple_encounter"],
            timeout_ms=5000.0,
            memory_budget_mb=128.0,
            evidence_links=["hyper/research_engine/independent_reference.py"],
        ))

        # 9. ML_MLP_INFERENCE
        self.register(CanonicalWorkloadContract(
            workload_id="ML_MLP_INFERENCE",
            name="Multi-Layer Perceptron Forward Inference",
            mathematical_contract="Y = ReLU(X @ W1 + b1) @ W2 + b2, where X in R^{64 x 128}, W1 in R^{128 x 64}, W2 in R^{64 x 64}",
            input_schemas={
                "X": TensorSchema(name="X", shape=(64, 128), dtype="float32"),
                "W1": TensorSchema(name="W1", shape=(128, 64), dtype="float32"),
                "b1": TensorSchema(name="b1", shape=(64,), dtype="float32"),
                "W2": TensorSchema(name="W2", shape=(64, 64), dtype="float32"),
                "b2": TensorSchema(name="b2", shape=(64,), dtype="float32"),
            },
            output_schema=TensorSchema(name="output", shape=(64, 64), dtype="float32"),
            exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
            atol=1e-4,
            rtol=1e-4,
            reference_impl_id="ref_two_layer_mlp_with_bias_relu",
            candidate_impl_id="cand_fused_gemm_bias_relu_mlp",
            required_edge_cases=["all_zero_inputs", "all_negative_preactivation_relu_clamp", "identity_weight_matrices"],
            required_adversarial_cases=["saturating_positive_magnitudes", "sparse_ternary_weights", "boundary_bias_offsets"],
            timeout_ms=5000.0,
            memory_budget_mb=128.0,
            evidence_links=["hyper/research_engine/independent_reference.py"],
        ))

        # 10. ATTENTION_HEAD
        self.register(CanonicalWorkloadContract(
            workload_id="ATTENTION_HEAD",
            name="Scaled Dot-Product Transformer Attention",
            mathematical_contract="Context = Softmax(Q @ K^T / sqrt(d_k)) @ V, with stable max-subtraction softmax",
            input_schemas={
                "Q": TensorSchema(name="Q", shape=(1, 32, 64), dtype="float32"),
                "K": TensorSchema(name="K", shape=(1, 32, 64), dtype="float32"),
                "V": TensorSchema(name="V", shape=(1, 32, 64), dtype="float32"),
            },
            output_schema=TensorSchema(name="context", shape=(1, 32, 64), dtype="float32"),
            exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
            atol=1e-4,
            rtol=1e-4,
            reference_impl_id="ref_textbook_scaled_dot_product_attention",
            candidate_impl_id="cand_tiled_flash_attention_avx2",
            required_edge_cases=["identity_qk_diagonal", "all_zero_query", "uniform_values"],
            required_adversarial_cases=["extreme_logits_softmax_overflow", "sparse_causal_mask", "vanishing_attention_weights"],
            timeout_ms=5000.0,
            memory_budget_mb=128.0,
            evidence_links=["hyper/research_engine/independent_reference.py"],
        ))

        # 11. SOBEL_FILTER
        self.register(CanonicalWorkloadContract(
            workload_id="SOBEL_FILTER",
            name="2D Spatial Sobel Gradient Edge Detection",
            mathematical_contract="G = sqrt( (image * Gx)^2 + (image * Gy)^2 ), where Gx, Gy are standard 3x3 Sobel kernels",
            input_schemas={
                "image": TensorSchema(name="image", shape=(128, 128), dtype="float32"),
            },
            output_schema=TensorSchema(name="gradient", shape=(126, 126), dtype="float32"),
            exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
            atol=1e-4,
            rtol=1e-4,
            reference_impl_id="ref_dual_separable_sobel_conv",
            candidate_impl_id="cand_fused_separable_simd_sobel",
            required_edge_cases=["constant_white_flat_image", "single_pixel_impulse", "horizontal_step_edge"],
            required_adversarial_cases=["high_frequency_checkerboard", "diagonal_ramp", "gaussian_noise_image"],
            timeout_ms=5000.0,
            memory_budget_mb=64.0,
            evidence_links=["hyper/research_engine/independent_reference.py"],
        ))

        # 12. STREAMING_VECTOR_OPS
        self.register(CanonicalWorkloadContract(
            workload_id="STREAMING_VECTOR_OPS",
            name="Streaming Vector AXPY (1,000,000 Elements)",
            mathematical_contract="y_out[i] = alpha * x[i] + y[i] for all i in [0, N-1]",
            input_schemas={
                "x": TensorSchema(name="x", shape=(1000000,), dtype="float32"),
                "y": TensorSchema(name="y", shape=(1000000,), dtype="float32"),
            },
            output_schema=TensorSchema(name="y_out", shape=(1000000,), dtype="float32"),
            exactness_class=ExactnessClass.BIT_EXACT,
            atol=0.0,
            rtol=0.0,
            reference_impl_id="ref_standard_axpy_loop",
            candidate_impl_id="cand_avx2_fma_streaming_axpy",
            required_edge_cases=["alpha_is_zero", "alpha_is_one", "all_zero_inputs"],
            required_adversarial_cases=["subnormal_magnitudes", "alternating_signs_cancel", "non_contiguous_slices"],
            timeout_ms=5000.0,
            memory_budget_mb=128.0,
            evidence_links=["hyper/research_engine/independent_reference.py"],
        ))

        # 13. MANDELBROT_FRACTAL
        self.register(CanonicalWorkloadContract(
            workload_id="MANDELBROT_FRACTAL",
            name="Mandelbrot Fractal Escape Iterations (128x128)",
            mathematical_contract="iterations[r, c] = argmin_k (|z_k| > 2.0 or k == max_iter) where z_{k+1} = z_k^2 + c",
            input_schemas={
                "c_grid": TensorSchema(name="c_grid", shape=(128, 128), dtype="complex64"),
            },
            output_schema=TensorSchema(name="iterations", shape=(128, 128), dtype="int32"),
            exactness_class=ExactnessClass.INTEGER_EXACT,
            atol=0.0,
            rtol=0.0,
            reference_impl_id="ref_canonical_mandelbrot_loop",
            candidate_impl_id="cand_vectorized_early_exit_mandelbrot",
            required_edge_cases=["origin_zero_point", "point_outside_radius_two", "main_cardioid_interior"],
            required_adversarial_cases=["period_two_bulb_interior", "seahorse_valley_boundary", "filament_boundary_points"],
            timeout_ms=5000.0,
            memory_budget_mb=64.0,
            evidence_links=["hyper/research_engine/independent_reference.py"],
        ))

        # 14. SPMV_IRREGULAR_CSR
        self.register(CanonicalWorkloadContract(
            workload_id="SPMV_IRREGULAR_CSR",
            name="Irregular Sparse CSR Matrix-Vector Product",
            mathematical_contract="y[i] = sum_{p=indptr[i]}^{indptr[i+1]-1} data[p] * x[indices[p]]",
            input_schemas={
                "data": TensorSchema(name="data", shape=(2048,), dtype="float32"),
                "indices": TensorSchema(name="indices", shape=(2048,), dtype="int32"),
                "indptr": TensorSchema(name="indptr", shape=(129,), dtype="int32"),
                "x": TensorSchema(name="x", shape=(128,), dtype="float32"),
            },
            output_schema=TensorSchema(name="y", shape=(128,), dtype="float32"),
            exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
            atol=1e-4,
            rtol=1e-4,
            reference_impl_id="ref_canonical_csr_spmv_loop",
            candidate_impl_id="cand_segmented_scan_simd_spmv",
            required_edge_cases=["completely_empty_rows", "dense_single_row", "identity_diagonal_csr"],
            required_adversarial_cases=["power_law_degree_distribution", "unaligned_column_indices", "alternating_dense_empty_rows"],
            timeout_ms=5000.0,
            memory_budget_mb=64.0,
            evidence_links=["hyper/research_engine/independent_reference.py"],
        ))

        # 15. ADVERSARIAL_HILBERT_STRESS
        self.register(CanonicalWorkloadContract(
            workload_id="ADVERSARIAL_HILBERT_STRESS",
            name="Ill-Conditioned Hilbert Matrix Stress Test",
            mathematical_contract="C = H @ B, where H[i,j] = 1.0 / (i + j + 1) exhibits condition number > 1e12 in R^{32 x 32}",
            input_schemas={
                "A": TensorSchema(name="A", shape=(32, 32), dtype="float32"),
                "B": TensorSchema(name="B", shape=(32, 32), dtype="float32"),
            },
            output_schema=TensorSchema(name="C", shape=(32, 32), dtype="float32"),
            exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
            atol=1e-4,
            rtol=1e-4,
            reference_impl_id="ref_high_precision_quad_accum_gemm",
            candidate_impl_id="cand_svd_regularized_hilbert_solver",
            required_edge_cases=["identity_B_matrix", "zero_B_matrix", "canonical_hilbert_kernel"],
            required_adversarial_cases=["random_gaussian_B", "orthogonal_haar_B", "eigenvector_aligned_B"],
            timeout_ms=5000.0,
            memory_budget_mb=64.0,
            evidence_links=["hyper/research_engine/independent_reference.py"],
        ))


# Global Authoritative Instance
CANONICAL_REGISTRY = CanonicalWorkloadRegistry()
CANONICAL_15_WORKLOAD_IDS = list(CANONICAL_REGISTRY.list_workloads())
