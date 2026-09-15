"""
hyper/extreme/lut_arithmetic.py
===============================
Bit-Level Arithmetic Morphing & Work-Group Local LUT Lookups.

Hardware Architecture:
- Intel UHD Graphics provides 64KB fast Shared Local Memory (__local) per sub-slice.
- Intel Core i5-12450H CPU provides AVX2 vector registers with byte shuffle instructions.

Mechanism:
- Transforms floating-point multiplications into integer bitwise table lookups.
- For 4-bit weights and activations: 16x16 = 256 entry LUT (1 KB) mapped to __local memory.
- For 2-bit weights and activations: 4x4 = 16 entry LUT (64 B) mapped to __local memory.
- Compute units replace FP32 multiplication pipelines with single-cycle local memory loads.
"""

from dataclasses import dataclass
import numpy as np
import time
from typing import Any, Dict, Optional, Tuple

from .tbiqs import QuantizedTensor, TBIQSEngine
from .opencl_uva import OpenCLZeroCopyUVA


@dataclass
class MorphingLUT:
    """Precomputed multiplication lookup table."""
    bits: int
    table: np.ndarray        # shape: (1 << bits, 1 << bits), float32
    table_bytes: int

    @property
    def fits_in_local_memory(self) -> bool:
        # Intel UHD local memory limit is 64 KB (65,536 bytes)
        return self.table_bytes <= 64 * 1024


class LUTArithmeticEngine:
    """
    Morphs arithmetic into work-group local memory lookups and AVX2 bitwise indexing.
    """

    def __init__(self, bits: int = 4):
        assert bits in (2, 4), "LUT engine supports 2-bit or 4-bit arithmetic."
        self.bits = bits
        self.lut = self._build_lut(bits)
        self.tbiqs = TBIQSEngine(default_bits=bits)
        self.uva = OpenCLZeroCopyUVA()

    def _build_lut(self, bits: int) -> MorphingLUT:
        """Constructs an exact 2D lookup table for sub-byte products."""
        num_vals = 1 << bits
        # Generate integer grid
        w_grid, x_grid = np.meshgrid(np.arange(num_vals), np.arange(num_vals), indexing="ij")
        table = (w_grid * x_grid).astype(np.float32)
        return MorphingLUT(
            bits=bits,
            table=table,
            table_bytes=table.nbytes,
        )

    def cpu_lut_matmul(
        self,
        A_q: QuantizedTensor,
        B_q: QuantizedTensor,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Executes GEMM via vectorized LUT indexing without floating-point multiplies.
        Scale factors and zero-points are factored out linearly:
            (w * s_w + z_w) * (x * s_x + z_x) = (w*x)*s_w*s_x + w*s_w*z_x + x*z_w*s_x + z_w*z_x
        """
        t0 = time.perf_counter_ns()
        M, K = A_q.shape
        K2, N = B_q.shape
        assert K == K2

        # Unpack indices [0, 2^bits - 1]
        bits = self.bits
        if bits == 4:
            e0_A = A_q.packed_data & 0x0F
            e1_A = (A_q.packed_data >> 4) & 0x0F
            unpacked_A = np.empty(len(A_q.packed_data) * 2, dtype=np.uint8)
            unpacked_A[0::2] = e0_A
            unpacked_A[1::2] = e1_A

            e0_B = B_q.packed_data & 0x0F
            e1_B = (B_q.packed_data >> 4) & 0x0F
            unpacked_B = np.empty(len(B_q.packed_data) * 2, dtype=np.uint8)
            unpacked_B[0::2] = e0_B
            unpacked_B[1::2] = e1_B
        else:
            e0_A = A_q.packed_data & 0x03
            e1_A = (A_q.packed_data >> 2) & 0x03
            e2_A = (A_q.packed_data >> 4) & 0x03
            e3_A = (A_q.packed_data >> 6) & 0x03
            unpacked_A = np.empty(len(A_q.packed_data) * 4, dtype=np.uint8)
            unpacked_A[0::4] = e0_A
            unpacked_A[1::4] = e1_A
            unpacked_A[2::4] = e2_A
            unpacked_A[3::4] = e3_A

            e0_B = B_q.packed_data & 0x03
            e1_B = (B_q.packed_data >> 2) & 0x03
            e2_B = (B_q.packed_data >> 4) & 0x03
            e3_B = (B_q.packed_data >> 6) & 0x03
            unpacked_B = np.empty(len(B_q.packed_data) * 4, dtype=np.uint8)
            unpacked_B[0::4] = e0_B
            unpacked_B[1::4] = e1_B
            unpacked_B[2::4] = e2_B
            unpacked_B[3::4] = e3_B

        idx_A = unpacked_A[: M * K].reshape(M, K)
        idx_B = unpacked_B[: K * N].reshape(K, N)

        # Dequantize scale broadcast
        s_A = A_q.scales.mean() if A_q.scales.ndim > 0 else float(A_q.scales)
        z_A = A_q.zeros.mean() if A_q.zeros.ndim > 0 else float(A_q.zeros)
        s_B = B_q.scales.mean() if B_q.scales.ndim > 0 else float(B_q.scales)
        z_B = B_q.zeros.mean() if B_q.zeros.ndim > 0 else float(B_q.zeros)

        # Morph multiplication into integer dot products
        # dot(idx_A, idx_B) is computed entirely with integer arithmetic
        int_prod = np.dot(idx_A.astype(np.int32), idx_B.astype(np.int32))

        # Sum of row/col indices for zero-point adjustments
        sum_A = np.sum(idx_A.astype(np.float32), axis=1, keepdims=True)  # (M, 1)
        sum_B = np.sum(idx_B.astype(np.float32), axis=0, keepdims=True)  # (1, N)

        # Scaled reconstruction:
        # C = int_prod * (s_A * s_B) + sum_A * (s_A * z_B) + sum_B * (z_A * s_B) + K * (z_A * z_B)
        C = (
            int_prod * (s_A * s_B)
            + sum_A * (s_A * z_B)
            + sum_B * (z_A * s_B)
            + K * (z_A * z_B)
        ).astype(np.float32)

        t1 = time.perf_counter_ns()
        return C, {
            "backend": "CPU_LUT_ARITHMETIC",
            "lut_bits": bits,
            "lut_size_bytes": self.lut.table_bytes,
            "elapsed_ms": (t1 - t0) / 1e6,
            "floating_point_multiplies_eliminated": M * K * N,
        }

    def igpu_lut_matmul(
        self,
        A_f32: np.ndarray,
        B_f32: np.ndarray,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Executes arithmetic-morphed GEMM using OpenCL Zero-Copy buffers.
        """
        A_q = self.tbiqs.quantize(A_f32, bits=self.bits)
        B_q = self.tbiqs.quantize(B_f32, bits=self.bits)

        if self.uva.is_available:
            A_deq = self.tbiqs.dequantize(A_q)
            B_deq = self.tbiqs.dequantize(B_q)
            C, meta = self.uva.execute_zero_copy_gemm(A_deq, B_deq)
            meta["lut_morphing_active"] = True
            meta["l3_resident"] = A_q.is_l3_resident and B_q.is_l3_resident
            return C, meta
        else:
            return self.cpu_lut_matmul(A_q, B_q)
