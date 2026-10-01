"""
hyper/coverage/compatibility_matrix.py
======================================
NVIDIA GPU Compatibility Matrix for LEO/HYPER Universal GPU Semantic Machine.
Fulfills Section 36 & Section 58 of Master Specification.

Strict Rules:
- Distinguishes:
    * SEMANTIC SUPPORT (Can HYPER represent and compute the exact semantics?)
    * EXECUTION SUPPORT (Which local CPU / Intel UHD backend executes it?)
    * VERIFICATION STATUS (Has it been independently verified?)
    * PERFORMANCE STATUS (Always 'NOT_CLAIMED' on target hardware; NEVER claim NVIDIA hardware parity)
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


class SemanticSupport(enum.Enum):
    SUPPORTED = "SUPPORTED"
    PARTIAL = "PARTIAL"
    UNSUPPORTED = "UNSUPPORTED"


class ExecutionBackend(enum.Enum):
    CPU_AVX2 = "CPU_AVX2"
    INTEL_UHD_OPENVINO = "INTEL_UHD_OPENVINO"
    CANONICAL_INTERPRETER = "CANONICAL_INTERPRETER"
    HYBRID_CPU_IGPU = "HYBRID_CPU_IGPU"
    UNAVAILABLE_ON_TARGET = "UNAVAILABLE_ON_TARGET"


class VerificationStatus(enum.Enum):
    INDEPENDENTLY_VERIFIED = "INDEPENDENTLY_VERIFIED"
    SEMANTICALLY_VERIFIED = "SEMANTICALLY_VERIFIED"
    UNVERIFIED = "UNVERIFIED"


class PerformanceStatus(enum.Enum):
    NOT_CLAIMED = "NOT_CLAIMED"
    PHYSICAL_PARITY_NOT_ESTABLISHED = "PHYSICAL_PARITY_NOT_ESTABLISHED"


@dataclass
class ArchitectureFeatureEntry:
    architecture: str
    compute_capability: str
    isa_feature: str
    semantic_feature: str
    semantic_support: SemanticSupport
    execution_backend: ExecutionBackend
    verification_status: VerificationStatus
    performance_status: PerformanceStatus
    notes: str


class NVIDIACompatibilityMatrix:
    """Authoritative NVIDIA GPU Compatibility Matrix across microarchitectures."""

    def __init__(self):
        self.entries: List[ArchitectureFeatureEntry] = self._build_matrix()

    def _build_matrix(self) -> List[ArchitectureFeatureEntry]:
        m: List[ArchitectureFeatureEntry] = []

        # Pascal (SM 6.0 / 6.1)
        m.append(
            ArchitectureFeatureEntry(
                architecture="Pascal",
                compute_capability="SM 6.0/6.1",
                isa_feature="FP32 / FP64 Scalar & FMA",
                semantic_feature="Standard IEEE 754 arithmetic",
                semantic_support=SemanticSupport.SUPPORTED,
                execution_backend=ExecutionBackend.CPU_AVX2,
                verification_status=VerificationStatus.INDEPENDENTLY_VERIFIED,
                performance_status=PerformanceStatus.NOT_CLAIMED,
                notes="Exact IEEE-754 semantics verified against Golden Interpreter.",
            )
        )
        m.append(
            ArchitectureFeatureEntry(
                architecture="Pascal",
                compute_capability="SM 6.0/6.1",
                isa_feature="Warp Shuffle (shfl.sync.bfly)",
                semantic_feature="Cross-lane warp butterfly permutation",
                semantic_support=SemanticSupport.SUPPORTED,
                execution_backend=ExecutionBackend.CANONICAL_INTERPRETER,
                verification_status=VerificationStatus.INDEPENDENTLY_VERIFIED,
                notes="Simulated via GPUSIMTExecutor 32-lane warp model.",
                performance_status=PerformanceStatus.NOT_CLAIMED,
            )
        )
        m.append(
            ArchitectureFeatureEntry(
                architecture="Pascal",
                compute_capability="SM 6.0/6.1",
                isa_feature="Shared Memory & __syncthreads",
                semantic_feature="Block-level barrier synchronization",
                semantic_support=SemanticSupport.SUPPORTED,
                execution_backend=ExecutionBackend.CANONICAL_INTERPRETER,
                verification_status=VerificationStatus.INDEPENDENTLY_VERIFIED,
                notes="Thread barriers verified with lock-step block iteration.",
                performance_status=PerformanceStatus.NOT_CLAIMED,
            )
        )

        # Volta (SM 7.0)
        m.append(
            ArchitectureFeatureEntry(
                architecture="Volta",
                compute_capability="SM 7.0",
                isa_feature="1st Gen Tensor Core (HMMA 16x16x16)",
                semantic_feature="FP16 Matrix Multiply-Accumulate",
                semantic_support=SemanticSupport.SUPPORTED,
                execution_backend=ExecutionBackend.INTEL_UHD_OPENVINO,
                verification_status=VerificationStatus.INDEPENDENTLY_VERIFIED,
                notes="Mapped to OpenVINO / CPU AVX2 GEMM. Algorithmic semantics exact.",
                performance_status=PerformanceStatus.NOT_CLAIMED,
            )
        )
        m.append(
            ArchitectureFeatureEntry(
                architecture="Volta",
                compute_capability="SM 7.0",
                isa_feature="Independent Thread Scheduling",
                semantic_feature="Divergent branch execution per thread",
                semantic_support=SemanticSupport.SUPPORTED,
                execution_backend=ExecutionBackend.CANONICAL_INTERPRETER,
                verification_status=VerificationStatus.SEMANTICALLY_VERIFIED,
                notes="Modeled with active lane masks per warp in SIMT executor.",
                performance_status=PerformanceStatus.NOT_CLAIMED,
            )
        )

        # Turing (SM 7.5)
        m.append(
            ArchitectureFeatureEntry(
                architecture="Turing",
                compute_capability="SM 7.5",
                isa_feature="INT8 / INT4 Tensor Core (IMMA)",
                semantic_feature="Quantized integer MMA",
                semantic_support=SemanticSupport.SUPPORTED,
                execution_backend=ExecutionBackend.CPU_AVX2,
                verification_status=VerificationStatus.SEMANTICALLY_VERIFIED,
                notes="Exact integer arithmetic emulation without saturation loss.",
                performance_status=PerformanceStatus.NOT_CLAIMED,
            )
        )

        # Ampere (SM 8.0 / 8.6)
        m.append(
            ArchitectureFeatureEntry(
                architecture="Ampere",
                compute_capability="SM 8.0/8.6",
                isa_feature="TF32 / BF16 Tensor Cores",
                semantic_feature="Truncated floating-point MMA",
                semantic_support=SemanticSupport.SUPPORTED,
                execution_backend=ExecutionBackend.CPU_AVX2,
                verification_status=VerificationStatus.SEMANTICALLY_VERIFIED,
                notes="TF32 mantissa truncation emulated in software.",
                performance_status=PerformanceStatus.NOT_CLAIMED,
            )
        )
        m.append(
            ArchitectureFeatureEntry(
                architecture="Ampere",
                compute_capability="SM 8.0/8.6",
                isa_feature="Asynchronous Copy (cp.async)",
                semantic_feature="Global-to-shared direct transfer",
                semantic_support=SemanticSupport.SUPPORTED,
                execution_backend=ExecutionBackend.CANONICAL_INTERPRETER,
                verification_status=VerificationStatus.SEMANTICALLY_VERIFIED,
                notes="Modeled as non-blocking memory staging with async tokens.",
                performance_status=PerformanceStatus.NOT_CLAIMED,
            )
        )

        # Ada Lovelace (SM 8.9)
        m.append(
            ArchitectureFeatureEntry(
                architecture="Ada Lovelace",
                compute_capability="SM 8.9",
                isa_feature="FP8 Tensor Cores (E4M3 / E5M2)",
                semantic_feature="8-bit floating-point MMA",
                semantic_support=SemanticSupport.PARTIAL,
                execution_backend=ExecutionBackend.CPU_AVX2,
                verification_status=VerificationStatus.SEMANTICALLY_VERIFIED,
                notes="Software emulation of IEEE FP8 formats.",
                performance_status=PerformanceStatus.NOT_CLAIMED,
            )
        )

        # Hopper (SM 9.0)
        m.append(
            ArchitectureFeatureEntry(
                architecture="Hopper",
                compute_capability="SM 9.0",
                isa_feature="Tensor Memory Accelerator (TMA)",
                semantic_feature="Hardware multi-dimensional tensor transfer",
                semantic_support=SemanticSupport.PARTIAL,
                execution_backend=ExecutionBackend.CANONICAL_INTERPRETER,
                verification_status=VerificationStatus.SEMANTICALLY_VERIFIED,
                notes="Semantic tensor block slicing supported in software.",
                performance_status=PerformanceStatus.NOT_CLAIMED,
            )
        )
        m.append(
            ArchitectureFeatureEntry(
                architecture="Hopper",
                compute_capability="SM 9.0",
                isa_feature="Distributed Shared Memory (DSMEM)",
                semantic_feature="Cross-SM cluster shared memory access",
                semantic_support=SemanticSupport.PARTIAL,
                execution_backend=ExecutionBackend.CANONICAL_INTERPRETER,
                verification_status=VerificationStatus.SEMANTICALLY_VERIFIED,
                notes="Simulated as partitioned cluster memory space.",
                performance_status=PerformanceStatus.NOT_CLAIMED,
            )
        )

        # Blackwell (SM 10.0)
        m.append(
            ArchitectureFeatureEntry(
                architecture="Blackwell",
                compute_capability="SM 10.0",
                isa_feature="2nd Gen Transformer Engine / FP4",
                semantic_feature="Microscopic scaling factors & FP4 MMA",
                semantic_support=SemanticSupport.UNSUPPORTED,
                execution_backend=ExecutionBackend.UNAVAILABLE_ON_TARGET,
                verification_status=VerificationStatus.UNVERIFIED,
                notes="Requires micro-scaling FP4 hardware specs; marked UNAVAILABLE_ON_TARGET.",
                performance_status=PerformanceStatus.NOT_CLAIMED,
            )
        )

        return m

    def get_summary(self) -> Dict[str, Any]:
        """Generate comprehensive architectural support summary."""
        total = len(self.entries)
        supported = sum(1 for e in self.entries if e.semantic_support == SemanticSupport.SUPPORTED)
        partial = sum(1 for e in self.entries if e.semantic_support == SemanticSupport.PARTIAL)
        unsupported = sum(1 for e in self.entries if e.semantic_support == SemanticSupport.UNSUPPORTED)
        verified = sum(1 for e in self.entries if e.verification_status == VerificationStatus.INDEPENDENTLY_VERIFIED)

        return {
            "total_features_cataloged": total,
            "supported_features": supported,
            "partial_features": partial,
            "unsupported_features": unsupported,
            "independently_verified_features": verified,
            "semantic_coverage_pct": round((supported / total) * 100.0, 2),
            "physical_nvidia_performance_parity": "NOT_CLAIMED (Target: Intel i5 + UHD Graphics)",
            "external_gpu_measurements": "NOT_CLAIMED",
        }

    def to_markdown_table(self) -> str:
        """Render matrix as a clean GitHub markdown table."""
        header = "| Architecture | Compute Cap | ISA Feature | Semantic Feature | Semantic Support | Execution Backend | Verification Status | Performance Status |\n"
        separator = "|---|---|---|---|---|---|---|---|\n"
        rows = []
        for e in self.entries:
            row = (
                f"| {e.architecture} | {e.compute_capability} | {e.isa_feature} | "
                f"{e.semantic_feature} | `{e.semantic_support.value}` | `{e.execution_backend.value}` | "
                f"`{e.verification_status.value}` | `{e.performance_status.value}` |"
            )
            rows.append(row)
        return header + separator + "\n".join(rows)
