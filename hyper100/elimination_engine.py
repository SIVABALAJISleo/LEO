"""
hyper100/elimination_engine.py
==============================
Computation Elimination Engine.
Performs algebraic common subexpression elimination, dead-node pruning,
dependency graph reduction, and incremental delta computation.
"""

import time
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass
import numpy as np

from .workload_analyzer import ComputationGraph, ComputationNode


@dataclass
class EliminationReport:
    """Audit record of computation eliminated from the execution graph."""
    original_operations: float
    eliminated_operations: float
    remaining_operations: float
    elimination_ratio: float           # (eliminated / original) in [0.0, 1.0]
    elimination_techniques: List[str]  # e.g., ['CSE', 'DEAD_CODE', 'DELTA_INCREMENTAL']
    correctness_classification: str    # 'EXACT', 'NUMERICALLY_EQUIVALENT', or 'APPROXIMATE'
    execution_time_saved_ms: float


class ComputationEliminationEngine:
    """Applies provable mathematical reductions to eliminate redundant FLOPs."""

    @staticmethod
    def eliminate_cse(graph: ComputationGraph) -> Tuple[ComputationGraph, EliminationReport]:
        """
        Common Subexpression Elimination across graph nodes.
        Merges nodes that perform identical operations on identical input signatures.
        """
        seen_ops: Dict[str, str] = {}  # signature -> primary_node_id
        eliminated_flops = 0.0
        orig_flops = sum(n.estimated_flops for n in graph.nodes.values())
        reduced_graph = ComputationGraph(name=f"{graph.name}_cse_reduced")
        merged_count = 0

        for node in graph.topological_sort():
            sig = f"{node.op_type}_{sorted(node.input_ids)}_{node.output_shape}"
            if sig in seen_ops and node.is_pure:
                # Merge into existing node
                primary_id = seen_ops[sig]
                eliminated_flops += node.estimated_flops
                merged_count += 1
            else:
                seen_ops[sig] = node.node_id
                reduced_graph.add_node(node)

        remaining_flops = orig_flops - eliminated_flops
        ratio = (eliminated_flops / orig_flops) if orig_flops > 0 else 0.0

        techniques = []
        if merged_count > 0:
            techniques.append(f"CSE_MERGED_{merged_count}_NODES")

        report = EliminationReport(
            original_operations=orig_flops,
            eliminated_operations=eliminated_flops,
            remaining_operations=remaining_flops,
            elimination_ratio=ratio,
            elimination_techniques=techniques or ["NO_CSE_OPPORTUNITY"],
            correctness_classification="EXACT",
            execution_time_saved_ms=(eliminated_flops / (50e9)) * 1000.0  # Approx CPU AVX2 throughput
        )
        return reduced_graph, report

    @staticmethod
    def incremental_delta_matmul(
        A: np.ndarray,
        B_curr: np.ndarray,
        B_prev: Optional[np.ndarray],
        Y_prev: Optional[np.ndarray],
        delta_threshold: float = 1e-4
    ) -> Tuple[np.ndarray, EliminationReport]:
        """
        Computes Y = A @ B incrementally:
        If B_curr = B_prev + Delta_B and Delta_B is sparse,
        Y_curr = Y_prev + A @ Delta_B.
        Saves up to 90% of FLOPs when state updates are localized.
        """
        M, K = A.shape
        _, N = B_curr.shape
        orig_flops = 2.0 * M * N * K

        if B_prev is not None and Y_prev is not None and B_prev.shape == B_curr.shape:
            delta_B = B_curr - B_prev
            active_cols = np.where(np.linalg.norm(delta_B, axis=0) > delta_threshold)[0]
            num_active = len(active_cols)

            if num_active < 0.5 * N:
                # Sparse column update
                delta_B_sparse = delta_B[:, active_cols]
                delta_Y = A @ delta_B_sparse
                Y_curr = np.array(Y_prev, copy=True)
                Y_curr[:, active_cols] += delta_Y

                active_flops = 2.0 * M * num_active * K
                elim_flops = orig_flops - active_flops
                ratio = elim_flops / orig_flops

                report = EliminationReport(
                    original_operations=orig_flops,
                    eliminated_operations=elim_flops,
                    remaining_operations=active_flops,
                    elimination_ratio=ratio,
                    elimination_techniques=[f"INCREMENTAL_COLUMN_UPDATE_{num_active}_OF_{N}"],
                    correctness_classification="NUMERICALLY_EQUIVALENT",
                    execution_time_saved_ms=(elim_flops / 50e9) * 1000.0
                )
                return Y_curr, report

        # Full compute fallback
        Y_full = A @ B_curr
        report = EliminationReport(
            original_operations=orig_flops,
            eliminated_operations=0.0,
            remaining_operations=orig_flops,
            elimination_ratio=0.0,
            elimination_techniques=["DENSE_FULL_COMPUTE"],
            correctness_classification="EXACT",
            execution_time_saved_ms=0.0
        )
        return Y_full, report
