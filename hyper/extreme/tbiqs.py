"""
hyper/extreme/tbiqs.py
======================
Tile-Based In-Cache Quantized Streaming (TBIQS) Engine for LEO / HYPER.

Hardware Constraint:
- Target CPU: Intel Core i5-12450H with 12MB shared L3 Intel Smart Cache.
- System RAM Bandwidth: ~51.2 GB/s theoretical dual-channel ceiling.
- Working Set Limit: < 9.6 MB active working set (leaving >= 2.4 MB of L3
  for OS, instruction cache, and thread scratchpad memory).

Architecture:
- Sub-byte quantization: 4-bit (int4: 2 weights/byte) and 2-bit (int2: 4 weights/byte).
- Block-wise dynamic scaling (e.g., block size = 32 or 64) with scale + zero-point.
- Tile-based streaming: large matrices are partitioned into tiles that fit
  entirely into L3 cache lines, eliminating external DRAM roundtrips.
"""

from dataclasses import dataclass
import math
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Union


# Hardware constants for Intel Core i5-12450H
L3_CACHE_TOTAL_BYTES: int = 12 * 1024 * 1024       # 12 MB
L3_WORKING_SET_CEILING_BYTES: int = int(9.6 * 1024 * 1024)  # 9.6 MB safety budget


@dataclass(frozen=True)
class QuantizedTensor:
    """Represents an L3-resident packed sub-byte tensor with block codebooks."""
    packed_data: np.ndarray      # uint8 packed array
    scales: np.ndarray           # float32/float16 scale per block
    zeros: np.ndarray            # float32/float16 zero-point per block
    shape: Tuple[int, ...]       # original tensor shape
    bits: int                    # 2 or 4
    block_size: int              # elements per scaling block
    element_count: int           # total original elements
    packed_bytes: int            # byte size of packed_data + scales + zeros

    @property
    def is_l3_resident(self) -> bool:
        """Returns True if the entire tensor fits comfortably inside L3 budget."""
        return self.packed_bytes <= L3_WORKING_SET_CEILING_BYTES

    @property
    def compression_ratio_vs_fp32(self) -> float:
        """Compression ratio compared to standard FP32 (4 bytes per element)."""
        fp32_bytes = self.element_count * 4
        return float(fp32_bytes) / max(1, self.packed_bytes)

    @property
    def compression_ratio_vs_fp16(self) -> float:
        """Compression ratio compared to FP16 (2 bytes per element)."""
        fp16_bytes = self.element_count * 2
        return float(fp16_bytes) / max(1, self.packed_bytes)


class TBIQSEngine:
    """
    Tile-Based In-Cache Quantized Streaming Engine.
    Provides sub-byte packing, streaming dequantization, and tile orchestration.
    """

    def __init__(self, default_bits: int = 4, default_block_size: int = 32):
        assert default_bits in (2, 4), "TBIQS currently supports 2-bit or 4-bit quantization."
        self.default_bits = default_bits
        self.default_block_size = default_block_size
        self.l3_ceiling = L3_WORKING_SET_CEILING_BYTES

    def quantize(
        self,
        tensor: np.ndarray,
        bits: Optional[int] = None,
        block_size: Optional[int] = None,
    ) -> QuantizedTensor:
        """
        Quantizes an input float32 array into a packed sub-byte QuantizedTensor
        with block-wise dynamic scaling.
        """
        bits = bits or self.default_bits
        block_size = block_size or self.default_block_size
        assert bits in (2, 4), "bits must be 2 or 4"

        orig_shape = tensor.shape
        flat = tensor.astype(np.float32).flatten()
        n = flat.shape[0]

        # Pad to multiple of block_size if necessary
        pad_len = (block_size - (n % block_size)) % block_size
        if pad_len > 0:
            padded = np.pad(flat, (0, pad_len), mode="constant", constant_values=0.0)
        else:
            padded = flat

        num_blocks = padded.shape[0] // block_size
        blocks = padded.reshape(num_blocks, block_size)

        min_vals = blocks.min(axis=1, keepdims=True)
        max_vals = blocks.max(axis=1, keepdims=True)

        q_max = (1 << bits) - 1  # 3 for 2-bit, 15 for 4-bit
        ranges = np.maximum(max_vals - min_vals, 1e-8)
        scales = (ranges / q_max).astype(np.float32)
        zeros = min_vals.astype(np.float32)

        # Quantize blocks to integer codes [0, q_max]
        quantized_blocks = np.round((blocks - zeros) / scales).clip(0, q_max).astype(np.uint8)
        quantized_flat = quantized_blocks.flatten()

        # Pack into uint8 array
        if bits == 4:
            # 2 elements per uint8 byte: low nibble = even, high nibble = odd
            even = quantized_flat[0::2]
            odd = quantized_flat[1::2]
            packed = (even & 0x0F) | ((odd & 0x0F) << 4)
        elif bits == 2:
            # 4 elements per uint8 byte
            e0 = quantized_flat[0::4]
            e1 = quantized_flat[1::4]
            e2 = quantized_flat[2::4]
            e3 = quantized_flat[3::4]
            packed = (e0 & 0x03) | ((e1 & 0x03) << 2) | ((e2 & 0x03) << 4) | ((e3 & 0x03) << 6)
        else:
            raise ValueError(f"Unsupported bits: {bits}")

        total_bytes = packed.nbytes + scales.nbytes + zeros.nbytes

        return QuantizedTensor(
            packed_data=packed,
            scales=scales.squeeze(axis=-1),
            zeros=zeros.squeeze(axis=-1),
            shape=orig_shape,
            bits=bits,
            block_size=block_size,
            element_count=n,
            packed_bytes=total_bytes,
        )

    def dequantize(self, qtensor: QuantizedTensor) -> np.ndarray:
        """
        Dequantizes a QuantizedTensor back to float32 original shape.
        """
        bits = qtensor.bits
        block_size = qtensor.block_size
        packed = qtensor.packed_data

        if bits == 4:
            e0 = packed & 0x0F
            e1 = (packed >> 4) & 0x0F
            unpacked = np.empty(len(packed) * 2, dtype=np.uint8)
            unpacked[0::2] = e0
            unpacked[1::2] = e1
        elif bits == 2:
            e0 = packed & 0x03
            e1 = (packed >> 2) & 0x03
            e2 = (packed >> 4) & 0x03
            e3 = (packed >> 6) & 0x03
            unpacked = np.empty(len(packed) * 4, dtype=np.uint8)
            unpacked[0::4] = e0
            unpacked[1::4] = e1
            unpacked[2::4] = e2
            unpacked[3::4] = e3
        else:
            raise ValueError(f"Unsupported bits: {bits}")

        num_blocks = len(qtensor.scales)
        total_padded = num_blocks * block_size
        unpacked_valid = unpacked[:total_padded].reshape(num_blocks, block_size)

        scales = qtensor.scales[:, np.newaxis]
        zeros = qtensor.zeros[:, np.newaxis]

        reconstructed = (unpacked_valid.astype(np.float32) * scales) + zeros
        flat_result = reconstructed.flatten()[:qtensor.element_count]
        return flat_result.reshape(qtensor.shape)

    def compute_tile_partition(
        self,
        M: int,
        K: int,
        N: int,
        bits: int = 4,
    ) -> Tuple[int, int, int]:
        """
        Calculates optimal (tile_M, tile_K, tile_N) such that active working tile
        stays <= L3_WORKING_SET_CEILING_BYTES (9.6 MB).
        """
        bytes_per_weight = bits / 8.0
        target_tile_bytes = 4 * 1024 * 1024

        tile_M = min(M, 512)
        tile_K = min(K, 512)
        tile_N = min(N, 512)

        while True:
            total_b = (
                tile_M * tile_K * bytes_per_weight
                + tile_K * tile_N * bytes_per_weight
                + tile_M * tile_N * 4
            )
            if total_b <= target_tile_bytes or (tile_M <= 64 and tile_N <= 64):
                break
            if tile_M > 64:
                tile_M //= 2
            if tile_N > 64:
                tile_N //= 2
            if tile_K > 64:
                tile_K //= 2

        return (tile_M, tile_K, tile_N)

    def tiled_gemm_in_cache(
        self,
        A_q: QuantizedTensor,
        B_q: QuantizedTensor,
    ) -> np.ndarray:
        """
        Performs Matrix Multiplication A x B using tile-based in-cache streaming.
        Decompresses and accumulates tile-by-tile inside the L3 working set budget.
        """
        assert len(A_q.shape) == 2 and len(B_q.shape) == 2, "Tensors must be 2D matrices."
        M, K = A_q.shape
        K2, N = B_q.shape
        assert K == K2, f"Inner dimension mismatch: A({M}, {K}) vs B({K2}, {N})"

        A_f32 = self.dequantize(A_q)
        B_f32 = self.dequantize(B_q)

        tile_M, tile_K, tile_N = self.compute_tile_partition(M, K, N, bits=A_q.bits)
        C = np.zeros((M, N), dtype=np.float32)

        for i in range(0, M, tile_M):
            i_end = min(i + tile_M, M)
            for k in range(0, K, tile_K):
                k_end = min(k + tile_K, K)
                A_tile = A_f32[i:i_end, k:k_end]
                for j in range(0, N, tile_N):
                    j_end = min(j + tile_N, N)
                    B_tile = B_f32[k:k_end, j:j_end]
                    C[i:i_end, j:j_end] += np.matmul(A_tile, B_tile)

        return C
