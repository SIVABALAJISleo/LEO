"""
hyper/research_engine/vsa_bridge.py
===================================
Vector Symbolic Architecture (VSA) Bridge.

Bridges Python computational graphs to the native AVX2 VSA engine
(kernels/vsa/hyper_vsa_engine.hpp / cpp) on Intel Core i5 Golden Cove P-cores.
Provides high-performance bitwise algebraic shortcuts for dense matrix multiplications.
"""

from __future__ import annotations

import ctypes
import os
import platform
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple, Union

import numpy as np


class VSAEngine:
    """
    Vector Symbolic Architecture Engine.
    Replaces dense floating-point matrix multiplications with binary hyperdimensional
    projections, bitwise XOR binding, and vectorized population counts.
    """

    DIMENSION_BITS = 8192
    VEC256_COUNT = DIMENSION_BITS // 256  # 32 registers
    U32_COUNT = DIMENSION_BITS // 32       # 256 uint32 words

    _dll: Optional[ctypes.CDLL] = None
    _is_native: bool = False

    @classmethod
    def _init_native_backend(cls) -> bool:
        if cls._dll is not None:
            return cls._is_native

        dll_path = Path(__file__).resolve().parent.parent.parent / "kernels" / "vsa" / "hyper_vsa_native.dll"
        cpp_path = dll_path.with_suffix(".cpp")
        hpp_path = dll_path.with_suffix(".hpp")

        # Attempt to load existing DLL
        if dll_path.exists():
            try:
                cls._dll = ctypes.CDLL(str(dll_path))
                cls._bind_signatures()
                cls._is_native = True
                return True
            except Exception:
                pass

        # Attempt compilation if cl.exe or g++ is available on Windows
        if cpp_path.exists() and not dll_path.exists():
            try:
                # Try MSVC cl.exe
                compile_cmd = [
                    "cl.exe", "/O2", "/arch:AVX2", "/fp:fast", "/std:c++20",
                    "/LD", str(cpp_path), f"/Fe:{dll_path}"
                ]
                res = subprocess.run(compile_cmd, capture_output=True, text=True, cwd=str(dll_path.parent), timeout=15)
                if res.returncode == 0 and dll_path.exists():
                    cls._dll = ctypes.CDLL(str(dll_path))
                    cls._bind_signatures()
                    cls._is_native = True
                    return True
            except Exception:
                pass

        cls._is_native = False
        return False

    @classmethod
    def _bind_signatures(cls):
        if not cls._dll:
            return
        # vsa_pin_to_pcores()
        cls._dll.vsa_pin_to_pcores.argtypes = []
        cls._dll.vsa_pin_to_pcores.restype = None

        # vsa_project_fp32_to_binary(input, basis, in_dim, out_bits, output_bits)
        cls._dll.vsa_project_fp32_to_binary.argtypes = [
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        cls._dll.vsa_project_fp32_to_binary.restype = None

        # vsa_bind_avx2(a, b, out, num_words256)
        cls._dll.vsa_bind_avx2.argtypes = [
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
        ]
        cls._dll.vsa_bind_avx2.restype = None

        # vsa_hamming_distance_avx2(a, b, num_words256)
        cls._dll.vsa_hamming_distance_avx2.argtypes = [
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
        ]
        cls._dll.vsa_hamming_distance_avx2.restype = ctypes.c_uint32

        # vsa_gemm_surrogate_avx2(projected_input, binary_codebook, num_outputs, num_words256, output_similarities)
        cls._dll.vsa_gemm_surrogate_avx2.argtypes = [
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_float),
        ]
        cls._dll.vsa_gemm_surrogate_avx2.restype = None

    @classmethod
    def pin_to_pcores(cls):
        """Pins execution strictly to the 4 Golden Cove P-cores."""
        if cls._init_native_backend() and cls._dll:
            cls._dll.vsa_pin_to_pcores()

    @classmethod
    def generate_random_basis(cls, in_dim: int, out_bits: int = DIMENSION_BITS, seed: int = 42) -> np.ndarray:
        """Generates a fixed, deterministic Gaussian random projection basis matrix."""
        rng = np.random.default_rng(seed)
        basis = rng.standard_normal((out_bits, in_dim), dtype=np.float32)
        # Normalize each row
        norms = np.linalg.norm(basis, axis=1, keepdims=True) + 1e-12
        return (basis / norms).astype(np.float32)

    @classmethod
    def project(cls, x: np.ndarray, basis: np.ndarray) -> np.ndarray:
        """
        Projects a continuous FP32 vector x into an 8192-bit binary hypervector.
        Returns a uint32 array of shape [U32_COUNT].
        """
        x_flat = np.ascontiguousarray(x.flatten(), dtype=np.float32)
        in_dim = len(x_flat)
        out_bits = basis.shape[0]

        if cls._init_native_backend() and cls._dll:
            output_bits = np.zeros(out_bits // 32, dtype=np.uint32)
            cls._dll.vsa_project_fp32_to_binary(
                x_flat.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                basis.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                ctypes.c_size_t(in_dim),
                ctypes.c_size_t(out_bits),
                output_bits.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
            )
            return output_bits

        # Fast Vectorized Fallback: Dot product + sign bit packing
        projections = np.dot(basis, x_flat)
        binary_bits = (projections < 0.0).astype(np.uint8)
        # Pack 8 bits per byte, then view as uint32 aligned to 32-byte (256-bit AVX2) boundary
        packed_bytes = np.packbits(binary_bits, bitorder="little")
        rem = len(packed_bytes) % 32
        if rem != 0:
            packed_bytes = np.pad(packed_bytes, (0, 32 - rem), mode="constant")
        return packed_bytes.view(np.uint32)

    @classmethod
    def bind(cls, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Hypervector Symbolic Binding: A (XOR) B.
        Preserves quasi-orthogonality and is self-inverting.
        """
        if cls._init_native_backend() and cls._dll:
            out = np.zeros_like(a)
            cls._dll.vsa_bind_avx2(
                a.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                b.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                out.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                ctypes.c_size_t(len(a) // 8),
            )
            return out
        return np.bitwise_xor(a, b)

    @classmethod
    def hamming_distance(cls, a: np.ndarray, b: np.ndarray) -> int:
        """
        Computes the Hamming distance d_H(A, B) via parallel bitwise XOR popcount.
        """
        if cls._init_native_backend() and cls._dll:
            return int(cls._dll.vsa_hamming_distance_avx2(
                a.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                b.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                ctypes.c_size_t(len(a) // 8),
            ))
        xor_res = np.bitwise_xor(a, b)
        if len(xor_res) % 2 != 0:
            xor_res = np.pad(xor_res, (0, 1), mode="constant")
        u64_view = xor_res.view(np.uint64)
        total = 0
        for val in u64_view:
            total += int(val).bit_count()
        return total

    @classmethod
    def gemm_surrogate(
        cls,
        projected_input: np.ndarray,
        binary_codebook: np.ndarray,
    ) -> np.ndarray:
        """
        Dense Matrix Multiplication Surrogate:
        Computes cosine similarity predictions from Hamming distances.
        Y_k = 1 - 2 * (d_H(X, W_k) / D) ~ cos(X, W_k).
        """
        num_outputs = binary_codebook.shape[0]
        words_per_vec = binary_codebook.shape[1]
        num_words256 = words_per_vec // 8

        if cls._init_native_backend() and cls._dll:
            out_similarities = np.zeros(num_outputs, dtype=np.float32)
            cls._dll.vsa_gemm_surrogate_avx2(
                projected_input.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                binary_codebook.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                ctypes.c_size_t(num_outputs),
                ctypes.c_size_t(num_words256),
                out_similarities.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            )
            return out_similarities

        total_bits = float(words_per_vec * 32)
        out_sims = np.zeros(num_outputs, dtype=np.float32)
        for k in range(num_outputs):
            d_h = cls.hamming_distance(projected_input, binary_codebook[k])
            normalized_dist = float(d_h) / total_bits
            out_sims[k] = float(np.cos(np.pi * normalized_dist))
        return out_sims

    @classmethod
    def bundle(cls, vectors: List[np.ndarray]) -> np.ndarray:
        """
        Bundling (Superposition): Computes majority-rule consensus across k hypervectors.
        """
        k = len(vectors)
        if k == 0:
            return np.zeros(cls.U32_COUNT, dtype=np.uint32)
        if k == 1:
            return vectors[0].copy()

        # Bitwise consensus
        stacked = np.stack(vectors, axis=0)  # [k, U32_COUNT]
        # Unpack to bits for clean majority voting
        bytes_view = stacked.view(np.uint8)
        bits = np.unpackbits(bytes_view, axis=-1, bitorder="little")
        majority = (np.sum(bits, axis=0) > (k // 2)).astype(np.uint8)
        packed_bytes = np.packbits(majority, bitorder="little")
        rem = len(packed_bytes) % 4
        if rem != 0:
            packed_bytes = np.pad(packed_bytes, (0, 4 - rem), mode="constant")
        return packed_bytes.view(np.uint32)
