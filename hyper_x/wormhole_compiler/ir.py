"""
hyper_x/wormhole_compiler/ir.py
=============================================================================
HYPER-X Intermediate Representation (HyperIR) (Phase 31)
=============================================================================
Defines a structured, target-independent IR representing:
  - Tensors & Arrays (shape, dtype, layout, memory space)
  - Computational Operations (MatMul, Conv, Elementwise, Reduction)
  - Information Boundaries & Observables (Full, Top-K, Vector, Region)
  - Transformation Annotations (LowRank, Sparse, Delta, Cached)
  - Execution Targets (CPU, iGPU, Hybrid)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import json


@dataclass
class IRTensor:
    name: str
    shape: Tuple[int, ...]
    dtype: str = "float32"
    memory_space: str = "HOST_SHARED"  # HOST_SHARED, CPU_L3, SCRATCH
    is_observable: bool = False


@dataclass
class IROperation:
    op_id: str
    op_type: str  # "MATMUL", "CONV2D", "REDUCE_SUM", "TOP_K", "PROJECT"
    inputs: List[str]
    outputs: List[str]
    attributes: Dict[str, Any] = field(default_factory=dict)
    transformation_tag: Optional[str] = None
    target_backend: str = "CPU_AVX2"


@dataclass
class HyperIRModule:
    """Complete structured IR module for a compiled workload."""
    module_id: str
    tensors: Dict[str, IRTensor] = field(default_factory=dict)
    operations: List[IROperation] = field(default_factory=list)
    observable_outputs: List[str] = field(default_factory=list)

    def add_tensor(self, name: str, shape: Tuple[int, ...], dtype: str = "float32", is_observable: bool = False) -> IRTensor:
        t = IRTensor(name=name, shape=shape, dtype=dtype, is_observable=is_observable)
        self.tensors[name] = t
        if is_observable:
            self.observable_outputs.append(name)
        return t

    def add_operation(
        self,
        op_id: str,
        op_type: str,
        inputs: List[str],
        outputs: List[str],
        attributes: Optional[Dict[str, Any]] = None,
        transformation_tag: Optional[str] = None,
        target_backend: str = "CPU_AVX2"
    ) -> IROperation:
        op = IROperation(
            op_id=op_id,
            op_type=op_type,
            inputs=inputs,
            outputs=outputs,
            attributes=attributes or {},
            transformation_tag=transformation_tag,
            target_backend=target_backend
        )
        self.operations.append(op)
        return op

    def to_dict(self) -> Dict[str, Any]:
        return {
            "module_id": self.module_id,
            "tensors": {k: {"shape": v.shape, "dtype": v.dtype, "is_observable": v.is_observable} for k, v in self.tensors.items()},
            "operations": [
                {
                    "op_id": op.op_id,
                    "op_type": op.op_type,
                    "inputs": op.inputs,
                    "outputs": op.outputs,
                    "attributes": op.attributes,
                    "transformation": op.transformation_tag,
                    "target_backend": op.target_backend,
                }
                for op in self.operations
            ],
            "observable_outputs": self.observable_outputs,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
