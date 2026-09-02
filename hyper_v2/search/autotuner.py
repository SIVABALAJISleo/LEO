"""
hyper_v2/search/autotuner.py
Autonomous candidate generator, cost evaluator, and strategy selector for HYPER 2.0.
"""

from typing import List, Dict, Any, Optional, Tuple
from hyper_v2.compiler.contract_compiler import ExecutionContract
from hyper_v2.compiler.intermediate_representation import ComputationGraphIR, DeviceTarget
from hyper_v2.search.cost_model import PredictiveCostModel, CostBreakdown


class StrategyAutotuner:
    """Explores the candidate transformation space and selects the lowest-cost verified execution strategy."""

    @staticmethod
    def generate_candidate_strategies(graph: ComputationGraphIR, contract: ExecutionContract) -> List[Dict[str, Any]]:
        candidates = []
        flops = graph.total_flops
        bytes_r = graph.total_memory_traffic_bytes // 2
        bytes_w = graph.total_memory_traffic_bytes // 2

        # Candidate 0: Dense CPU Baseline (Track A fallback)
        candidates.append({
            "name": "Dense_CPU_AVX2_Baseline",
            "flops": flops,
            "bytes_read": bytes_r,
            "bytes_written": bytes_w,
            "device": DeviceTarget.CPU_PCORE,
            "error_estimate": 0.0,
            "level": 8
        })

        # Candidate 1: Dense iGPU OpenVINO
        candidates.append({
            "name": "Dense_Intel_iGPU_OpenVINO",
            "flops": flops,
            "bytes_read": bytes_r,
            "bytes_written": bytes_w,
            "device": DeviceTarget.INTEL_IGPU,
            "error_estimate": 0.0,
            "level": 5
        })

        # Candidate 2: CPU+iGPU Split Hybrid
        candidates.append({
            "name": "Hybrid_CPU_iGPU_Split",
            "flops": flops,
            "bytes_read": bytes_r,
            "bytes_written": bytes_w,
            "device": DeviceTarget.HYBRID_CPU_IGPU,
            "error_estimate": 0.0,
            "level": 5
        })

        # If contract permits optimizations (Track B)
        if not contract.exactness_required:
            # Candidate 3: Fused Kernel Sequence
            if contract.is_transformation_permitted("kernel_fusion"):
                candidates.append({
                    "name": "Fused_SIMD_InRegister",
                    "flops": int(flops * 0.95),
                    "bytes_read": bytes_r,
                    "bytes_written": int(bytes_w * 0.2),  # Eliminate intermediate write
                    "device": DeviceTarget.CPU_PCORE,
                    "error_estimate": 0.0,
                    "level": 4
                })

            # Candidate 4: Low-Rank / BitNet b1.58
            if contract.is_transformation_permitted("low_rank"):
                candidates.append({
                    "name": "Randomized_SVD_LowRank_BitNet",
                    "flops": int(flops * 0.045),
                    "bytes_read": int(bytes_r * 0.08),
                    "bytes_written": bytes_w,
                    "device": DeviceTarget.CPU_PCORE,
                    "error_estimate": 0.0008,
                    "level": 2
                })

            # Candidate 5: Sublinear Sparse FFT
            if contract.is_transformation_permitted("sparsity"):
                candidates.append({
                    "name": "Sublinear_Sparse_FFT",
                    "flops": int(flops * 0.034),
                    "bytes_read": int(bytes_r * 0.05),
                    "bytes_written": bytes_w,
                    "device": DeviceTarget.CPU_PCORE,
                    "error_estimate": 0.0004,
                    "level": 3
                })

            # Candidate 6: Barnes-Hut Octree
            if contract.is_transformation_permitted("Barnes_Hut_expansion"):
                candidates.append({
                    "name": "Barnes_Hut_Octree_O(N_log_N)",
                    "flops": int(flops * 0.003),
                    "bytes_read": int(bytes_r * 0.01),
                    "bytes_written": bytes_w,
                    "device": DeviceTarget.HYBRID_CPU_IGPU,
                    "error_estimate": 0.0001,
                    "level": 3
                })

            # Candidate 7: Zero-Compute Semantic Cache
            if contract.is_transformation_permitted("reuse"):
                candidates.append({
                    "name": "Zero_Compute_Lattice_Reuse",
                    "flops": 100,
                    "bytes_read": 1024,
                    "bytes_written": 1024,
                    "device": DeviceTarget.CPU_PCORE,
                    "error_estimate": 0.0,
                    "level": 0
                })

        return candidates

    @staticmethod
    def select_optimal_strategy(graph: ComputationGraphIR, contract: ExecutionContract) -> Tuple[CostBreakdown, List[CostBreakdown]]:
        candidates = StrategyAutotuner.generate_candidate_strategies(graph, contract)
        evaluations: List[CostBreakdown] = []

        for cand in candidates:
            cost = PredictiveCostModel.evaluate_strategy_cost(
                strategy_name=cand["name"],
                flops=cand["flops"],
                bytes_read=cand["bytes_read"],
                bytes_written=cand["bytes_written"],
                device=cand["device"],
                tolerance_budget=contract.numerical_tolerance,
                error_estimate=cand["error_estimate"]
            )
            evaluations.append(cost)

        # Filter viable and sort by total estimated latency
        viable = [c for c in evaluations if c.is_contract_viable]
        if not viable:
            viable = evaluations  # Fallback to least-cost candidate

        viable.sort(key=lambda x: x.total_estimated_latency_ms)
        best_strategy = viable[0]
        return best_strategy, evaluations
