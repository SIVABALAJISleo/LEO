"""
hyper_universal/adapters/adapter_registry.py
Universal Workload Adapter Framework & Provisional Contract Engine:
Bridges domain-specific workloads into formal UniversalContracts, ComputationalIR DAGs,
and executable reference pipelines across 9 major workload families.
Declares supported ops, accepted formats, unsupported constructs, and backend compatibility.
Provides provisional contract inference for undefined requests.
"""
from __future__ import annotations
import hashlib
import json
import math
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union
import numpy as np

from hyper_universal.contracts.contract_engine import (
    UniversalContract,
    ExactnessRequirement,
    NumericalTolerance,
    ResourceBudget,
    BackendTarget,
)
from hyper_universal.workload_ir.graph import ComputationalIR, OpKind


class WorkloadAdapter(ABC):
    """Abstract base adapter for computational workload families."""

    @abstractmethod
    def get_family_name(self) -> str:
        """Returns the canonical family identifier."""
        pass

    @abstractmethod
    def get_declaration(self) -> Dict[str, Any]:
        """
        Declares adapter specifications:
        - supported_operations
        - accepted_formats
        - unsupported_constructs
        - output_semantics
        - verification_method
        - backend_compatibility
        - resource_requirements
        """
        pass

    @abstractmethod
    def create_contract(
        self,
        workload_id: str,
        exactness: ExactnessRequirement = ExactnessRequirement.NUMERICALLY_EQUIVALENT,
        budget: Optional[ResourceBudget] = None,
    ) -> UniversalContract:
        """Creates formal UniversalContract for this workload family."""
        pass

    @abstractmethod
    def build_ir(self, workload_id: str, sample_input: Any) -> ComputationalIR:
        """Constructs ComputationalIR DAG for bottleneck analysis."""
        pass

    @abstractmethod
    def execute_reference(self, sample_input: Any) -> Any:
        """Executes unoptimized independent canonical reference implementation."""
        pass


class DenseLinearAlgebraAdapter(WorkloadAdapter):
    def get_family_name(self) -> str:
        return "DENSE_LINEAR_ALGEBRA"

    def get_declaration(self) -> Dict[str, Any]:
        return {
            "family": self.get_family_name(),
            "supported_operations": ["matmul", "transpose", "add", "gemm", "cholesky", "qr"],
            "accepted_formats": ["numpy.ndarray", "torch.Tensor", "float32", "float64", "float16"],
            "unsupported_constructs": ["complex128_matrix_inversion", "sparse_csr_without_dense_conversion"],
            "output_semantics": "2D/3D continuous memory matrix buffer",
            "verification_method": "Differential Frobenius norm & max absolute/relative tolerance",
            "backend_compatibility": ["CPU_AVX2", "INTEL_UHD_IGPU_OPENVINO", "HYBRID_CPU_IGPU"],
            "resource_requirements": {"min_ram_mb": 16, "supports_streaming": True},
        }

    def create_contract(
        self,
        workload_id: str,
        exactness: ExactnessRequirement = ExactnessRequirement.NUMERICALLY_EQUIVALENT,
        budget: Optional[ResourceBudget] = None,
    ) -> UniversalContract:
        return UniversalContract(
            workload_id=workload_id,
            family=self.get_family_name(),
            exactness=exactness,
            tolerances=NumericalTolerance(max_relative_error=1e-4, max_absolute_error=1e-4),
            budget=budget or ResourceBudget(max_ram_bytes=512 * 1024 * 1024, max_latency_ms=2000.0),
        )

    def build_ir(self, workload_id: str, sample_input: Tuple[np.ndarray, np.ndarray]) -> ComputationalIR:
        A, B = sample_input
        ir = ComputationalIR(name=workload_id)
        in_a = ir.add_input("A", A.shape, str(A.dtype))
        in_b = ir.add_input("B", B.shape, str(B.dtype))
        m, k = A.shape
        _, n = B.shape
        flops = 2 * m * k * n
        op = ir.add_op("matmul_out", OpKind.MATMUL, [in_a, in_b], (m, n), str(A.dtype), flops=flops)
        ir.mark_output(op)
        return ir

    def execute_reference(self, sample_input: Tuple[np.ndarray, np.ndarray]) -> np.ndarray:
        A, B = sample_input
        return A @ B


class SparseLinearAlgebraAdapter(WorkloadAdapter):
    def get_family_name(self) -> str:
        return "SPARSE_LINEAR_ALGEBRA"

    def get_declaration(self) -> Dict[str, Any]:
        return {
            "family": self.get_family_name(),
            "supported_operations": ["spmv", "sparse_dense_matmul", "sparse_transpose"],
            "accepted_formats": ["CSR", "COO", "dense_with_mask", "float32", "float64"],
            "unsupported_constructs": ["arbitrary_unstructured_hypergraph_reordering"],
            "output_semantics": "Dense vector or structured sparse matrix",
            "verification_method": "Differential vector comparison against dense reference",
            "backend_compatibility": ["CPU_AVX2", "CPU_STREAMING"],
            "resource_requirements": {"min_ram_mb": 8, "supports_streaming": True},
        }

    def create_contract(
        self,
        workload_id: str,
        exactness: ExactnessRequirement = ExactnessRequirement.NUMERICALLY_EQUIVALENT,
        budget: Optional[ResourceBudget] = None,
    ) -> UniversalContract:
        return UniversalContract(
            workload_id=workload_id,
            family=self.get_family_name(),
            exactness=exactness,
            tolerances=NumericalTolerance(max_relative_error=1e-5, max_absolute_error=1e-5),
            budget=budget or ResourceBudget(max_ram_bytes=256 * 1024 * 1024, max_latency_ms=1000.0),
        )

    def build_ir(self, workload_id: str, sample_input: Tuple[np.ndarray, np.ndarray]) -> ComputationalIR:
        A, x = sample_input
        ir = ComputationalIR(name=workload_id)
        in_a = ir.add_input("SparseMatrix", A.shape, str(A.dtype))
        in_x = ir.add_input("VectorX", x.shape, str(x.dtype))
        non_zeros = int(np.count_nonzero(A))
        flops = 2 * non_zeros
        op = ir.add_op("spmv_out", OpKind.MATMUL, [in_a, in_x], (A.shape[0],), str(x.dtype), flops=flops)
        ir.mark_output(op)
        return ir

    def execute_reference(self, sample_input: Tuple[np.ndarray, np.ndarray]) -> np.ndarray:
        A, x = sample_input
        return A @ x


class SpectralFFTAdapter(WorkloadAdapter):
    def get_family_name(self) -> str:
        return "SPECTRAL_FFT"

    def get_declaration(self) -> Dict[str, Any]:
        return {
            "family": self.get_family_name(),
            "supported_operations": ["fft1d", "rfft1d", "fft2d", "ifft", "stft"],
            "accepted_formats": ["numpy.ndarray", "complex64", "complex128", "float32"],
            "unsupported_constructs": ["non_equispaced_fft_nfft"],
            "output_semantics": "Complex frequency spectrum coefficients",
            "verification_method": "Spectral SNR (min 60 dB) & differential L2 norm",
            "backend_compatibility": ["CPU_AVX2", "INTEL_UHD_IGPU_OPENVINO"],
            "resource_requirements": {"min_ram_mb": 16, "supports_streaming": True},
        }

    def create_contract(
        self,
        workload_id: str,
        exactness: ExactnessRequirement = ExactnessRequirement.NUMERICALLY_EQUIVALENT,
        budget: Optional[ResourceBudget] = None,
    ) -> UniversalContract:
        return UniversalContract(
            workload_id=workload_id,
            family=self.get_family_name(),
            exactness=exactness,
            tolerances=NumericalTolerance(max_relative_error=1e-5, max_absolute_error=1e-5, min_snr_db=60.0),
            budget=budget or ResourceBudget(max_ram_bytes=128 * 1024 * 1024, max_latency_ms=500.0),
        )

    def build_ir(self, workload_id: str, sample_input: np.ndarray) -> ComputationalIR:
        ir = ComputationalIR(name=workload_id)
        in_sig = ir.add_input("signal", sample_input.shape, str(sample_input.dtype))
        n = len(sample_input)
        flops = int(5 * n * math.log2(max(n, 2)))
        op = ir.add_op("fft_out", OpKind.FFT, [in_sig], (n // 2 + 1,), "complex64", flops=flops)
        ir.mark_output(op)
        return ir

    def execute_reference(self, sample_input: np.ndarray) -> np.ndarray:
        return np.fft.rfft(sample_input)


class AIInferenceAdapter(WorkloadAdapter):
    def get_family_name(self) -> str:
        return "AI_INFERENCE"

    def get_declaration(self) -> Dict[str, Any]:
        return {
            "family": self.get_family_name(),
            "supported_operations": ["transformer_attention", "mlp_forward", "gelu", "layernorm", "softmax"],
            "accepted_formats": ["tensor [B, S, D]", "tensor [B, D]", "float32", "float16", "int8"],
            "unsupported_constructs": ["dynamic_recurrent_control_flow_with_side_effects"],
            "output_semantics": "Probability distribution or hidden state representation",
            "verification_method": "Top-1 token agreement & KL-divergence < 1e-4",
            "backend_compatibility": ["CPU_AVX2", "INTEL_UHD_IGPU_OPENVINO", "HYBRID_CPU_IGPU"],
            "resource_requirements": {"min_ram_mb": 64, "supports_streaming": True},
        }

    def create_contract(
        self,
        workload_id: str,
        exactness: ExactnessRequirement = ExactnessRequirement.NUMERICALLY_EQUIVALENT,
        budget: Optional[ResourceBudget] = None,
    ) -> UniversalContract:
        return UniversalContract(
            workload_id=workload_id,
            family=self.get_family_name(),
            exactness=exactness,
            tolerances=NumericalTolerance(max_relative_error=1e-4, max_absolute_error=1e-4),
            budget=budget or ResourceBudget(max_ram_bytes=1024 * 1024 * 1024, max_latency_ms=1000.0),
        )

    def build_ir(self, workload_id: str, sample_input: Tuple[np.ndarray, np.ndarray, np.ndarray]) -> ComputationalIR:
        q, k, v = sample_input
        ir = ComputationalIR(name=workload_id)
        iq = ir.add_input("Q", q.shape, str(q.dtype))
        ik = ir.add_input("K", k.shape, str(k.dtype))
        iv = ir.add_input("V", v.shape, str(v.dtype))
        n, d = q.shape
        flops = 4 * n * n * d
        attn_op = ir.add_op("attn_out", OpKind.CUSTOM, [iq, ik, iv], (n, d), str(q.dtype), flops=flops)
        ir.mark_output(attn_op)
        return ir

    def execute_reference(self, sample_input: Tuple[np.ndarray, np.ndarray, np.ndarray]) -> np.ndarray:
        q, k, v = sample_input
        d_k = q.shape[-1]
        scores = (q @ k.T) / math.sqrt(d_k)
        exp_s = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
        probs = exp_s / np.sum(exp_s, axis=-1, keepdims=True)
        return probs @ v


class ImageProcessingAdapter(WorkloadAdapter):
    def get_family_name(self) -> str:
        return "IMAGE_PROCESSING"

    def get_declaration(self) -> Dict[str, Any]:
        return {
            "family": self.get_family_name(),
            "supported_operations": ["conv2d_filter", "gaussian_blur", "sobel_gradient", "bilinear_resize"],
            "accepted_formats": ["image [H, W, C]", "image [H, W]", "uint8", "float32"],
            "unsupported_constructs": ["non_euclidean_mesh_projections"],
            "output_semantics": "Filtered 2D raster image buffer",
            "verification_method": "SSIM >= 0.98 & Peak Signal-to-Noise Ratio (PSNR)",
            "backend_compatibility": ["CPU_AVX2", "INTEL_UHD_IGPU_OPENVINO"],
            "resource_requirements": {"min_ram_mb": 32, "supports_streaming": True},
        }

    def create_contract(
        self,
        workload_id: str,
        exactness: ExactnessRequirement = ExactnessRequirement.APPLICATION_CONTRACT_EQUIVALENT,
        budget: Optional[ResourceBudget] = None,
    ) -> UniversalContract:
        return UniversalContract(
            workload_id=workload_id,
            family=self.get_family_name(),
            exactness=exactness,
            tolerances=NumericalTolerance(max_relative_error=1e-3, max_absolute_error=1e-3, min_ssim=0.98),
            budget=budget or ResourceBudget(max_ram_bytes=256 * 1024 * 1024, max_latency_ms=500.0),
        )

    def build_ir(self, workload_id: str, sample_input: np.ndarray) -> ComputationalIR:
        ir = ComputationalIR(name=workload_id)
        in_img = ir.add_input("image", sample_input.shape, str(sample_input.dtype))
        h, w = sample_input.shape[:2]
        flops = 9 * h * w
        op = ir.add_op("filter_out", OpKind.CONV2D, [in_img], sample_input.shape, str(sample_input.dtype), flops=flops)
        ir.mark_output(op)
        return ir

    def execute_reference(self, sample_input: np.ndarray) -> np.ndarray:
        # 3x3 Box filter software convolution
        h, w = sample_input.shape[:2]
        res = sample_input.copy()
        res[1:h-1, 1:w-1] = (
            sample_input[0:h-2, 1:w-1] + sample_input[2:h, 1:w-1] +
            sample_input[1:h-1, 0:w-2] + sample_input[1:h-1, 2:w] +
            sample_input[1:h-1, 1:w-1]
        ) / 5.0
        return res


class CompressionAdapter(WorkloadAdapter):
    def get_family_name(self) -> str:
        return "COMPRESSION"

    def get_declaration(self) -> Dict[str, Any]:
        return {
            "family": self.get_family_name(),
            "supported_operations": ["deflate", "lz4", "run_length", "quantized_packing"],
            "accepted_formats": ["bytes", "bytearray", "raw_buffer"],
            "unsupported_constructs": ["lossy_compression_on_bitwise_contracts"],
            "output_semantics": "Losslessly compressed byte array",
            "verification_method": "Bitwise exact byte reconstruction on decompression",
            "backend_compatibility": ["CPU_AVX2"],
            "resource_requirements": {"min_ram_mb": 16, "supports_streaming": True},
        }

    def create_contract(
        self,
        workload_id: str,
        exactness: ExactnessRequirement = ExactnessRequirement.BITWISE_EXACT,
        budget: Optional[ResourceBudget] = None,
    ) -> UniversalContract:
        return UniversalContract(
            workload_id=workload_id,
            family=self.get_family_name(),
            exactness=ExactnessRequirement.BITWISE_EXACT,
            tolerances=NumericalTolerance(max_relative_error=0.0, max_absolute_error=0.0),
            budget=budget or ResourceBudget(max_ram_bytes=128 * 1024 * 1024, max_latency_ms=500.0),
        )

    def build_ir(self, workload_id: str, sample_input: bytes) -> ComputationalIR:
        ir = ComputationalIR(name=workload_id)
        in_buf = ir.add_input("raw_bytes", (len(sample_input),), "uint8")
        op = ir.add_op("compressed", OpKind.CUSTOM, [in_buf], (len(sample_input),), "uint8", flops=len(sample_input))
        ir.mark_output(op)
        return ir

    def execute_reference(self, sample_input: bytes) -> bytes:
        import zlib
        return zlib.compress(sample_input, level=6)


class CryptographyAdapter(WorkloadAdapter):
    def get_family_name(self) -> str:
        return "CRYPTOGRAPHY"

    def get_declaration(self) -> Dict[str, Any]:
        return {
            "family": self.get_family_name(),
            "supported_operations": ["sha256", "hmac_sha256", "modular_exponentiation", "crc32"],
            "accepted_formats": ["bytes", "int", "hex_string"],
            "unsupported_constructs": ["quantum_vulnerable_broken_primitives"],
            "output_semantics": "Fixed-length deterministic cryptographic hash/digest",
            "verification_method": "Strict bitwise byte parity",
            "backend_compatibility": ["CPU_AVX2"],
            "resource_requirements": {"min_ram_mb": 8, "supports_streaming": True},
        }

    def create_contract(
        self,
        workload_id: str,
        exactness: ExactnessRequirement = ExactnessRequirement.BITWISE_EXACT,
        budget: Optional[ResourceBudget] = None,
    ) -> UniversalContract:
        return UniversalContract(
            workload_id=workload_id,
            family=self.get_family_name(),
            exactness=ExactnessRequirement.BITWISE_EXACT,
            tolerances=NumericalTolerance(max_relative_error=0.0, max_absolute_error=0.0),
            budget=budget or ResourceBudget(max_ram_bytes=64 * 1024 * 1024, max_latency_ms=200.0),
        )

    def build_ir(self, workload_id: str, sample_input: bytes) -> ComputationalIR:
        ir = ComputationalIR(name=workload_id)
        in_buf = ir.add_input("bytes_in", (len(sample_input),), "uint8")
        op = ir.add_op("digest_out", OpKind.CUSTOM, [in_buf], (32,), "uint8", flops=len(sample_input) * 64)
        ir.mark_output(op)
        return ir

    def execute_reference(self, sample_input: bytes) -> str:
        return hashlib.sha256(sample_input).hexdigest()


class PhysicsSimulationAdapter(WorkloadAdapter):
    def get_family_name(self) -> str:
        return "PHYSICS_SIMULATION"

    def get_declaration(self) -> Dict[str, Any]:
        return {
            "family": self.get_family_name(),
            "supported_operations": ["nbody_gravity", "verlet_integration", "wave_equation_finite_diff"],
            "accepted_formats": ["positions [N, 3]", "velocities [N, 3]", "masses [N]", "float32", "float64"],
            "unsupported_constructs": ["infinite_body_relativistic_spacetime_curvature"],
            "output_semantics": "Updated particle trajectories and energy conservation",
            "verification_method": "Symplectic energy conservation < 1e-4 drift & trajectory L2 diff",
            "backend_compatibility": ["CPU_AVX2", "INTEL_UHD_IGPU_OPENVINO"],
            "resource_requirements": {"min_ram_mb": 32, "supports_streaming": True},
        }

    def create_contract(
        self,
        workload_id: str,
        exactness: ExactnessRequirement = ExactnessRequirement.NUMERICALLY_EQUIVALENT,
        budget: Optional[ResourceBudget] = None,
    ) -> UniversalContract:
        return UniversalContract(
            workload_id=workload_id,
            family=self.get_family_name(),
            exactness=exactness,
            tolerances=NumericalTolerance(max_relative_error=1e-4, max_absolute_error=1e-4),
            budget=budget or ResourceBudget(max_ram_bytes=256 * 1024 * 1024, max_latency_ms=1000.0),
        )

    def build_ir(self, workload_id: str, sample_input: Tuple[np.ndarray, np.ndarray, float]) -> ComputationalIR:
        pos, vel, dt = sample_input
        ir = ComputationalIR(name=workload_id)
        ip = ir.add_input("pos", pos.shape, str(pos.dtype))
        iv = ir.add_input("vel", vel.shape, str(vel.dtype))
        n = pos.shape[0]
        flops = 12 * n * n
        op = ir.add_op("step_out", OpKind.CUSTOM, [ip, iv], pos.shape, str(pos.dtype), flops=flops)
        ir.mark_output(op)
        return ir

    def execute_reference(self, sample_input: Tuple[np.ndarray, np.ndarray, float]) -> Tuple[np.ndarray, np.ndarray]:
        pos, vel, dt = sample_input
        # Simple velocity-Verlet gravitational step with softening parameter
        n = pos.shape[0]
        acc = np.zeros_like(pos)
        eps = 1e-3
        for i in range(n):
            diff = pos - pos[i]
            dist_sq = np.sum(diff**2, axis=-1) + eps**2
            dist_inv3 = dist_sq**(-1.5)
            acc[i] = np.sum(diff * dist_inv3[:, None], axis=0)
        new_vel = vel + acc * dt
        new_pos = pos + new_vel * dt
        return new_pos, new_vel


class SortingAndAlgorithmsAdapter(WorkloadAdapter):
    def get_family_name(self) -> str:
        return "SORTING_AND_ALGORITHMS"

    def get_declaration(self) -> Dict[str, Any]:
        return {
            "family": self.get_family_name(),
            "supported_operations": ["radix_sort", "quicksort", "top_k_heap", "longest_common_subsequence"],
            "accepted_formats": ["1D int32 array", "1D float32 array", "strings"],
            "unsupported_constructs": ["infinite_stream_sorting_without_window"],
            "output_semantics": "Monotonically ordered array permutation",
            "verification_method": "Strict bitwise order monotonicity and multiset equivalence",
            "backend_compatibility": ["CPU_AVX2"],
            "resource_requirements": {"min_ram_mb": 32, "supports_streaming": True},
        }

    def create_contract(
        self,
        workload_id: str,
        exactness: ExactnessRequirement = ExactnessRequirement.BITWISE_EXACT,
        budget: Optional[ResourceBudget] = None,
    ) -> UniversalContract:
        return UniversalContract(
            workload_id=workload_id,
            family=self.get_family_name(),
            exactness=ExactnessRequirement.BITWISE_EXACT,
            tolerances=NumericalTolerance(max_relative_error=0.0, max_absolute_error=0.0),
            budget=budget or ResourceBudget(max_ram_bytes=256 * 1024 * 1024, max_latency_ms=1000.0),
        )

    def build_ir(self, workload_id: str, sample_input: np.ndarray) -> ComputationalIR:
        ir = ComputationalIR(name=workload_id)
        in_arr = ir.add_input("keys", sample_input.shape, str(sample_input.dtype))
        n = len(sample_input)
        flops = int(n * math.log2(max(n, 2)))
        op = ir.add_op("sorted", OpKind.SORT, [in_arr], sample_input.shape, str(sample_input.dtype), flops=flops)
        ir.mark_output(op)
        return ir

    def execute_reference(self, sample_input: np.ndarray) -> np.ndarray:
        return np.sort(sample_input)


class ProvisionalContractInferenceEngine:
    """
    Infers candidate observable behaviors and constructs provisional contracts
    when a workload request lacks a formal contract.
    Distinguishes inferred requirements from confirmed requirements.
    """

    @classmethod
    def infer_provisional_contract(
        cls,
        workload_id: str,
        candidate_func: Callable[[Any], Any],
        sample_input: Any,
        confirmed_requirements: Optional[Dict[str, Any]] = None,
    ) -> UniversalContract:
        confirmed = confirmed_requirements or {}

        # 1. Inspect Candidate Execution Observables
        try:
            sample_output = candidate_func(sample_input)
            exec_ok = True
        except Exception as e:
            sample_output = None
            exec_ok = False

        inferred_exactness = ExactnessRequirement.NUMERICALLY_EQUIVALENT
        inferred_rel_err = 1e-4
        inferred_abs_err = 1e-4

        # 2. Infer Exactness Requirements from Output Types
        if isinstance(sample_output, (bytes, bytearray)):
            inferred_exactness = ExactnessRequirement.BITWISE_EXACT
            inferred_rel_err = 0.0
            inferred_abs_err = 0.0
        elif isinstance(sample_output, np.ndarray):
            if np.issubdtype(sample_output.dtype, np.integer):
                inferred_exactness = ExactnessRequirement.EXACT_INTEGER_SYMBOLIC
                inferred_rel_err = 0.0
                inferred_abs_err = 0.0
            else:
                inferred_exactness = ExactnessRequirement.NUMERICALLY_EQUIVALENT
                inferred_rel_err = 1e-4
                inferred_abs_err = 1e-4

        # Override with confirmed requirements if explicitly provided
        final_exactness = confirmed.get("exactness", inferred_exactness)
        rel_tol = confirmed.get("max_relative_error", inferred_rel_err)
        abs_tol = confirmed.get("max_absolute_error", inferred_abs_err)

        contract = UniversalContract(
            workload_id=workload_id,
            family=confirmed.get("family", "INFERRED_PROVISIONAL"),
            description=f"Provisional contract inferred for {workload_id}",
            exactness=final_exactness,
            tolerances=NumericalTolerance(max_relative_error=rel_tol, max_absolute_error=abs_tol),
            budget=ResourceBudget(max_ram_bytes=512 * 1024 * 1024, max_latency_ms=2000.0),
        )

        return contract


class AdapterRegistry:
    """Central store managing workload family adapters with capability declarations."""

    def __init__(self):
        self._adapters: Dict[str, WorkloadAdapter] = {}
        self._register_default_adapters()

    def register(self, adapter: WorkloadAdapter) -> None:
        self._adapters[adapter.get_family_name()] = adapter

    def get_adapter(self, family_name: str) -> Optional[WorkloadAdapter]:
        return self._adapters.get(family_name)

    def list_supported_families(self) -> List[str]:
        return list(self._adapters.keys())

    def list_declarations(self) -> List[Dict[str, Any]]:
        return [adapter.get_declaration() for adapter in self._adapters.values()]

    def _register_default_adapters(self) -> None:
        self.register(DenseLinearAlgebraAdapter())
        self.register(SparseLinearAlgebraAdapter())
        self.register(SpectralFFTAdapter())
        self.register(AIInferenceAdapter())
        self.register(ImageProcessingAdapter())
        self.register(CompressionAdapter())
        self.register(CryptographyAdapter())
        self.register(PhysicsSimulationAdapter())
        self.register(SortingAndAlgorithmsAdapter())
