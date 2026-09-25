"""
hyper/discovery/cir.py
======================
Canonical Computational Intermediate Representation (CIR).

Provides a formal, expressive, and rewrite-capable directed acyclic computational
graph for arbitrary mathematical, tensor, and numerical workloads.
"""

from __future__ import annotations

import copy
import dataclasses
import enum
import hashlib
import json
import uuid
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import numpy as np


class DataType(str, enum.Enum):
    FP64 = "FP64"
    FP32 = "FP32"
    FP16 = "FP16"
    BF16 = "BF16"
    INT64 = "INT64"
    INT32 = "INT32"
    INT16 = "INT16"
    INT8 = "INT8"
    BOOL = "BOOL"
    COMPLEX128 = "COMPLEX128"
    COMPLEX64 = "COMPLEX64"

    @classmethod
    def from_numpy(cls, dtype: np.dtype | type) -> DataType:
        dt = np.dtype(dtype)
        mapping = {
            np.dtype("float64"): cls.FP64,
            np.dtype("float32"): cls.FP32,
            np.dtype("float16"): cls.FP16,
            np.dtype("int64"): cls.INT64,
            np.dtype("int32"): cls.INT32,
            np.dtype("int16"): cls.INT16,
            np.dtype("int8"): cls.INT8,
            np.dtype("bool"): cls.BOOL,
            np.dtype("complex128"): cls.COMPLEX128,
            np.dtype("complex64"): cls.COMPLEX64,
        }
        return mapping.get(dt, cls.FP32)

    def to_numpy(self) -> np.dtype:
        mapping = {
            self.FP64: np.float64,
            self.FP32: np.float32,
            self.FP16: np.float16,
            self.BF16: np.float32,  # NumPy fallback
            self.INT64: np.int64,
            self.INT32: np.int32,
            self.INT16: np.int16,
            self.INT8: np.int8,
            self.BOOL: np.bool_,
            self.COMPLEX128: np.complex128,
            self.COMPLEX64: np.complex64,
        }
        return np.dtype(mapping[self])


class OpType(str, enum.Enum):
    # Linear Algebra
    MATMUL = "MATMUL"
    BATCH_MATMUL = "BATCH_MATMUL"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    NEG = "NEG"
    TRANSPOSE = "TRANSPOSE"
    PERMUTE = "PERMUTE"
    RESHAPE = "RESHAPE"
    SLICING = "SLICING"
    CONCAT = "CONCAT"
    SPLIT = "SPLIT"

    # Reductions
    REDUCE_SUM = "REDUCE_SUM"
    REDUCE_MEAN = "REDUCE_MEAN"
    REDUCE_MAX = "REDUCE_MAX"
    REDUCE_MIN = "REDUCE_MIN"
    REDUCE_NORM = "REDUCE_NORM"

    # Convolutions & Signal
    CONV1D = "CONV1D"
    CONV2D = "CONV2D"
    CONV3D = "CONV3D"
    FFT = "FFT"
    IFFT = "IFFT"
    FFT2D = "FFT2D"
    IFFT2D = "IFFT2D"

    # Non-linearities / Activations
    RELU = "RELU"
    GELU = "GELU"
    SILU = "SILU"
    SIGMOID = "SIGMOID"
    TANH = "TANH"
    SOFTMAX = "SOFTMAX"
    EXP = "EXP"
    LOG = "LOG"
    SQRT = "SQRT"
    POW = "POW"
    ABS = "ABS"

    # Special / Domain
    ATTENTION = "ATTENTION"
    FUSED_GEMM_ADD = "FUSED_GEMM_ADD"
    FUSED_CONV_RELU = "FUSED_CONV_RELU"
    FUSED_GEMM_RELU = "FUSED_GEMM_RELU"
    SCATTER_ADD = "SCATTER_ADD"
    GATHER = "GATHER"
    HASH_SHA256 = "HASH_SHA256"
    ODE_EULER_STEP = "ODE_EULER_STEP"
    CUSTOM = "CUSTOM"


class EdgeType(str, enum.Enum):
    DATA = "DATA"
    MEMORY_DEP = "MEMORY_DEP"
    CONTROL_DEP = "CONTROL_DEP"


@dataclasses.dataclass
class CIRTensorMeta:
    shape: Tuple[int, ...]
    dtype: DataType
    is_sparse: bool = False
    sparsity_ratio: float = 0.0
    memory_bytes: int = 0

    def __post_init__(self):
        if self.memory_bytes == 0 and self.shape:
            item_size = np.dtype(self.dtype.to_numpy()).itemsize
            total_elements = 1
            for d in self.shape:
                total_elements *= int(d)
            self.memory_bytes = total_elements * item_size

    def to_dict(self) -> Dict[str, Any]:
        return {
            "shape": list(self.shape),
            "dtype": self.dtype.value,
            "is_sparse": self.is_sparse,
            "sparsity_ratio": self.sparsity_ratio,
            "memory_bytes": self.memory_bytes,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> CIRTensorMeta:
        return cls(
            shape=tuple(d["shape"]),
            dtype=DataType(d["dtype"]),
            is_sparse=d.get("is_sparse", False),
            sparsity_ratio=d.get("sparsity_ratio", 0.0),
            memory_bytes=d.get("memory_bytes", 0),
        )


@dataclasses.dataclass
class CIREdge:
    source_id: str
    target_id: str
    edge_type: EdgeType = EdgeType.DATA
    source_output_idx: int = 0
    target_input_idx: int = 0
    tensor_meta: Optional[CIRTensorMeta] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type.value,
            "source_output_idx": self.source_output_idx,
            "target_input_idx": self.target_input_idx,
            "tensor_meta": self.tensor_meta.to_dict() if self.tensor_meta else None,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> CIREdge:
        return cls(
            source_id=d["source_id"],
            target_id=d["target_id"],
            edge_type=EdgeType(d.get("edge_type", EdgeType.DATA.value)),
            source_output_idx=d.get("source_output_idx", 0),
            target_input_idx=d.get("target_input_idx", 0),
            tensor_meta=CIRTensorMeta.from_dict(d["tensor_meta"]) if d.get("tensor_meta") else None,
        )


@dataclasses.dataclass
class CIRNode:
    node_id: str
    name: str
    op_type: OpType
    inputs: List[str] = dataclasses.field(default_factory=list)  # node_ids providing inputs
    attributes: Dict[str, Any] = dataclasses.field(default_factory=dict)
    constant_value: Optional[Any] = None  # Scalar, ndarray, or serialized constant
    output_meta: Optional[CIRTensorMeta] = None
    estimated_flops: float = 0.0
    side_effects: bool = False
    custom_eval_fn: Optional[Callable[..., Any]] = None  # Local evaluation callback if custom

    def to_dict(self) -> Dict[str, Any]:
        # Handle numpy constant serialization
        const_val = None
        if self.constant_value is not None:
            if isinstance(self.constant_value, np.ndarray):
                if self.constant_value.size <= 100:
                    const_val = {"type": "ndarray", "data": self.constant_value.tolist()}
                else:
                    const_val = {
                        "type": "ndarray_hash",
                        "shape": list(self.constant_value.shape),
                        "dtype": str(self.constant_value.dtype),
                        "sha256": hashlib.sha256(self.constant_value.tobytes()).hexdigest(),
                    }
            elif isinstance(self.constant_value, (int, float, bool, str, list)):
                const_val = self.constant_value
            else:
                const_val = str(self.constant_value)

        return {
            "node_id": self.node_id,
            "name": self.name,
            "op_type": self.op_type.value,
            "inputs": list(self.inputs),
            "attributes": copy.deepcopy(self.attributes),
            "constant_value": const_val,
            "output_meta": self.output_meta.to_dict() if self.output_meta else None,
            "estimated_flops": self.estimated_flops,
            "side_effects": self.side_effects,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> CIRNode:
        const_val = d.get("constant_value")
        if isinstance(const_val, dict) and const_val.get("type") == "ndarray":
            const_val = np.array(const_val["data"])

        return cls(
            node_id=d["node_id"],
            name=d["name"],
            op_type=OpType(d["op_type"]),
            inputs=list(d.get("inputs", [])),
            attributes=dict(d.get("attributes", {})),
            constant_value=const_val,
            output_meta=CIRTensorMeta.from_dict(d["output_meta"]) if d.get("output_meta") else None,
            estimated_flops=float(d.get("estimated_flops", 0.0)),
            side_effects=bool(d.get("side_effects", False)),
        )


class CIRGraph:
    """
    Canonical Computational Intermediate Representation Graph.
    Directed Acyclic Graph supporting topological execution and pattern-based graph rewriting.
    """

    def __init__(self, name: str = "cir_graph", graph_id: Optional[str] = None):
        self.graph_id: str = graph_id or f"cir_{uuid.uuid4().hex[:12]}"
        self.name: str = name
        self.nodes: Dict[str, CIRNode] = {}
        self.edges: List[CIREdge] = []
        self.inputs: List[str] = []   # Node IDs acting as external inputs
        self.outputs: List[str] = []  # Node IDs designated as final outputs
        self.metadata: Dict[str, Any] = {}

    def add_input(self, name: str, shape: Tuple[int, ...], dtype: DataType = DataType.FP32) -> CIRNode:
        """Add an external input node."""
        node_id = f"in_{name}_{uuid.uuid4().hex[:6]}"
        meta = CIRTensorMeta(shape=shape, dtype=dtype)
        node = CIRNode(
            node_id=node_id,
            name=name,
            op_type=OpType.CUSTOM,
            attributes={"is_input": True},
            output_meta=meta,
        )
        self.nodes[node_id] = node
        self.inputs.append(node_id)
        return node

    def add_constant(self, name: str, value: Any, dtype: Optional[DataType] = None) -> CIRNode:
        """Add a constant scalar or tensor node."""
        node_id = f"const_{name}_{uuid.uuid4().hex[:6]}"
        if isinstance(value, np.ndarray):
            dt = dtype or DataType.from_numpy(value.dtype)
            meta = CIRTensorMeta(shape=value.shape, dtype=dt)
        else:
            val_arr = np.array(value)
            dt = dtype or DataType.from_numpy(val_arr.dtype)
            meta = CIRTensorMeta(shape=val_arr.shape, dtype=dt)

        node = CIRNode(
            node_id=node_id,
            name=name,
            op_type=OpType.CUSTOM,
            constant_value=value,
            attributes={"is_constant": True},
            output_meta=meta,
        )
        self.nodes[node_id] = node
        return node

    def add_op(
        self,
        op_type: OpType,
        inputs: List[CIRNode | str],
        name: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        output_meta: Optional[CIRTensorMeta] = None,
        estimated_flops: float = 0.0,
        custom_eval_fn: Optional[Callable[..., Any]] = None,
    ) -> CIRNode:
        """Add a computational operation node with directed data edges."""
        input_ids = [inp.node_id if isinstance(inp, CIRNode) else inp for inp in inputs]
        for inp_id in input_ids:
            if inp_id not in self.nodes:
                raise ValueError(f"Input node ID '{inp_id}' does not exist in CIR graph.")

        op_name = name or f"{op_type.value.lower()}_{uuid.uuid4().hex[:6]}"
        node_id = f"op_{op_name}_{uuid.uuid4().hex[:6]}"

        node = CIRNode(
            node_id=node_id,
            name=op_name,
            op_type=op_type,
            inputs=input_ids,
            attributes=attributes or {},
            output_meta=output_meta,
            estimated_flops=estimated_flops,
            custom_eval_fn=custom_eval_fn,
        )
        self.nodes[node_id] = node

        # Auto-create dataflow edges
        for idx, inp_id in enumerate(input_ids):
            src_node = self.nodes[inp_id]
            self.edges.append(
                CIREdge(
                    source_id=inp_id,
                    target_id=node_id,
                    edge_type=EdgeType.DATA,
                    source_output_idx=0,
                    target_input_idx=idx,
                    tensor_meta=src_node.output_meta,
                )
            )

        # Estimate FLOPs automatically if not provided
        if estimated_flops == 0.0:
            node.estimated_flops = self._estimate_op_flops(node)

        return node

    def mark_output(self, node: CIRNode | str):
        """Mark a node as an authoritative output of the CIR graph."""
        nid = node.node_id if isinstance(node, CIRNode) else node
        if nid not in self.nodes:
            raise ValueError(f"Output node '{nid}' not found in graph.")
        if nid not in self.outputs:
            self.outputs.append(nid)

    def _estimate_op_flops(self, node: CIRNode) -> float:
        """Heuristic FLOP calculator for standard operators."""
        if node.op_type == OpType.MATMUL:
            if len(node.inputs) >= 2:
                n0 = self.nodes.get(node.inputs[0])
                n1 = self.nodes.get(node.inputs[1])
                if n0 and n1 and n0.output_meta and n1.output_meta:
                    s0 = n0.output_meta.shape
                    s1 = n1.output_meta.shape
                    if len(s0) == 2 and len(s1) == 2:
                        M, K = s0
                        K2, N = s1
                        return 2.0 * float(M) * float(K) * float(N)
        elif node.op_type == OpType.CONV2D:
            if node.output_meta and node.output_meta.shape:
                s_out = node.output_meta.shape
                kernel_size = node.attributes.get("kernel_size", (3, 3))
                cin = node.attributes.get("in_channels", 1)
                # 2 * H_out * W_out * C_out * (C_in * Kh * Kw)
                if len(s_out) == 4:
                    N, Cout, Hout, Wout = s_out
                    return 2.0 * N * Cout * Hout * Wout * (cin * kernel_size[0] * kernel_size[1])
        elif node.op_type in (OpType.FFT, OpType.IFFT):
            if len(node.inputs) >= 1:
                n0 = self.nodes.get(node.inputs[0])
                if n0 and n0.output_meta and n0.output_meta.shape:
                    sz = float(np.prod(n0.output_meta.shape))
                    return 5.0 * sz * np.log2(max(sz, 2.0))
        elif node.op_type in (OpType.ADD, OpType.SUB, OpType.MUL, OpType.DIV, OpType.RELU):
            if node.output_meta and node.output_meta.shape:
                return float(np.prod(node.output_meta.shape))
        return 1.0

    def total_estimated_flops(self) -> float:
        """Return the sum of estimated FLOPs across all nodes in the graph."""
        return sum(n.estimated_flops for n in self.nodes.values())

    def topological_sort(self) -> List[str]:
        """Compute topological ordering of nodes directly from node.inputs."""
        in_degree: Dict[str, int] = {nid: 0 for nid in self.nodes}
        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}

        for nid, node in self.nodes.items():
            for inp_id in node.inputs:
                if inp_id in self.nodes:
                    adj[inp_id].append(nid)
                    in_degree[nid] += 1

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        order = []

        while queue:
            curr = queue.pop(0)
            order.append(curr)
            for neighbor in adj.get(curr, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self.nodes):
            raise ValueError("CIR graph contains a cycle! Valid CIR must be a DAG.")

        return order

    def evaluate(self, input_values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interprets and executes the CIR graph topologically.
        input_values: Dict mapping input node names or IDs to ndarray / scalar values.
        Returns: Dict mapping output node names or IDs to computed results.
        """
        order = self.topological_sort()
        env: Dict[str, Any] = {}

        # Bind external inputs
        for in_id in self.inputs:
            node = self.nodes[in_id]
            if node.name in input_values:
                env[in_id] = input_values[node.name]
            elif in_id in input_values:
                env[in_id] = input_values[in_id]
            else:
                raise KeyError(f"Missing required input '{node.name}' (ID: {in_id}) in evaluation.")

        # Execute nodes
        for nid in order:
            node = self.nodes[nid]
            if nid in env:
                continue

            if node.attributes.get("is_constant"):
                env[nid] = node.constant_value
                continue

            # Gather inputs
            args = [env[inp_id] for inp_id in node.inputs]

            # Execute custom function if present
            if node.custom_eval_fn is not None:
                env[nid] = node.custom_eval_fn(*args)
                continue

            # Standard operator interpreter
            env[nid] = self._eval_standard_op(node.op_type, args, node.attributes)

        # Collect outputs
        results = {}
        for out_id in self.outputs:
            out_node = self.nodes[out_id]
            results[out_node.name] = env[out_id]
        return results

    def _eval_standard_op(self, op_type: OpType, args: List[Any], attrs: Dict[str, Any]) -> Any:
        """Built-in evaluation logic for canonical CIR operators."""
        if op_type == OpType.MATMUL:
            return np.matmul(args[0], args[1])
        elif op_type == OpType.ADD:
            return args[0] + args[1]
        elif op_type == OpType.SUB:
            return args[0] - args[1]
        elif op_type == OpType.MUL:
            return args[0] * args[1]
        elif op_type == OpType.DIV:
            return args[0] / args[1]
        elif op_type == OpType.NEG:
            return -args[0]
        elif op_type == OpType.TRANSPOSE:
            axes = attrs.get("axes", None)
            return np.transpose(args[0], axes=axes)
        elif op_type == OpType.RESHAPE:
            target_shape = attrs.get("shape", args[0].shape)
            return np.reshape(args[0], target_shape)
        elif op_type == OpType.RELU:
            return np.maximum(args[0], 0)
        elif op_type == OpType.GELU:
            x = args[0]
            return 0.5 * x * (1.0 + np.tanh(np.sqrt(2.0 / np.pi) * (x + 0.044715 * np.power(x, 3))))
        elif op_type == OpType.EXP:
            return np.exp(args[0])
        elif op_type == OpType.LOG:
            return np.log(args[0])
        elif op_type == OpType.SQRT:
            return np.sqrt(args[0])
        elif op_type == OpType.ABS:
            return np.abs(args[0])
        elif op_type == OpType.REDUCE_SUM:
            axis = attrs.get("axis", None)
            keepdims = attrs.get("keepdims", False)
            return np.sum(args[0], axis=axis, keepdims=keepdims)
        elif op_type == OpType.REDUCE_MEAN:
            axis = attrs.get("axis", None)
            keepdims = attrs.get("keepdims", False)
            return np.mean(args[0], axis=axis, keepdims=keepdims)
        elif op_type == OpType.CONV2D:
            # 2D cross-correlation / convolution
            inp, weight = args[0], args[1]
            bias = args[2] if len(args) > 2 else None
            return self._conv2d_reference(inp, weight, bias, attrs)
        elif op_type == OpType.FFT:
            return np.fft.fft(args[0], axis=attrs.get("axis", -1))
        elif op_type == OpType.IFFT:
            return np.fft.ifft(args[0], axis=attrs.get("axis", -1))
        elif op_type == OpType.FUSED_GEMM_ADD:
            return np.matmul(args[0], args[1]) + args[2]
        elif op_type == OpType.FUSED_CONV_RELU:
            res = self._conv2d_reference(args[0], args[1], args[2] if len(args) > 2 else None, attrs)
            return np.maximum(res, 0)
        elif op_type == OpType.FUSED_GEMM_RELU:
            return np.maximum(np.matmul(args[0], args[1]), 0)
        elif op_type == OpType.ATTENTION:
            # Q, K, V
            q, k, v = args[0], args[1], args[2]
            scale = attrs.get("scale", 1.0 / np.sqrt(q.shape[-1]))
            scores = np.matmul(q, np.swapaxes(k, -1, -2)) * scale
            exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
            probs = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
            return np.matmul(probs, v)
        elif op_type == OpType.HASH_SHA256:
            data = args[0]
            if isinstance(data, np.ndarray):
                b = data.tobytes()
            elif isinstance(data, str):
                b = data.encode("utf-8")
            else:
                b = str(data).encode("utf-8")
            return hashlib.sha256(b).hexdigest()
        elif op_type == OpType.ODE_EULER_STEP:
            # y_next = y + dt * f(y)
            y, f_val = args[0], args[1]
            dt = attrs.get("dt", 0.01)
            return y + dt * f_val
        else:
            raise NotImplementedError(f"Interpreter for operator {op_type.value} is not implemented.")

    def _conv2d_reference(self, x: np.ndarray, w: np.ndarray, b: Optional[np.ndarray], attrs: Dict[str, Any]) -> np.ndarray:
        """Reference 2D Convolution for CIR verification."""
        stride = attrs.get("stride", 1)
        padding = attrs.get("padding", 0)

        orig_x_ndim = x.ndim
        if x.ndim == 2:
            x = x[np.newaxis, np.newaxis, :, :]
        elif x.ndim == 3:
            x = x[np.newaxis, :, :, :]

        if w.ndim == 2:
            w = w[np.newaxis, np.newaxis, :, :]
        elif w.ndim == 3:
            w = w[:, np.newaxis, :, :]

        N, C_in, H, W = x.shape
        C_out, _, Kh, Kw = w.shape

        if padding > 0:
            x_padded = np.pad(x, ((0, 0), (0, 0), (padding, padding), (padding, padding)), mode="constant")
        else:
            x_padded = x

        H_out = (H + 2 * padding - Kh) // stride + 1
        W_out = (W + 2 * padding - Kw) // stride + 1
        out = np.zeros((N, C_out, H_out, W_out), dtype=x.dtype)

        for n in range(N):
            for co in range(C_out):
                for h in range(H_out):
                    for wi in range(W_out):
                        h_start = h * stride
                        w_start = wi * stride
                        patch = x_padded[n, :, h_start : h_start + Kh, w_start : w_start + Kw]
                        val = np.sum(patch * w[co])
                        if b is not None:
                            val += b[co]
                        out[n, co, h, wi] = val
        if orig_x_ndim == 2:
            return out[0, 0]
        elif orig_x_ndim == 3:
            return out[0]
        return out

    def clone(self) -> CIRGraph:
        """Return a deep copy of the CIR graph."""
        new_g = CIRGraph(name=f"{self.name}_copy", graph_id=f"cir_{uuid.uuid4().hex[:12]}")
        for nid, node in self.nodes.items():
            new_node = CIRNode(
                node_id=node.node_id,
                name=node.name,
                op_type=node.op_type,
                inputs=list(node.inputs),
                attributes=copy.deepcopy(node.attributes),
                constant_value=copy.deepcopy(node.constant_value),
                output_meta=copy.deepcopy(node.output_meta),
                estimated_flops=node.estimated_flops,
                side_effects=node.side_effects,
                custom_eval_fn=node.custom_eval_fn,
            )
            new_g.nodes[nid] = new_node
        new_g.edges = [copy.deepcopy(e) for e in self.edges]
        new_g.inputs = list(self.inputs)
        new_g.outputs = list(self.outputs)
        new_g.metadata = copy.deepcopy(self.metadata)
        return new_g

    def eliminate_dead_nodes(self) -> int:
        """Eliminate nodes that do not reach designated outputs."""
        needed: Set[str] = set()

        def mark(nid: str):
            if nid in needed:
                return
            needed.add(nid)
            node = self.nodes.get(nid)
            if node:
                for inp_id in node.inputs:
                    mark(inp_id)

        for out_id in self.outputs:
            mark(out_id)

        to_remove = [nid for nid in self.nodes if nid not in needed and nid not in self.inputs]
        for nid in to_remove:
            del self.nodes[nid]

        self.edges = [e for e in self.edges if e.source_id in self.nodes and e.target_id in self.nodes]
        return len(to_remove)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize complete CIR graph to JSON-compatible dictionary."""
        return {
            "graph_id": self.graph_id,
            "name": self.name,
            "inputs": list(self.inputs),
            "outputs": list(self.outputs),
            "metadata": copy.deepcopy(self.metadata),
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()},
            "edges": [edge.to_dict() for edge in self.edges],
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> CIRGraph:
        """Deserialize CIR graph from dictionary."""
        graph = cls(name=d["name"], graph_id=d["graph_id"])
        graph.inputs = list(d.get("inputs", []))
        graph.outputs = list(d.get("outputs", []))
        graph.metadata = dict(d.get("metadata", {}))

        for nid, ndict in d.get("nodes", {}).items():
            graph.nodes[nid] = CIRNode.from_dict(ndict)

        for edict in d.get("edges", []):
            graph.edges.append(CIREdge.from_dict(edict))

        return graph

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, s: str) -> CIRGraph:
        return cls.from_dict(json.loads(s))
