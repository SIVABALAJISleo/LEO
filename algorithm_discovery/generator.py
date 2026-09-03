"""
algorithm_discovery/generator.py
Synthesizes candidate executable algorithmic strategies across algorithm, representation,
precision, scheduling, and device mapping dimensions.
"""

from typing import Dict, Any, List, Optional
import copy


class AlgorithmStrategy:
    """Executable algorithmic candidate with complete architectural specification."""
    def __init__(
        self,
        strategy_id: str,
        algorithm_name: str,
        representation: str,      # dense, sparse_2to4, low_rank, bitnet_ternary, morton_bvh, frequency
        precision: str,           # fp32, fp16, int8, ternary
        device_mapping: str,      # CPU, iGPU, HYBRID
        cpu_ratio: float = 0.5,   # partition ratio for hybrid
        tile_size: int = 64,
        vector_width: int = 8,
        approximation_param: float = 0.0,
        expected_complexity: str = "O(N^3)",
        estimated_vwa: float = 0.0
    ):
        self.strategy_id = strategy_id
        self.algorithm_name = algorithm_name
        self.representation = representation
        self.precision = precision
        self.device_mapping = device_mapping
        self.cpu_ratio = cpu_ratio
        self.tile_size = tile_size
        self.vector_width = vector_width
        self.approximation_param = approximation_param
        self.expected_complexity = expected_complexity
        self.estimated_vwa = estimated_vwa

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "algorithm_name": self.algorithm_name,
            "representation": self.representation,
            "precision": self.precision,
            "device_mapping": self.device_mapping,
            "cpu_ratio": self.cpu_ratio,
            "tile_size": self.tile_size,
            "vector_width": self.vector_width,
            "approximation_param": self.approximation_param,
            "expected_complexity": self.expected_complexity,
            "estimated_vwa": self.estimated_vwa
        }


class StrategyCandidateGenerator:
    """Generates a diverse set of algorithmic candidates for a given workload domain."""

    @staticmethod
    def generate_candidates(workload_name: str, allow_approx: bool = True) -> List[AlgorithmStrategy]:
        """Synthesizes candidate strategies covering exact, structured, and transformed approaches."""
        candidates: List[AlgorithmStrategy] = []

        # Baseline Exact Reference Candidate
        candidates.append(AlgorithmStrategy(
            strategy_id=f"{workload_name}_exact_cpu",
            algorithm_name="reference_direct",
            representation="dense",
            precision="fp32",
            device_mapping="CPU",
            cpu_ratio=1.0,
            expected_complexity="standard_reference",
            estimated_vwa=0.0
        ))

        # Specialized Candidates by Domain
        if "gemm" in workload_name or "matmul" in workload_name:
            candidates.append(AlgorithmStrategy(
                strategy_id=f"{workload_name}_tiled_hybrid",
                algorithm_name="cache_tiled_gemm",
                representation="dense",
                precision="fp32",
                device_mapping="HYBRID",
                cpu_ratio=0.6,
                tile_size=64,
                vector_width=8,
                expected_complexity="O(N^3)",
                estimated_vwa=0.15
            ))
            if allow_approx:
                candidates.append(AlgorithmStrategy(
                    strategy_id=f"{workload_name}_sparse_2to4_igpu",
                    algorithm_name="sparse_2to4_matmul",
                    representation="sparse_2to4",
                    precision="fp16",
                    device_mapping="iGPU",
                    cpu_ratio=0.0,
                    tile_size=128,
                    approximation_param=0.05,
                    expected_complexity="O(0.5 * N^3)",
                    estimated_vwa=0.50
                ))
                candidates.append(AlgorithmStrategy(
                    strategy_id=f"{workload_name}_low_rank_svd",
                    algorithm_name="randomized_svd_factorized",
                    representation="low_rank",
                    precision="fp32",
                    device_mapping="HYBRID",
                    cpu_ratio=0.5,
                    approximation_param=0.10,
                    expected_complexity="O(2 * k * N^2)",
                    estimated_vwa=0.75
                ))

        elif "fft" in workload_name:
            if allow_approx:
                candidates.append(AlgorithmStrategy(
                    strategy_id=f"{workload_name}_sparse_sfft",
                    algorithm_name="sublinear_sfft",
                    representation="frequency",
                    precision="fp32",
                    device_mapping="CPU",
                    cpu_ratio=1.0,
                    approximation_param=0.01,
                    expected_complexity="O(k * log N)",
                    estimated_vwa=0.80
                ))

        elif "nbody" in workload_name:
            if allow_approx:
                candidates.append(AlgorithmStrategy(
                    strategy_id=f"{workload_name}_barnes_hut_octree",
                    algorithm_name="barnes_hut_spatial_octree",
                    representation="hierarchical",
                    precision="fp32",
                    device_mapping="CPU",
                    cpu_ratio=1.0,
                    approximation_param=0.05,
                    expected_complexity="O(N * log N)",
                    estimated_vwa=0.90
                ))

        elif "monte_carlo" in workload_name:
            if allow_approx:
                candidates.append(AlgorithmStrategy(
                    strategy_id=f"{workload_name}_qmc_sobol",
                    algorithm_name="quasi_monte_carlo_sobol",
                    representation="sampled",
                    precision="fp32",
                    device_mapping="CPU",
                    cpu_ratio=1.0,
                    approximation_param=0.02,
                    expected_complexity="O(N_sub)",
                    estimated_vwa=0.90
                ))

        return candidates
