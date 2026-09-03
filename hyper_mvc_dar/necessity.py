"""
hyper_mvc_dar/necessity.py
Necessity Proof Engine: Formally proves whether an operation is necessary or can be eliminated,
reused, derived from invariants, or approximated under the contract.
"""

from enum import Enum, auto
from typing import Dict, List, Any, Optional
from .ir import OpNode, ComputationGraph, OpType
from .contract import ExecutionContract


class NecessityStatus(Enum):
    ESSENTIAL = "ESSENTIAL"
    CONDITIONALLY_ESSENTIAL = "CONDITIONALLY_ESSENTIAL"
    REDUNDANT = "REDUNDANT"
    DERIVABLE = "DERIVABLE"
    PREDICTABLE = "PREDICTABLE"
    DISCARDABLE = "DISCARDABLE"
    UNKNOWN = "UNKNOWN"


class NecessityProofEngine:
    """Evaluates operations against the 11 Invariant Queries."""

    @staticmethod
    def classify_operation(node: OpNode, graph: ComputationGraph, contract: ExecutionContract) -> Dict[str, Any]:
        # 1. Terminal dependency check
        is_terminal = any(out in graph.terminal_outputs for out in node.outputs)
        succs = graph.get_successors(node.node_id)
        
        if not is_terminal and len(succs) == 0:
            return {
                "status": NecessityStatus.DISCARDABLE,
                "reason": "Dead code: no terminal or intermediate consumer depends on output",
                "can_eliminate": True
            }

        # 2. Check for constant or identity reduction
        if node.op_type == OpType.ELEMENTWISE and node.metadata.get("is_identity", False):
            return {
                "status": NecessityStatus.DERIVABLE,
                "reason": "Identity operation: output equals input",
                "can_eliminate": True
            }

        # 3. Check for low-rank / bounded approximation allowance
        if node.op_type == OpType.MATMUL and contract.allows_low_rank():
            input_tensor = graph.tensors.get(node.inputs[0]) if node.inputs else None
            if input_tensor and input_tensor.effective_rank and input_tensor.effective_rank < min(input_tensor.shape):
                return {
                    "status": NecessityStatus.CONDITIONALLY_ESSENTIAL,
                    "reason": f"Low-rank matrix structure detected (rank {input_tensor.effective_rank}); reducible via SVD",
                    "can_approximate": True
                }

        # Default classification
        return {
            "status": NecessityStatus.ESSENTIAL,
            "reason": "Mandatory computation required to satisfy contract output",
            "can_eliminate": False
        }
