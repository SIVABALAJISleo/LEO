"""
hyper/workloads/cuda_test_corpus.py
==================================
Progressive CUDA Workload Corpus for LEO/HYPER Universal GPU Semantic Machine.
Fulfills Section 37 of Master Specification.

Contains 19 progressively difficult GPU computational workloads:
 1. Hello Kernel (Scalar identity / copy)
 2. Vector Addition (Pointwise 1D SIMT)
 3. Matrix Multiplication (GEMM / Block Tiling)
 4. Parallel Reduction (Tree reduction with shared memory)
 5. Inclusive/Exclusive Scan (Prefix sum / Blelloch/Hillis-Steele)
 6. Histogram (Shared & Global Atomic Add)
 7. Convolution 1D/2D (Direct & Stencil halo exchange)
 8. Stencil (5-point 2D finite difference)
 9. Bitonic Sort (Parallel comparison networks)
10. Graph Traversal (Breadth-First Search / Frontiers)
11. Attention (Scaled Dot-Product Attention: Q @ K^T / sqrt(d) -> Softmax -> @ V)
12. Softmax (Safe Numerically Stable 2-pass/3-pass Softmax)
13. Fast Fourier Transform (Cooley-Tukey Radix-2 spectral transform)
14. Sparse Matrix-Vector Multiply (SpMV CSR format)
15. Global & Shared Atomics (AtomicAdd, AtomicCAS)
16. Cooperative Synchronization (Grid-wide barrier / block sync)
17. Dynamic Indexing (Indirect addressing & gathered loads)
18. Irregular Memory Access (Random index permutation / scatter-gather)
19. Multi-Kernel Pipelined Program (Fused Producer-Consumer Pipeline)
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper.universal_ir.opcodes import UniversalOpcode
from hyper.universal_ir.program import UniversalIRProgram, UniversalOp, UniversalType


@dataclass
class ProgressiveCUDAWorkload:
    id: int
    name: str
    difficulty_level: int  # 1 to 5
    contract: str
    cuda_source: str
    limitations: str
    input_generator: Callable[[], Dict[str, np.ndarray]]
    reference_fn: Callable[[Dict[str, np.ndarray]], np.ndarray]
    ir_builder: Callable[[], UniversalIRProgram]


class CUDATestCorpus:
    """Repository of 19 progressive CUDA workloads for rigorous semantic testing."""

    def __init__(self):
        self.workloads: List[ProgressiveCUDAWorkload] = self._build_corpus()

    def _build_corpus(self) -> List[ProgressiveCUDAWorkload]:
        wl: List[ProgressiveCUDAWorkload] = []

        # 1. Hello Kernel (Scalar Identity / Copy)
        def _wl1_inputs():
            return {"x": np.array([42.0], dtype=np.float32)}

        def _wl1_ref(inp):
            return inp["x"].copy()

        def _wl1_ir():
            prog = UniversalIRProgram("hello_kernel")
            prog.add_input("x", UniversalType.FLOAT32, (1,))
            prog.add_output("out", UniversalType.FLOAT32, (1,))
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.IDENTITY,
                    result_id="out",
                    result_type=UniversalType.FLOAT32,
                    operands=("x",),
                )
            )
            return prog

        wl.append(
            ProgressiveCUDAWorkload(
                id=1,
                name="hello_kernel",
                difficulty_level=1,
                contract="BITWISE_EXACT",
                cuda_source="__global__ void hello(const float* in, float* out) { *out = *in; }",
                limitations="Single scalar element, no parallelism.",
                input_generator=_wl1_inputs,
                reference_fn=_wl1_ref,
                ir_builder=_wl1_ir,
            )
        )

        # 2. Vector Addition
        def _wl2_inputs():
            rng = np.random.default_rng(42)
            return {
                "a": rng.standard_normal(128, dtype=np.float32),
                "b": rng.standard_normal(128, dtype=np.float32),
            }

        def _wl2_ref(inp):
            return inp["a"] + inp["b"]

        def _wl2_ir():
            prog = UniversalIRProgram("vector_add")
            prog.add_input("a", UniversalType.FLOAT32, (128,))
            prog.add_input("b", UniversalType.FLOAT32, (128,))
            prog.add_output("out", UniversalType.FLOAT32, (128,))
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.ADD,
                    result_id="out",
                    result_type=UniversalType.FLOAT32,
                    operands=("a", "b"),
                )
            )
            return prog

        wl.append(
            ProgressiveCUDAWorkload(
                id=2,
                name="vector_add",
                difficulty_level=1,
                contract="BITWISE_EXACT",
                cuda_source="__global__ void vecAdd(const float* a, const float* b, float* c, int n) {\n"
                            "  int i = blockIdx.x * blockDim.x + threadIdx.x;\n"
                            "  if (i < n) c[i] = a[i] + b[i];\n"
                            "}",
                limitations="Linear 1D memory access.",
                input_generator=_wl2_inputs,
                reference_fn=_wl2_ref,
                ir_builder=_wl2_ir,
            )
        )

        # 3. Matrix Multiplication (GEMM)
        def _wl3_inputs():
            rng = np.random.default_rng(43)
            return {
                "A": rng.standard_normal((16, 16), dtype=np.float32),
                "B": rng.standard_normal((16, 16), dtype=np.float32),
            }

        def _wl3_ref(inp):
            return inp["A"] @ inp["B"]

        def _wl3_ir():
            prog = UniversalIRProgram("matmul_gemm")
            prog.add_input("A", UniversalType.FLOAT32, (16, 16))
            prog.add_input("B", UniversalType.FLOAT32, (16, 16))
            prog.add_output("C", UniversalType.FLOAT32, (16, 16))
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.MATMUL,
                    result_id="C",
                    result_type=UniversalType.FLOAT32,
                    operands=("A", "B"),
                )
            )
            return prog

        wl.append(
            ProgressiveCUDAWorkload(
                id=3,
                name="matrix_multiplication",
                difficulty_level=2,
                contract="IEEE_SEMANTIC_EXACT",
                cuda_source="__global__ void gemm(const float* A, const float* B, float* C, int N) {\n"
                            "  int row = blockIdx.y * blockDim.y + threadIdx.y;\n"
                            "  int col = blockIdx.x * blockDim.x + threadIdx.x;\n"
                            "  if (row < N && col < N) {\n"
                            "    float acc = 0.0f;\n"
                            "    for (int k = 0; k < N; ++k) acc += A[row*N+k] * B[k*N+col];\n"
                            "    C[row*N+col] = acc;\n"
                            "  }\n"
                            "}",
                limitations="2D tiled access.",
                input_generator=_wl3_inputs,
                reference_fn=_wl3_ref,
                ir_builder=_wl3_ir,
            )
        )

        # 4. Parallel Reduction
        def _wl4_inputs():
            rng = np.random.default_rng(44)
            return {"x": rng.standard_normal((8, 16), dtype=np.float32)}

        def _wl4_ref(inp):
            return np.sum(inp["x"], axis=-1, keepdims=False)

        def _wl4_ir():
            prog = UniversalIRProgram("parallel_reduction")
            prog.add_input("x", UniversalType.FLOAT32, (8, 16))
            prog.add_output("out", UniversalType.FLOAT32, (8,))
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.REDUCE_SUM,
                    result_id="out",
                    result_type=UniversalType.FLOAT32,
                    operands=("x",),
                    attributes={"axis": -1},
                )
            )
            return prog

        wl.append(
            ProgressiveCUDAWorkload(
                id=4,
                name="parallel_reduction",
                difficulty_level=2,
                contract="IEEE_SEMANTIC_EXACT",
                cuda_source="__global__ void reduceSum(const float* g_in, float* g_out) {\n"
                            "  __shared__ float sdata[256];\n"
                            "  unsigned int tid = threadIdx.x;\n"
                            "  sdata[tid] = g_in[blockIdx.x * blockDim.x + tid];\n"
                            "  __syncthreads();\n"
                            "  for (unsigned int s = blockDim.x/2; s > 0; s >>= 1) {\n"
                            "    if (tid < s) sdata[tid] += sdata[tid + s];\n"
                            "    __syncthreads();\n"
                            "  }\n"
                            "  if (tid == 0) g_out[blockIdx.x] = sdata[0];\n"
                            "}",
                limitations="Tree reduction over shared memory.",
                input_generator=_wl4_inputs,
                reference_fn=_wl4_ref,
                ir_builder=_wl4_ir,
            )
        )

        # 5. Inclusive/Exclusive Scan (Prefix Sum)
        def _wl5_inputs():
            return {"x": np.arange(1, 17, dtype=np.float32)}

        def _wl5_ref(inp):
            return np.cumsum(inp["x"], dtype=np.float32)

        def _wl5_ir():
            # Scan represented as custom/scan opcode or sequential accumulation
            prog = UniversalIRProgram("parallel_scan")
            prog.add_input("x", UniversalType.FLOAT32, (16,))
            prog.add_output("out", UniversalType.FLOAT32, (16,))
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.CUSTOM,
                    result_id="out",
                    result_type=UniversalType.FLOAT32,
                    operands=("x",),
                    attributes={"sub_op": "PREFIX_SUM"},
                )
            )
            return prog

        wl.append(
            ProgressiveCUDAWorkload(
                id=5,
                name="parallel_scan",
                difficulty_level=3,
                contract="INTEGER_EXACT",
                cuda_source="// Blelloch Work-Efficient Parallel Scan\n"
                            "__global__ void blellochScan(float* d_out, float* d_in, int n);",
                limitations="Work-efficient parallel prefix tree.",
                input_generator=_wl5_inputs,
                reference_fn=_wl5_ref,
                ir_builder=_wl5_ir,
            )
        )

        # 6. Histogram (Shared & Global Atomic Add)
        def _wl6_inputs():
            rng = np.random.default_rng(45)
            vals = rng.integers(0, 10, size=100, dtype=np.int32)
            hist = np.zeros(10, dtype=np.int32)
            ones = np.ones(100, dtype=np.int32)
            return {"vals": vals, "hist": hist, "ones": ones}

        def _wl6_ref(inp):
            hist = np.zeros(10, dtype=np.int32)
            for v in inp["vals"]:
                hist[v] += 1
            return hist

        def _wl6_ir():
            prog = UniversalIRProgram("histogram_atomic")
            prog.add_input("vals", UniversalType.INT32, (100,))
            prog.add_input("hist", UniversalType.INT32, (10,))
            prog.add_input("ones", UniversalType.INT32, (100,))
            prog.add_output("out", UniversalType.INT32, (10,))
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.SCATTER_ADD,
                    result_id="out",
                    result_type=UniversalType.INT32,
                    operands=("hist", "vals", "ones"),
                )
            )
            return prog

        wl.append(
            ProgressiveCUDAWorkload(
                id=6,
                name="histogram_atomics",
                difficulty_level=3,
                contract="INTEGER_EXACT",
                cuda_source="__global__ void histo(const int* data, int* hist, int n) {\n"
                            "  int i = blockIdx.x * blockDim.x + threadIdx.x;\n"
                            "  if (i < n) atomicAdd(&(hist[data[i]]), 1);\n"
                            "}",
                limitations="Concurrent atomic collisions.",
                input_generator=_wl6_inputs,
                reference_fn=_wl6_ref,
                ir_builder=_wl6_ir,
            )
        )

        # 7. Convolution 2D
        def _wl7_inputs():
            rng = np.random.default_rng(46)
            return {
                "x": rng.standard_normal((1, 1, 8, 8), dtype=np.float32),
                "w": rng.standard_normal((1, 1, 3, 3), dtype=np.float32),
            }

        def _wl7_ref(inp):
            x = inp["x"][0, 0]
            w = inp["w"][0, 0]
            # Valid 2D correlation
            out = np.zeros((6, 6), dtype=np.float32)
            for r in range(6):
                for c in range(6):
                    out[r, c] = np.sum(x[r:r+3, c:c+3] * w)
            return out.reshape((1, 1, 6, 6))

        def _wl7_ir():
            prog = UniversalIRProgram("conv2d_workload")
            prog.add_input("x", UniversalType.FLOAT32, (1, 1, 8, 8))
            prog.add_input("w", UniversalType.FLOAT32, (1, 1, 3, 3))
            prog.add_output("out", UniversalType.FLOAT32, (1, 1, 6, 6))
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.CONV2D,
                    result_id="out",
                    result_type=UniversalType.FLOAT32,
                    operands=("x", "w"),
                    attributes={"padding": 0, "stride": 1},
                )
            )
            return prog

        wl.append(
            ProgressiveCUDAWorkload(
                id=7,
                name="convolution_2d",
                difficulty_level=3,
                contract="IEEE_SEMANTIC_EXACT",
                cuda_source="__global__ void conv2d(const float* img, const float* mask, float* out);",
                limitations="Sliding window boundary handling.",
                input_generator=_wl7_inputs,
                reference_fn=_wl7_ref,
                ir_builder=_wl7_ir,
            )
        )

        # 8. Stencil (5-point 2D finite difference)
        def _wl8_inputs():
            rng = np.random.default_rng(47)
            grid = rng.standard_normal((8, 8), dtype=np.float32)
            return {"grid": grid}

        def _wl8_ref(inp):
            g = inp["grid"]
            out = g.copy()
            # 5-point interior laplacian
            out[1:-1, 1:-1] = 0.25 * (g[0:-2, 1:-1] + g[2:, 1:-1] + g[1:-1, 0:-2] + g[1:-1, 2:])
            return out

        def _wl8_ir():
            prog = UniversalIRProgram("stencil_5point")
            prog.add_input("grid", UniversalType.FLOAT32, (8, 8))
            prog.add_output("out", UniversalType.FLOAT32, (8, 8))
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.CUSTOM,
                    result_id="out",
                    result_type=UniversalType.FLOAT32,
                    operands=("grid",),
                    attributes={"sub_op": "STENCIL_5POINT"},
                )
            )
            return prog

        wl.append(
            ProgressiveCUDAWorkload(
                id=8,
                name="stencil_5point",
                difficulty_level=3,
                contract="IEEE_SEMANTIC_EXACT",
                cuda_source="// 5-point 2D Stencil kernel with halo cells\n"
                            "__global__ void stencil2d(const float* in, float* out, int width, int height);",
                limitations="Halo exchange across blocks.",
                input_generator=_wl8_inputs,
                reference_fn=_wl8_ref,
                ir_builder=_wl8_ir,
            )
        )

        # 9. Bitonic Sort
        def _wl9_inputs():
            rng = np.random.default_rng(48)
            return {"x": rng.permutation(np.arange(16, dtype=np.int32))}

        def _wl9_ref(inp):
            return np.sort(inp["x"])

        def _wl9_ir():
            prog = UniversalIRProgram("bitonic_sort")
            prog.add_input("x", UniversalType.INT32, (16,))
            prog.add_output("out", UniversalType.INT32, (16,))
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.CUSTOM,
                    result_id="out",
                    result_type=UniversalType.INT32,
                    operands=("x",),
                    attributes={"sub_op": "BITONIC_SORT"},
                )
            )
            return prog

        wl.append(
            ProgressiveCUDAWorkload(
                id=9,
                name="bitonic_sort",
                difficulty_level=4,
                contract="INTEGER_EXACT",
                cuda_source="// Parallel bitonic sorting network\n"
                            "__global__ void bitonicSortStep(int* d_values, int j, int k);",
                limitations="Recursive comparator network.",
                input_generator=_wl9_inputs,
                reference_fn=_wl9_ref,
                ir_builder=_wl9_ir,
            )
        )

        # 10. Graph Traversal (BFS)
        def _wl10_inputs():
            # Adjacency matrix of 8-node graph and source node 0
            adj = np.zeros((8, 8), dtype=np.int32)
            adj[0, 1] = 1; adj[0, 2] = 1; adj[1, 3] = 1; adj[2, 4] = 1
            return {"adj": adj, "src": np.array([0], dtype=np.int32)}

        def _wl10_ref(inp):
            # Distance array from src 0
            dist = np.full(8, -1, dtype=np.int32)
            dist[0] = 0
            queue = [0]
            while queue:
                u = queue.pop(0)
                for v in range(8):
                    if inp["adj"][u, v] == 1 and dist[v] == -1:
                        dist[v] = dist[u] + 1
                        queue.append(v)
            return dist

        def _wl10_ir():
            prog = UniversalIRProgram("graph_bfs")
            prog.add_input("adj", UniversalType.INT32, (8, 8))
            prog.add_input("src", UniversalType.INT32, (1,))
            prog.add_output("dist", UniversalType.INT32, (8,))
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.CUSTOM,
                    result_id="dist",
                    result_type=UniversalType.INT32,
                    operands=("adj", "src"),
                    attributes={"sub_op": "GRAPH_BFS"},
                )
            )
            return prog

        wl.append(
            ProgressiveCUDAWorkload(
                id=10,
                name="graph_traversal_bfs",
                difficulty_level=4,
                contract="INTEGER_EXACT",
                cuda_source="// Breadth-first frontier graph search\n"
                            "__global__ void bfsKernel(int* va, int* ea, bool* frontier, bool* visited, int* cost);",
                limitations="Dynamic workload divergence per vertex degree.",
                input_generator=_wl10_inputs,
                reference_fn=_wl10_ref,
                ir_builder=_wl10_ir,
            )
        )

        # 11. Scaled Dot-Product Attention
        def _wl11_inputs():
            rng = np.random.default_rng(49)
            seq, dim = 8, 16
            return {
                "Q": rng.standard_normal((seq, dim), dtype=np.float32),
                "K": rng.standard_normal((seq, dim), dtype=np.float32),
                "V": rng.standard_normal((seq, dim), dtype=np.float32),
                "scale": np.array([4.0], dtype=np.float32),
            }

        def _wl11_ref(inp):
            Q, K, V = inp["Q"], inp["K"], inp["V"]
            d_k = Q.shape[-1]
            scores = (Q @ K.T) / np.sqrt(d_k)
            # Numerically stable softmax
            max_s = np.max(scores, axis=-1, keepdims=True)
            exp_s = np.exp(scores - max_s)
            weights = exp_s / np.sum(exp_s, axis=-1, keepdims=True)
            return weights @ V

        def _wl11_ir():
            prog = UniversalIRProgram("scaled_dot_product_attention")
            prog.add_input("Q", UniversalType.FLOAT32, (8, 16))
            prog.add_input("K", UniversalType.FLOAT32, (8, 16))
            prog.add_input("V", UniversalType.FLOAT32, (8, 16))
            prog.add_input("scale", UniversalType.FLOAT32, (1,))
            prog.add_output("out", UniversalType.FLOAT32, (8, 16))
            # Lowered into Q @ K^T -> scale -> softmax -> @ V
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.TRANSPOSE,
                    result_id="Kt",
                    result_type=UniversalType.FLOAT32,
                    operands=("K",),
                )
            )
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.MATMUL,
                    result_id="raw_scores",
                    result_type=UniversalType.FLOAT32,
                    operands=("Q", "Kt"),
                )
            )
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.DIV,
                    result_id="scores",
                    result_type=UniversalType.FLOAT32,
                    operands=("raw_scores", "scale"),
                )
            )
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.SOFTMAX,
                    result_id="weights",
                    result_type=UniversalType.FLOAT32,
                    operands=("scores",),
                )
            )
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.MATMUL,
                    result_id="out",
                    result_type=UniversalType.FLOAT32,
                    operands=("weights", "V"),
                )
            )
            return prog

        wl.append(
            ProgressiveCUDAWorkload(
                id=11,
                name="attention_mechanism",
                difficulty_level=4,
                contract="IEEE_SEMANTIC_EXACT",
                cuda_source="// FlashAttention / Scaled Dot-Product Attention\n"
                            "__global__ void scaledDotProductAttention(float* Q, float* K, float* V, float* O);",
                limitations="Fused online softmax tile reduction.",
                input_generator=_wl11_inputs,
                reference_fn=_wl11_ref,
                ir_builder=_wl11_ir,
            )
        )

        # 12. Softmax
        def _wl12_inputs():
            rng = np.random.default_rng(50)
            return {"x": rng.standard_normal((4, 16), dtype=np.float32)}

        def _wl12_ref(inp):
            x = inp["x"]
            e = np.exp(x - np.max(x, axis=-1, keepdims=True))
            return e / np.sum(e, axis=-1, keepdims=True)

        def _wl12_ir():
            prog = UniversalIRProgram("softmax_workload")
            prog.add_input("x", UniversalType.FLOAT32, (4, 16))
            prog.add_output("out", UniversalType.FLOAT32, (4, 16))
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.SOFTMAX,
                    result_id="out",
                    result_type=UniversalType.FLOAT32,
                    operands=("x",),
                )
            )
            return prog

        wl.append(
            ProgressiveCUDAWorkload(
                id=12,
                name="numerically_stable_softmax",
                difficulty_level=2,
                contract="IEEE_SEMANTIC_EXACT",
                cuda_source="__global__ void warpSoftmax(const float* x, float* y, int N);",
                limitations="Three-pass max-sub-exp-sum normalization.",
                input_generator=_wl12_inputs,
                reference_fn=_wl12_ref,
                ir_builder=_wl12_ir,
            )
        )

        # 13. Fast Fourier Transform (FFT)
        def _wl13_inputs():
            rng = np.random.default_rng(51)
            return {"x": rng.standard_normal(16, dtype=np.float32)}

        def _wl13_ref(inp):
            return np.fft.fft(inp["x"])

        def _wl13_ir():
            prog = UniversalIRProgram("fft_1d")
            prog.add_input("x", UniversalType.FLOAT32, (16,))
            prog.add_output("out", UniversalType.COMPLEX64, (16,))
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.FFT,
                    result_id="out",
                    result_type=UniversalType.COMPLEX64,
                    operands=("x",),
                )
            )
            return prog

        wl.append(
            ProgressiveCUDAWorkload(
                id=13,
                name="fast_fourier_transform",
                difficulty_level=4,
                contract="IEEE_SEMANTIC_EXACT",
                cuda_source="// Cooley-Tukey Radix-2 FFT\n"
                            "__global__ void radix2FFT(cuComplex* data, int n);",
                limitations="Butterfly twiddle factors & complex math.",
                input_generator=_wl13_inputs,
                reference_fn=_wl13_ref,
                ir_builder=_wl13_ir,
            )
        )

        # 14. SpMV (Sparse Matrix-Vector Multiply)
        def _wl14_inputs():
            # Diagonal matrix with few off-diagonals
            A = np.eye(8, dtype=np.float32)
            A[0, 2] = 2.0; A[3, 5] = 1.5
            x = np.arange(8, dtype=np.float32)
            return {"A": A, "x": x}

        def _wl14_ref(inp):
            return inp["A"] @ inp["x"]

        def _wl14_ir():
            prog = UniversalIRProgram("spmv_workload")
            prog.add_input("A", UniversalType.FLOAT32, (8, 8))
            prog.add_input("x", UniversalType.FLOAT32, (8,))
            prog.add_output("out", UniversalType.FLOAT32, (8,))
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.MATMUL,
                    result_id="out",
                    result_type=UniversalType.FLOAT32,
                    operands=("A", "x"),
                )
            )
            return prog

        wl.append(
            ProgressiveCUDAWorkload(
                id=14,
                name="sparse_matrix_vector",
                difficulty_level=3,
                contract="IEEE_SEMANTIC_EXACT",
                cuda_source="// CSR SpMV kernel\n"
                            "__global__ void spmvCSR(const int* row_ptr, const int* col_idx, const float* val, const float* x, float* y);",
                limitations="Irregular row length load imbalance.",
                input_generator=_wl14_inputs,
                reference_fn=_wl14_ref,
                ir_builder=_wl14_ir,
            )
        )

        # 15. Global & Shared Atomics
        def _wl15_inputs():
            return {"data": np.ones(32, dtype=np.int32), "acc": np.array([0], dtype=np.int32)}

        def _wl15_ref(inp):
            return np.array([np.sum(inp["data"])], dtype=np.int32)

        def _wl15_ir():
            prog = UniversalIRProgram("atomics_sum")
            prog.add_input("data", UniversalType.INT32, (32,))
            prog.add_input("acc", UniversalType.INT32, (1,))
            prog.add_output("out", UniversalType.INT32, (1,))
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.REDUCE_SUM,
                    result_id="out",
                    result_type=UniversalType.INT32,
                    operands=("data",),
                )
            )
            return prog

        wl.append(
            ProgressiveCUDAWorkload(
                id=15,
                name="atomic_accumulation",
                difficulty_level=3,
                contract="INTEGER_EXACT",
                cuda_source="__global__ void atomicAccum(const int* in, int* out) {\n"
                            "  int tid = threadIdx.x;\n"
                            "  atomicAdd(out, in[tid]);\n"
                            "}",
                limitations="Sequential consistency memory fence.",
                input_generator=_wl15_inputs,
                reference_fn=_wl15_ref,
                ir_builder=_wl15_ir,
            )
        )

        # 16. Cooperative Synchronization
        def _wl16_inputs():
            return {"x": np.ones(32, dtype=np.float32)}

        def _wl16_ref(inp):
            return inp["x"] * 2.0

        def _wl16_ir():
            prog = UniversalIRProgram("coop_sync")
            prog.add_input("x", UniversalType.FLOAT32, (32,))
            prog.add_output("out", UniversalType.FLOAT32, (32,))
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.BARRIER,
                    result_id="bar",
                    result_type=UniversalType.VOID,
                    operands=(),
                )
            )
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.ADD,
                    result_id="out",
                    result_type=UniversalType.FLOAT32,
                    operands=("x", "x"),
                )
            )
            return prog

        wl.append(
            ProgressiveCUDAWorkload(
                id=16,
                name="cooperative_grid_sync",
                difficulty_level=4,
                contract="BITWISE_EXACT",
                cuda_source="#include <cooperative_groups.h>\n"
                            "namespace cg = cooperative_groups;\n"
                            "__global__ void coopKernel(float* d) {\n"
                            "  cg::grid_group grid = cg::this_grid();\n"
                            "  grid.sync();\n"
                            "}",
                limitations="Grid-wide hardware residency requirement.",
                input_generator=_wl16_inputs,
                reference_fn=_wl16_ref,
                ir_builder=_wl16_ir,
            )
        )

        # 17. Dynamic Indexing (Indirect Gather)
        def _wl17_inputs():
            lut = np.array([10.0, 20.0, 30.0, 40.0], dtype=np.float32)
            idx = np.array([3, 1, 0, 2, 1, 3], dtype=np.int32)
            return {"lut": lut, "idx": idx}

        def _wl17_ref(inp):
            return inp["lut"][inp["idx"]]

        def _wl17_ir():
            prog = UniversalIRProgram("gather_lut")
            prog.add_input("lut", UniversalType.FLOAT32, (4,))
            prog.add_input("idx", UniversalType.INT32, (6,))
            prog.add_output("out", UniversalType.FLOAT32, (6,))
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.GATHER,
                    result_id="out",
                    result_type=UniversalType.FLOAT32,
                    operands=("lut", "idx"),
                )
            )
            return prog

        wl.append(
            ProgressiveCUDAWorkload(
                id=17,
                name="dynamic_indirect_gather",
                difficulty_level=2,
                contract="BITWISE_EXACT",
                cuda_source="__global__ void gatherLUT(const float* lut, const int* idx, float* out) {\n"
                            "  int i = threadIdx.x;\n"
                            "  out[i] = lut[idx[i]];\n"
                            "}",
                limitations="Non-contiguous memory lookups.",
                input_generator=_wl17_inputs,
                reference_fn=_wl17_ref,
                ir_builder=_wl17_ir,
            )
        )

        # 18. Irregular Memory Access (Scatter-Gather)
        def _wl18_inputs():
            data = np.arange(16, dtype=np.float32)
            perm = np.array([15, 0, 14, 1, 13, 2, 12, 3, 11, 4, 10, 5, 9, 6, 8, 7], dtype=np.int32)
            return {"data": data, "perm": perm}

        def _wl18_ref(inp):
            return inp["data"][inp["perm"]]

        def _wl18_ir():
            prog = UniversalIRProgram("irregular_permute")
            prog.add_input("data", UniversalType.FLOAT32, (16,))
            prog.add_input("perm", UniversalType.INT32, (16,))
            prog.add_output("out", UniversalType.FLOAT32, (16,))
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.GATHER,
                    result_id="out",
                    result_type=UniversalType.FLOAT32,
                    operands=("data", "perm"),
                )
            )
            return prog

        wl.append(
            ProgressiveCUDAWorkload(
                id=18,
                name="irregular_memory_access",
                difficulty_level=3,
                contract="BITWISE_EXACT",
                cuda_source="__global__ void irregularScatterGather(const float* in, const int* p, float* out) {\n"
                            "  int tid = threadIdx.x;\n"
                            "  out[tid] = in[p[tid]];\n"
                            "}",
                limitations="Divergent memory requests across warp lanes.",
                input_generator=_wl18_inputs,
                reference_fn=_wl18_ref,
                ir_builder=_wl18_ir,
            )
        )

        # 19. Multi-Kernel Pipelined Program
        def _wl19_inputs():
            rng = np.random.default_rng(52)
            return {
                "A": rng.standard_normal((8, 8), dtype=np.float32),
                "B": rng.standard_normal((8, 8), dtype=np.float32),
                "bias": rng.standard_normal(8, dtype=np.float32),
            }

        def _wl19_ref(inp):
            # Producer: GEMM -> Consumer: Bias Add -> Consumer 2: ReLU
            ab = inp["A"] @ inp["B"]
            biased = ab + inp["bias"]
            return np.maximum(biased, 0.0)

        def _wl19_ir():
            prog = UniversalIRProgram("pipelined_gemm_relu")
            prog.add_input("A", UniversalType.FLOAT32, (8, 8))
            prog.add_input("B", UniversalType.FLOAT32, (8, 8))
            prog.add_input("bias", UniversalType.FLOAT32, (8,))
            prog.add_output("out", UniversalType.FLOAT32, (8, 8))

            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.MATMUL,
                    result_id="ab",
                    result_type=UniversalType.FLOAT32,
                    operands=("A", "B"),
                )
            )
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.ADD,
                    result_id="biased",
                    result_type=UniversalType.FLOAT32,
                    operands=("ab", "bias"),
                )
            )
            prog.add_instruction(
                UniversalOp(
                    opcode=UniversalOpcode.RELU,
                    result_id="out",
                    result_type=UniversalType.FLOAT32,
                    operands=("biased",),
                )
            )
            return prog

        wl.append(
            ProgressiveCUDAWorkload(
                id=19,
                name="multi_kernel_pipeline",
                difficulty_level=3,
                contract="IEEE_SEMANTIC_EXACT",
                cuda_source="// Multi-kernel pipeline: kernel1 -> cudaStream -> kernel2\n"
                            "gemmKernel<<<grid1, block1, 0, s1>>>(d_A, d_B, d_AB);\n"
                            "biasReluKernel<<<grid2, block2, 0, s1>>>(d_AB, d_bias, d_out);",
                limitations="Inter-kernel stream synchronization.",
                input_generator=_wl19_inputs,
                reference_fn=_wl19_ref,
                ir_builder=_wl19_ir,
            )
        )

        return wl

    def get_all_workloads(self) -> List[ProgressiveCUDAWorkload]:
        return self.workloads
