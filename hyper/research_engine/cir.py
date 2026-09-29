"""
hyper/research_engine/cir.py
============================
Unified Computational Intermediate Representation (CIR) Interface.
Provides unified access to CIRGraph, CIRNode, CIREdge, and converters for workloads.
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
import numpy as np

from hyper.discovery.cir import (
    CIRGraph,
    CIRNode,
    CIREdge,
    CIRTensorMeta,
    DataType,
    OpType,
    EdgeType,
)
from hyper.research_engine.contracts import ComputationalContract, ProblemContract
from hyper.research_engine.exactness import ExactnessCategory, ExactnessMode

__all__ = [
    "CIRGraph",
    "CIRNode",
    "CIREdge",
    "CIRTensorMeta",
    "DataType",
    "OpType",
    "EdgeType",
    "ComputationalContract",
    "ProblemContract",
    "ExactnessCategory",
    "ExactnessMode",
    "workload_contract_to_cir",
]


def workload_contract_to_cir(contract: ComputationalContract) -> CIRGraph:
    """
    Constructs a canonical baseline CIRGraph from a ComputationalContract.
    Binds the contract and establishes inputs, operations, and outputs.
    """
    g = CIRGraph(name=contract.workload_id)
    g.bind_contract(contract)

    # 1. Inputs
    created_nodes: Dict[str, CIRNode] = {}
    for inp_name, domain in contract.input_domain.items():
        shape = tuple(domain.get("shape", (1,)))
        dtype_str = domain.get("dtype", "FP32")
        dt = getattr(DataType, dtype_str, DataType.FP32)
        node = g.add_input(inp_name, shape=shape, dtype=dt)
        created_nodes[inp_name] = node

    # 2. Heuristic op construction based on workload ID
    w_id = contract.workload_id.upper()
    if "GEMM" in w_id or "MATMUL" in w_id:
        if "A" in created_nodes and "B" in created_nodes:
            op = g.add_op(OpType.MATMUL, [created_nodes["A"], created_nodes["B"]], name="matmul_out")
            g.mark_output(op)
    elif "CONV" in w_id:
        if "x" in created_nodes and "w" in created_nodes:
            inputs = [created_nodes["x"], created_nodes["w"]]
            if "b" in created_nodes:
                inputs.append(created_nodes["b"])
            op = g.add_op(OpType.CONV2D, inputs, name="conv2d_out")
            g.mark_output(op)
    elif "FFT" in w_id:
        inp = list(created_nodes.values())[0] if created_nodes else None
        if inp:
            op = g.add_op(OpType.FFT, [inp], name="fft_out")
            g.mark_output(op)
    elif "REDUCTION" in w_id:
        inp = list(created_nodes.values())[0] if created_nodes else None
        if inp:
            op = g.add_op(OpType.REDUCE_SUM, [inp], name="reduce_sum_out")
            g.mark_output(op)
    elif "SORT" in w_id or "GRAPH" in w_id or "CRYPTO" in w_id or "NBODY" in w_id:
        # Generic op representing the canonical baseline kernel
        inp_list = list(created_nodes.values())
        op = g.add_op(OpType.CUSTOM, inp_list, name=f"{w_id.lower()}_baseline_op")
        g.mark_output(op)
    else:
        inp_list = list(created_nodes.values())
        op = g.add_op(OpType.CUSTOM, inp_list, name=f"{w_id.lower()}_kernel")
        g.mark_output(op)

    return g
