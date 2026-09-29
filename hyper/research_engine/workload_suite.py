"""
hyper/research_engine/workload_suite.py
=======================================
Required 15-Workload Canonical Suite, Dynamic Workload Generator, and Self-Challenge Engine.

Implements Sections 25, 43, 44, and 45:
1. Canonical 15-Workload Suite:
   - Matrix Multiplication, Convolution, FFT, Reduction, Sorting, Graph Processing,
     Cryptographic, Scientific, ML Inference, Transformer Attention, Image Processing,
     Memory-Bound, Compute-Bound, Irregular SpMV, Adversarial.
2. New Workload Generator: Synthesizes novel tensor expressions and dependency graphs.
3. Self-Challenge Engine: Autonomous generation of adversarial workloads targeting optimizer blindspots.
"""

from __future__ import annotations
import math
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper.research_engine.contracts import ProblemContract
from hyper.research_engine.exactness import ExactnessMode
from hyper.discovery.cir import CIRGraph, CIRNode, CIREdge, OpType, DataType


class Canonical15WorkloadSuite:
    """The formal, authoritative 15-workload benchmark suite required by the research protocol."""

    @classmethod
    def get_all_workload_contracts(cls) -> Dict[str, ProblemContract]:
        contracts = {
            # 1. Matrix Multiplication
            "GEMM_STANDARD": ProblemContract(
                workload_id="GEMM_STANDARD",
                description="Dense matrix multiplication C = A @ B (128x128 FP32)",
                input_domain={"A": {"shape": [128, 128], "dtype": "FP32"}, "B": {"shape": [128, 128], "dtype": "FP32"}},
                output_domain={"C": {"shape": [128, 128], "dtype": "FP32"}},
                exactness_mode=ExactnessMode.NUMERIC_TOLERANCE,
                tolerance_epsilon=1e-3,
            ),
            # 2. Convolution
            "CONV2D_STANDARD": ProblemContract(
                workload_id="CONV2D_STANDARD",
                description="2D spatial convolution of 64x64 image with 5x5 filter",
                input_domain={"image": {"shape": [64, 64], "dtype": "FP32"}, "kernel": {"shape": [5, 5], "dtype": "FP32"}},
                output_domain={"output": {"shape": [60, 60], "dtype": "FP32"}},
                exactness_mode=ExactnessMode.NUMERIC_TOLERANCE,
                tolerance_epsilon=1e-3,
            ),
            # 3. FFT
            "FFT_STANDARD": ProblemContract(
                workload_id="FFT_STANDARD",
                description="1D Discrete Fast Fourier Transform (1024 points)",
                input_domain={"x": {"shape": [1024], "dtype": "COMPLEX64"}},
                output_domain={"output": {"shape": [1024], "dtype": "COMPLEX64"}},
                exactness_mode=ExactnessMode.NUMERIC_TOLERANCE,
                tolerance_epsilon=1e-3,
            ),
            # 4. Reduction
            "REDUCTION_SUM": ProblemContract(
                workload_id="REDUCTION_SUM",
                description="High-throughput floating point sum reduction (100,000 elements)",
                input_domain={"x": {"shape": [100000], "dtype": "FP32"}},
                output_domain={"scalar": {"shape": [], "dtype": "FP32"}},
                exactness_mode=ExactnessMode.NUMERIC_TOLERANCE,
                tolerance_epsilon=1e-2,
            ),
            # 5. Sorting
            "SORT_STANDARD": ProblemContract(
                workload_id="SORT_STANDARD",
                description="Array element sorting (10,000 float32 elements)",
                input_domain={"x": {"shape": [10000], "dtype": "FP32"}},
                output_domain={"output": {"shape": [10000], "dtype": "FP32"}},
                exactness_mode=ExactnessMode.BIT_EXACT,
                tolerance_epsilon=0.0,
            ),
            # 6. Graph Processing
            "PAGERANK_GRAPH": ProblemContract(
                workload_id="PAGERANK_GRAPH",
                description="Iterative PageRank over 128-node directed adjacency graph",
                input_domain={"adj_matrix": {"shape": [128, 128], "dtype": "FP32"}},
                output_domain={"scores": {"shape": [128], "dtype": "FP32"}},
                exactness_mode=ExactnessMode.NUMERIC_TOLERANCE,
                tolerance_epsilon=1e-3,
            ),
            # 7. Cryptographic Computation
            "SHA256_CRYPTO": ProblemContract(
                workload_id="SHA256_CRYPTO",
                description="FIPS 180-4 SHA-256 hash over 1 MB payload",
                input_domain={"data": {"dtype": "BYTES"}},
                output_domain={"digest": {"dtype": "HEX_STRING"}},
                exactness_mode=ExactnessMode.BIT_EXACT,
                tolerance_epsilon=0.0,
            ),
            # 8. Scientific Computation
            "NBODY_GRAVITATIONAL": ProblemContract(
                workload_id="NBODY_GRAVITATIONAL",
                description="Gravitational pairwise simulation step for 256 celestial bodies",
                input_domain={
                    "positions": {"shape": [256, 3], "dtype": "FP32"},
                    "velocities": {"shape": [256, 3], "dtype": "FP32"},
                    "masses": {"shape": [256], "dtype": "FP32"},
                },
                output_domain={"positions_next": {"shape": [256, 3], "dtype": "FP32"}},
                exactness_mode=ExactnessMode.NUMERIC_TOLERANCE,
                tolerance_epsilon=1e-3,
            ),
            # 9. ML Inference
            "ML_MLP_INFERENCE": ProblemContract(
                workload_id="ML_MLP_INFERENCE",
                description="Multi-layer perceptron forward inference (Dense -> ReLU -> Dense)",
                input_domain={"A": {"shape": [64, 128], "dtype": "FP32"}, "B": {"shape": [128, 64], "dtype": "FP32"}},
                output_domain={"output": {"shape": [64, 64], "dtype": "FP32"}},
                exactness_mode=ExactnessMode.NUMERIC_TOLERANCE,
                tolerance_epsilon=1e-3,
            ),
            # 10. Transformer-Related Workload
            "ATTENTION_HEAD": ProblemContract(
                workload_id="ATTENTION_HEAD",
                description="Transformer Scaled Dot-Product Attention (Batch=1, Seq=32, HeadDim=64)",
                input_domain={
                    "Q": {"shape": [1, 32, 64], "dtype": "FP32"},
                    "K": {"shape": [1, 32, 64], "dtype": "FP32"},
                    "V": {"shape": [1, 32, 64], "dtype": "FP32"},
                },
                output_domain={"context": {"shape": [1, 32, 64], "dtype": "FP32"}},
                exactness_mode=ExactnessMode.NUMERIC_TOLERANCE,
                tolerance_epsilon=1e-3,
            ),
            # 11. Image Processing
            "SOBEL_FILTER": ProblemContract(
                workload_id="SOBEL_FILTER",
                description="Spatial gradient edge detection over 128x128 grayscale image",
                input_domain={"image": {"shape": [128, 128], "dtype": "FP32"}},
                output_domain={"gradient": {"shape": [126, 126], "dtype": "FP32"}},
                exactness_mode=ExactnessMode.NUMERIC_TOLERANCE,
                tolerance_epsilon=1e-3,
            ),
            # 12. Memory-Bound Workload
            "STREAMING_VECTOR_OPS": ProblemContract(
                workload_id="STREAMING_VECTOR_OPS",
                description="Memory-bandwidth limited sequential vector axpy operations (1,000,000 elements)",
                input_domain={"x": {"shape": [1000000], "dtype": "FP32"}},
                output_domain={"y": {"shape": [1000000], "dtype": "FP32"}},
                exactness_mode=ExactnessMode.BIT_EXACT,
                tolerance_epsilon=0.0,
            ),
            # 13. Compute-Bound Workload
            "MANDELBROT_FRACTAL": ProblemContract(
                workload_id="MANDELBROT_FRACTAL",
                description="Compute-bound iterative divergence count over 128x128 complex grid",
                input_domain={"c_grid": {"shape": [128, 128], "dtype": "COMPLEX64"}},
                output_domain={"iterations": {"shape": [128, 128], "dtype": "INT32"}},
                exactness_mode=ExactnessMode.INTEGER_EXACT,
                tolerance_epsilon=0.0,
            ),
            # 14. Irregular Workload
            "SPMV_IRREGULAR_CSR": ProblemContract(
                workload_id="SPMV_IRREGULAR_CSR",
                description="Compressed Sparse Row matrix-vector product with non-uniform sparsity",
                input_domain={
                    "data": {"shape": [2048], "dtype": "FP32"},
                    "indices": {"shape": [2048], "dtype": "INT32"},
                    "indptr": {"shape": [129], "dtype": "INT32"},
                    "x": {"shape": [128], "dtype": "FP32"},
                },
                output_domain={"y": {"shape": [128], "dtype": "FP32"}},
                exactness_mode=ExactnessMode.NUMERIC_TOLERANCE,
                tolerance_epsilon=1e-3,
            ),
            # 15. Adversarial Workload
            "ADVERSARIAL_HILBERT_STRESS": ProblemContract(
                workload_id="ADVERSARIAL_HILBERT_STRESS",
                description="Extremely ill-conditioned Hilbert matrix multiplication designed to break approximations",
                input_domain={"A": {"shape": [32, 32], "dtype": "FP32"}, "B": {"shape": [32, 32], "dtype": "FP32"}},
                output_domain={"C": {"shape": [32, 32], "dtype": "FP32"}},
                exactness_mode=ExactnessMode.NUMERIC_TOLERANCE,
                tolerance_epsilon=1e-4,
            ),
        }
        return contracts

    @classmethod
    def get_sample_inputs_for_workload(cls, workload_id: str) -> Dict[str, Any]:
        """Generates representative input tensors for a canonical workload."""
        w = workload_id.upper()
        if "GEMM" in w or "MLP" in w:
            return {"A": np.random.randn(128, 128).astype(np.float32), "B": np.random.randn(128, 128).astype(np.float32)}
        elif "CONV2D" in w:
            return {"image": np.random.randn(64, 64).astype(np.float32), "kernel": np.random.randn(5, 5).astype(np.float32)}
        elif "FFT" in w:
            return {"x": (np.random.randn(1024) + 1j * np.random.randn(1024)).astype(np.complex64)}
        elif "REDUCTION" in w:
            return {"x": np.random.randn(100000).astype(np.float32)}
        elif "SORT" in w:
            return {"x": np.random.randn(10000).astype(np.float32)}
        elif "PAGERANK" in w:
            adj = np.random.rand(128, 128).astype(np.float32) > 0.8
            return {"adj_matrix": adj.astype(np.float32)}
        elif "SHA256" in w:
            return {"data": b"HYPER_BENCHMARK_PAYLOAD_TEST_" * 32}
        elif "NBODY" in w:
            return {
                "positions": np.random.randn(256, 3).astype(np.float32),
                "velocities": np.random.randn(256, 3).astype(np.float32),
                "masses": np.random.rand(256).astype(np.float32) * 10.0 + 1.0,
                "dt": 0.01,
            }
        elif "ATTENTION" in w:
            return {
                "Q": np.random.randn(1, 32, 64).astype(np.float32),
                "K": np.random.randn(1, 32, 64).astype(np.float32),
                "V": np.random.randn(1, 32, 64).astype(np.float32),
            }
        elif "SOBEL" in w:
            return {"image": np.random.randn(128, 128).astype(np.float32)}
        elif "STREAMING" in w:
            return {"x": np.random.randn(1000000).astype(np.float32)}
        elif "MANDELBROT" in w:
            x = np.linspace(-2.0, 1.0, 128)
            y = np.linspace(-1.5, 1.5, 128)
            xx, yy = np.meshgrid(x, y)
            return {"c_grid": (xx + 1j * yy).astype(np.complex64)}
        elif "SPMV" in w:
            N = 128
            indptr = np.linspace(0, 2048, N + 1, dtype=np.int32)
            indices = np.random.randint(0, N, size=2048, dtype=np.int32)
            data = np.random.randn(2048).astype(np.float32)
            x_vec = np.random.randn(N).astype(np.float32)
            return {"data": data, "indices": indices, "indptr": indptr, "x": x_vec}
        elif "HILBERT" in w or "ADVERSARIAL" in w:
            dim = 32
            H = 1.0 / (np.arange(1, dim + 1)[:, None] + np.arange(1, dim + 1)[None, :] - 1.0).astype(np.float32)
            return {"A": H, "B": np.random.randn(dim, dim).astype(np.float32)}
        else:
            return {"x": np.random.randn(64).astype(np.float32)}


class NewWorkloadGenerator:
    """Generates novel, synthetic tensor workloads and computational expressions."""

    @classmethod
    def generate_random_workload(cls, seed: Optional[int] = None) -> Tuple[ProblemContract, CIRGraph, Dict[str, Any]]:
        rng = np.random.default_rng(seed)
        m = int(rng.integers(17, 73))
        k = int(rng.integers(13, 67))
        n = int(rng.integers(19, 79))
        
        w_id = f"SYNTHETIC_WORKLOAD_{m}X{k}X{n}"
        contract = ProblemContract(
            workload_id=w_id,
            description=f"Synthetic composite graph with prime/irregular shapes: {m}x{k} @ {k}x{n}",
            input_domain={"A": {"shape": [m, k], "dtype": "FP32"}, "B": {"shape": [k, n], "dtype": "FP32"}},
            output_domain={"C": {"shape": [m, n], "dtype": "FP32"}},
            exactness_mode=ExactnessMode.NUMERIC_TOLERANCE,
            tolerance_epsilon=1e-3,
        )

        g = CIRGraph(name=w_id)
        in_a = g.add_input("A", shape=(m, k), dtype=DataType.FP32)
        in_b = g.add_input("B", shape=(k, n), dtype=DataType.FP32)
        mm = g.add_op(OpType.MATMUL, [in_a, in_b], name="mm")
        relu = g.add_op(OpType.RELU, [mm], name="relu")
        g.mark_output(relu)

        inputs = {
            "A": rng.standard_normal((m, k)).astype(np.float32),
            "B": rng.standard_normal((k, n)).astype(np.float32),
        }
        return contract, g, inputs


class SelfChallengeEngine:
    """
    Self-Challenge Mode: Actively synthesizes workloads specifically engineered
    to falsify HYPER's internal optimizations and expose false verifications.
    """

    @classmethod
    def run_self_challenge(cls, rounds: int = 5) -> List[Dict[str, Any]]:
        results = []
        for r in range(1, rounds + 1):
            if r == 1:
                # Challenge: Awkward prime shapes (defeats fixed-size tiling)
                contract = ProblemContract(
                    workload_id="CHALLENGE_PRIME_TENSOR_37x41",
                    description="Non-power-of-2 dimensions designed to break SIMD/Tiling assumptions",
                    input_domain={"A": {"shape": [37, 41], "dtype": "FP32"}, "B": {"shape": [41, 47], "dtype": "FP32"}},
                    output_domain={"C": {"shape": [37, 47], "dtype": "FP32"}},
                    exactness_mode=ExactnessMode.NUMERIC_TOLERANCE,
                    tolerance_epsilon=1e-4,
                )
            elif r == 2:
                # Challenge: Extreme condition number (defeats low-rank truncation)
                contract = ProblemContract(
                    workload_id="CHALLENGE_HIGH_CONDITION_NUMBER",
                    description="Matrix with condition number > 1e7; SVD truncation will fail",
                    input_domain={"A": {"shape": [32, 32], "dtype": "FP32"}, "B": {"shape": [32, 32], "dtype": "FP32"}},
                    output_domain={"C": {"shape": [32, 32], "dtype": "FP32"}},
                    exactness_mode=ExactnessMode.NUMERIC_TOLERANCE,
                    tolerance_epsilon=1e-4,
                )
            elif r == 3:
                # Challenge: Zero-reuse memory streaming
                contract = ProblemContract(
                    workload_id="CHALLENGE_ZERO_REUSE_STREAM",
                    description="Elementwise stream where cache reuse is mathematically impossible",
                    input_domain={"x": {"shape": [500000], "dtype": "FP32"}},
                    output_domain={"y": {"shape": [500000], "dtype": "FP32"}},
                    exactness_mode=ExactnessMode.BIT_EXACT,
                    tolerance_epsilon=0.0,
                )
            else:
                contract, _, _ = NewWorkloadGenerator.generate_random_workload(seed=42 + r)

            from hyper.research_engine.search_and_cost import HybridEscalationSearchEngine
            best_cand, cost, proof, level = HybridEscalationSearchEngine.search_best_pathway(contract, max_level=3)

            results.append({
                "round": r,
                "workload_id": contract.workload_id,
                "verified": proof.is_verified,
                "max_error": proof.max_error,
                "escalation_level": level,
                "latency_ms": cost.execution_time_ms,
                "strategy_selected": best_cand.transformation_history[-1],
            })

        return results
