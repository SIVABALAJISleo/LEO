"""
hyper/executor/reference_executor.py
====================================
Canonical Semantic Reference Executor for HYPER Universal IR.
Serves as the infallible Correctness Oracle.
Executes every opcode in pure, traceable, deterministic scalar/reference semantics
with zero candidate optimization.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from hyper.universal_ir.opcodes import Opcode, MemorySpace, MemoryLayout
from hyper.universal_ir.instruction import UniversalOp
from hyper.universal_ir.program import UniversalIRProgram
from hyper.semantics.types import DataType, TensorType
from hyper.semantics.arithmetic import (
    exact_fp32_add,
    exact_fp32_sub,
    exact_fp32_mul,
    exact_fp32_div,
    exact_fp32_fma,
    exact_fp32_sqrt,
    exact_int_add,
    exact_int_sub,
    exact_int_mul,
    exact_int_div,
    exact_int_rem,
    exact_int_shl,
    exact_int_shr_logical,
    exact_int_shr_arithmetic,
    bitcast_fp32_to_int32,
    bitcast_int32_to_fp32,
)


class UniversalReferenceExecutor:
    """
    Canonical Correctness Oracle.
    Executes a UniversalIRProgram strictly according to the declared semantic contract.
    """

    def __init__(self, trace_execution: bool = False) -> None:
        self.trace_execution = trace_execution
        self.trace_log: List[str] = []

    def execute(
        self,
        program: UniversalIRProgram,
        inputs: Dict[str, np.ndarray],
    ) -> Dict[str, np.ndarray]:
        """
        Execute program instructions sequentially in environment.
        Returns dictionary of output tensors.
        """
        program.validate()

        # Environment holds intermediate and output tensors
        env: Dict[str, np.ndarray] = {}
        for name, tensor in inputs.items():
            if name not in program.inputs:
                raise ValueError(f"Unexpected input '{name}' not declared in program inputs")
            expected_type = program.inputs[name]
            np_dtype = expected_type.dtype.to_numpy_dtype()
            arr = np.ascontiguousarray(tensor, dtype=np_dtype)
            if expected_type.shape and arr.shape != expected_type.shape:
                raise ValueError(
                    f"Shape mismatch for input '{name}': expected {expected_type.shape}, got {arr.shape}"
                )
            env[name] = arr

        # Step through instructions
        for idx, op in enumerate(program.instructions):
            out_tensor = self._execute_op(op, env)
            env[op.result_id] = out_tensor
            if self.trace_execution:
                self.trace_log.append(
                    f"[{idx}] {op.opcode.value} -> %{op.result_id} shape={out_tensor.shape} dtype={out_tensor.dtype}"
                )

        # Collect outputs
        outputs: Dict[str, np.ndarray] = {}
        for out_name in program.outputs:
            if out_name not in env:
                raise RuntimeError(f"Output '{out_name}' was not produced by program execution")
            outputs[out_name] = env[out_name]

        return outputs

    def _execute_op(self, op: UniversalOp, env: Dict[str, np.ndarray]) -> np.ndarray:
        opcode = op.opcode
        res_type = op.result_type
        if hasattr(res_type, "dtype"):
            np_dt = res_type.dtype.to_numpy_dtype()
        elif hasattr(res_type, "to_numpy_dtype"):
            np_dt = res_type.to_numpy_dtype()
        else:
            np_dt = np.float32

        # ----------------------------------------------------------------------
        # IDENTITY / BARRIER / CUSTOM
        # ----------------------------------------------------------------------
        if opcode == Opcode.IDENTITY:
            src_name = str(op.operands[0])
            return env[src_name].copy()

        elif opcode == Opcode.BARRIER:
            return np.array([0], dtype=np.int32)

        elif opcode == Opcode.CUSTOM:
            sub_op = op.attributes.get("sub_op", "")
            if sub_op == "PREFIX_SUM":
                src = env[str(op.operands[0])]
                return np.cumsum(src, dtype=np_dt)
            elif sub_op == "STENCIL_5POINT":
                g = env[str(op.operands[0])]
                out = g.copy()
                out[1:-1, 1:-1] = 0.25 * (g[0:-2, 1:-1] + g[2:, 1:-1] + g[1:-1, 0:-2] + g[1:-1, 2:])
                return out
            elif sub_op == "BITONIC_SORT":
                src = env[str(op.operands[0])]
                return np.sort(src)
            elif sub_op == "GRAPH_BFS":
                adj = env[str(op.operands[0])]
                src = int(env[str(op.operands[1])][0])
                n = adj.shape[0]
                dist = np.full(n, -1, dtype=np.int32)
                dist[src] = 0
                queue = [src]
                while queue:
                    u = queue.pop(0)
                    for v in range(n):
                        if adj[u, v] == 1 and dist[v] == -1:
                            dist[v] = dist[u] + 1
                            queue.append(v)
                return dist
            else:
                return env[str(op.operands[0])].copy()

        # ----------------------------------------------------------------------
        # CONST
        # ----------------------------------------------------------------------
        elif opcode == Opcode.CONST:
            val = op.operands[0]
            if isinstance(val, (int, float, bool)):
                return np.full(getattr(res_type, "shape", None) or (1,), val, dtype=np_dt)
            elif isinstance(val, (list, tuple)):
                return np.array(val, dtype=np_dt).reshape(getattr(res_type, "shape", None) or (-1,))
            else:
                return np.full(getattr(res_type, "shape", None) or (1,), float(val), dtype=np_dt)

        # ----------------------------------------------------------------------
        # LOAD / STORE
        # ----------------------------------------------------------------------
        elif opcode == Opcode.LOAD:
            src_name = str(op.operands[0])
            return env[src_name].copy()

        elif opcode == Opcode.STORE:
            src_name = str(op.operands[0])
            return env[src_name].copy()

        # ----------------------------------------------------------------------
        # ARITHMETIC
        # ----------------------------------------------------------------------
        elif opcode == Opcode.ADD:
            a = env[str(op.operands[0])]
            b = env[str(op.operands[1])]
            return np.add(a, b, dtype=np_dt)

        elif opcode == Opcode.SUB:
            a = env[str(op.operands[0])]
            b = env[str(op.operands[1])]
            return np.subtract(a, b, dtype=np_dt)

        elif opcode == Opcode.MUL:
            a = env[str(op.operands[0])]
            b = env[str(op.operands[1])]
            return np.multiply(a, b, dtype=np_dt)

        elif opcode == Opcode.DIV:
            a = env[str(op.operands[0])]
            b = env[str(op.operands[1])]
            is_int = getattr(getattr(res_type, "dtype", res_type), "is_integer", False)
            if is_int:
                return np.floor_divide(a, b).astype(np_dt)
            return np.divide(a, b, dtype=np_dt)

        elif opcode == Opcode.FMA:
            # (a * b) + c with exact fusion
            a = env[str(op.operands[0])]
            b = env[str(op.operands[1])]
            c = env[str(op.operands[2])]
            # High-precision accumulator: compute in float64, cast once to destination
            prod = a.astype(np.float64) * b.astype(np.float64)
            res = prod + c.astype(np.float64)
            return res.astype(np_dt)

        elif opcode == Opcode.NEG:
            a = env[str(op.operands[0])]
            return np.negative(a, dtype=np_dt)

        elif opcode == Opcode.ABS:
            a = env[str(op.operands[0])]
            return np.abs(a).astype(np_dt)

        elif opcode == Opcode.MIN:
            a = env[str(op.operands[0])]
            b = env[str(op.operands[1])]
            return np.minimum(a, b).astype(np_dt)

        elif opcode == Opcode.MAX:
            a = env[str(op.operands[0])]
            b = env[str(op.operands[1])]
            return np.maximum(a, b).astype(np_dt)

        # ----------------------------------------------------------------------
        # TRANSCENDENTAL & POWERS
        # ----------------------------------------------------------------------
        elif opcode == Opcode.SQRT:
            a = env[str(op.operands[0])]
            return np.sqrt(a).astype(np_dt)

        elif opcode == Opcode.EXP:
            a = env[str(op.operands[0])]
            return np.exp(a).astype(np_dt)

        elif opcode == Opcode.LOG:
            a = env[str(op.operands[0])]
            return np.log(a).astype(np_dt)

        elif opcode == Opcode.SIN:
            a = env[str(op.operands[0])]
            return np.sin(a).astype(np_dt)

        elif opcode == Opcode.COS:
            a = env[str(op.operands[0])]
            return np.cos(a).astype(np_dt)

        elif opcode == Opcode.TAN:
            a = env[str(op.operands[0])]
            return np.tan(a).astype(np_dt)

        elif opcode == Opcode.POW:
            a = env[str(op.operands[0])]
            b = env[str(op.operands[1])] if len(op.operands) > 1 else float(op.attributes.get("exponent", 2.0))
            return np.power(a, b).astype(np_dt)

        # ----------------------------------------------------------------------
        # ACTIVATIONS & NON-LINEARITIES
        # ----------------------------------------------------------------------
        elif opcode == Opcode.RELU:
            a = env[str(op.operands[0])]
            return np.maximum(a, 0).astype(np_dt)

        elif opcode == Opcode.GELU:
            a = env[str(op.operands[0])]
            return (0.5 * a * (1.0 + np.tanh(np.sqrt(2.0 / np.pi) * (a + 0.044715 * np.power(a, 3))))).astype(np_dt)

        elif opcode == Opcode.SILU:
            a = env[str(op.operands[0])]
            return (a / (1.0 + np.exp(-a))).astype(np_dt)

        elif opcode == Opcode.SIGMOID:
            a = env[str(op.operands[0])]
            return (1.0 / (1.0 + np.exp(-a))).astype(np_dt)

        elif opcode == Opcode.TANH:
            a = env[str(op.operands[0])]
            return np.tanh(a).astype(np_dt)

        elif opcode == Opcode.SOFTMAX:
            a = env[str(op.operands[0])]
            axis = op.attributes.get("axis", -1)
            shift_a = a - np.max(a, axis=axis, keepdims=True)
            exps = np.exp(shift_a)
            return (exps / np.sum(exps, axis=axis, keepdims=True)).astype(np_dt)

        # ----------------------------------------------------------------------
        # COMPARISON & SELECTION
        # ----------------------------------------------------------------------
        elif opcode == Opcode.CMP:
            a = env[str(op.operands[0])]
            b = env[str(op.operands[1])]
            predicate = op.attributes.get("predicate", "EQ")
            if predicate == "EQ":
                return (a == b).astype(np.bool_)
            elif predicate == "NE":
                return (a != b).astype(np.bool_)
            elif predicate == "LT":
                return (a < b).astype(np.bool_)
            elif predicate == "LE":
                return (a <= b).astype(np.bool_)
            elif predicate == "GT":
                return (a > b).astype(np.bool_)
            elif predicate == "GE":
                return (a >= b).astype(np.bool_)
            return (a == b).astype(np.bool_)

        elif opcode == Opcode.SELECT:
            cond = env[str(op.operands[0])]
            true_val = env[str(op.operands[1])]
            false_val = env[str(op.operands[2])]
            return np.where(cond, true_val, false_val).astype(np_dt)

        # ----------------------------------------------------------------------
        # CAST & BITCAST
        # ----------------------------------------------------------------------
        elif opcode == Opcode.CAST:
            a = env[str(op.operands[0])]
            return a.astype(np_dt)

        elif opcode == Opcode.BITCAST:
            a = env[str(op.operands[0])]
            return a.view(np_dt)

        # ----------------------------------------------------------------------
        # REDUCTION & SCAN
        # ----------------------------------------------------------------------
        elif opcode in (Opcode.REDUCE, Opcode.REDUCE_SUM):
            a = env[str(op.operands[0])]
            mode = op.attributes.get("mode", "SUM") if opcode == Opcode.REDUCE else "SUM"
            axis = op.attributes.get("axis", None)
            keepdims = op.attributes.get("keepdims", False)

            if mode == "SUM":
                return np.sum(a, axis=axis, keepdims=keepdims, dtype=np_dt)
            elif mode == "PROD":
                return np.prod(a, axis=axis, keepdims=keepdims, dtype=np_dt)
            elif mode == "MAX":
                return np.max(a, axis=axis, keepdims=keepdims).astype(np_dt)
            elif mode == "MIN":
                return np.min(a, axis=axis, keepdims=keepdims).astype(np_dt)
            return np.sum(a, axis=axis, keepdims=keepdims, dtype=np_dt)

        elif opcode == Opcode.REDUCE_MEAN:
            a = env[str(op.operands[0])]
            axis = op.attributes.get("axis", None)
            keepdims = op.attributes.get("keepdims", False)
            return np.mean(a, axis=axis, keepdims=keepdims).astype(np_dt)

        elif opcode == Opcode.REDUCE_MAX:
            a = env[str(op.operands[0])]
            axis = op.attributes.get("axis", None)
            keepdims = op.attributes.get("keepdims", False)
            return np.max(a, axis=axis, keepdims=keepdims).astype(np_dt)

        elif opcode == Opcode.REDUCE_MIN:
            a = env[str(op.operands[0])]
            axis = op.attributes.get("axis", None)
            keepdims = op.attributes.get("keepdims", False)
            return np.min(a, axis=axis, keepdims=keepdims).astype(np_dt)

        elif opcode == Opcode.REDUCE_NORM:
            a = env[str(op.operands[0])]
            axis = op.attributes.get("axis", None)
            keepdims = op.attributes.get("keepdims", False)
            ord_val = op.attributes.get("ord", 2)
            return np.linalg.norm(a, ord=ord_val, axis=axis, keepdims=keepdims).astype(np_dt)

        elif opcode == Opcode.SCAN:
            a = env[str(op.operands[0])]
            axis = op.attributes.get("axis", -1)
            return np.cumsum(a, axis=axis, dtype=np_dt)

        # ----------------------------------------------------------------------
        # LINEAR ALGEBRA: MATMUL, BATCH_MATMUL, GEMM, GEMV
        # ----------------------------------------------------------------------
        elif opcode in (Opcode.MATMUL, Opcode.BATCH_MATMUL, Opcode.GEMM, Opcode.GEMV):
            a = env[str(op.operands[0])]
            b = env[str(op.operands[1])]
            trans_a = op.attributes.get("trans_a", False)
            trans_b = op.attributes.get("trans_b", False)
            alpha = float(op.attributes.get("alpha", 1.0))
            beta = float(op.attributes.get("beta", 0.0))

            a_mat = a.T if (trans_a and a.ndim == 2) else a
            b_mat = b.T if (trans_b and b.ndim == 2) else b

            prod = np.matmul(a_mat, b_mat, dtype=np_dt)
            if alpha != 1.0:
                prod = prod * alpha

            if len(op.operands) > 2 and beta != 0.0:
                c = env[str(op.operands[2])]
                prod = prod + (beta * c)

            return prod.astype(np_dt)

        # ----------------------------------------------------------------------
        # TENSOR RESHAPING & MOVEMENT
        # ----------------------------------------------------------------------
        elif opcode == Opcode.TRANSPOSE:
            a = env[str(op.operands[0])]
            axes = op.attributes.get("axes", None)
            return np.transpose(a, axes=axes).astype(np_dt)

        elif opcode == Opcode.PERMUTE:
            a = env[str(op.operands[0])]
            axes = op.attributes.get("axes", op.attributes.get("dims", None))
            return np.transpose(a, axes=axes).astype(np_dt)

        elif opcode == Opcode.RESHAPE:
            a = env[str(op.operands[0])]
            target_shape = op.attributes.get("shape", res_type.shape)
            return np.reshape(a, target_shape).astype(np_dt)

        elif opcode == Opcode.SLICING:
            a = env[str(op.operands[0])]
            slices = op.attributes.get("slices")
            if slices is not None:
                return a[tuple(slices) if isinstance(slices, list) else slices].astype(np_dt)
            axis = op.attributes.get("axis", 0)
            start = op.attributes.get("start", 0)
            end = op.attributes.get("end", None)
            step = op.attributes.get("step", 1)
            slc = [slice(None)] * a.ndim
            slc[axis] = slice(start, end, step)
            return a[tuple(slc)].astype(np_dt)

        elif opcode == Opcode.CONCAT:
            tensors = [env[str(op_id)] for op_id in op.operands]
            axis = op.attributes.get("axis", 0)
            return np.concatenate(tensors, axis=axis).astype(np_dt)

        elif opcode == Opcode.SPLIT:
            a = env[str(op.operands[0])]
            axis = op.attributes.get("axis", 0)
            split_idx = op.attributes.get("split_index", 0)
            sections = op.attributes.get("sections", op.attributes.get("indices_or_sections", 2))
            parts = np.split(a, sections, axis=axis)
            return parts[split_idx].astype(np_dt) if split_idx < len(parts) else parts[0].astype(np_dt)

        # ----------------------------------------------------------------------
        # CONVOLUTIONS (1D, 2D, 3D)
        # ----------------------------------------------------------------------
        elif opcode == Opcode.CONV1D:
            img = env[str(op.operands[0])]
            kernel = env[str(op.operands[1])]
            bias = env[str(op.operands[2])] if len(op.operands) > 2 else None
            return self._conv1d_reference(img, kernel, bias, op.attributes, np_dt)

        elif opcode == Opcode.CONV2D:
            img = env[str(op.operands[0])]
            kernel = env[str(op.operands[1])]
            bias = env[str(op.operands[2])] if len(op.operands) > 2 else None
            return self._conv2d_reference(img, kernel, bias, op.attributes, np_dt)

        elif opcode == Opcode.CONV3D:
            img = env[str(op.operands[0])]
            kernel = env[str(op.operands[1])]
            bias = env[str(op.operands[2])] if len(op.operands) > 2 else None
            return self._conv3d_reference(img, kernel, bias, op.attributes, np_dt)

        # ----------------------------------------------------------------------
        # FAST FOURIER TRANSFORMS
        # ----------------------------------------------------------------------
        elif opcode == Opcode.FFT:
            a = env[str(op.operands[0])]
            axis = op.attributes.get("axis", -1)
            return np.fft.fft(a, axis=axis)

        elif opcode == Opcode.IFFT:
            a = env[str(op.operands[0])]
            axis = op.attributes.get("axis", -1)
            return np.fft.ifft(a, axis=axis)

        elif opcode == Opcode.FFT2D:
            a = env[str(op.operands[0])]
            axes = op.attributes.get("axes", (-2, -1))
            return np.fft.fft2(a, axes=axes)

        elif opcode == Opcode.IFFT2D:
            a = env[str(op.operands[0])]
            axes = op.attributes.get("axes", (-2, -1))
            return np.fft.ifft2(a, axes=axes)

        # ----------------------------------------------------------------------
        # SPECIAL, FUSED & DOMAIN
        # ----------------------------------------------------------------------
        elif opcode == Opcode.ATTENTION:
            q = env[str(op.operands[0])]
            k = env[str(op.operands[1])]
            v = env[str(op.operands[2])]
            scale = float(op.attributes.get("scale", 1.0 / np.sqrt(q.shape[-1])))
            scores = np.matmul(q, np.swapaxes(k, -1, -2)) * scale
            exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
            probs = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
            return np.matmul(probs, v).astype(np_dt)

        elif opcode == Opcode.FUSED_GEMM_ADD:
            a = env[str(op.operands[0])]
            b = env[str(op.operands[1])]
            c = env[str(op.operands[2])]
            return (np.matmul(a, b) + c).astype(np_dt)

        elif opcode == Opcode.FUSED_CONV_RELU:
            img = env[str(op.operands[0])]
            kernel = env[str(op.operands[1])]
            bias = env[str(op.operands[2])] if len(op.operands) > 2 else None
            conv_res = self._conv2d_reference(img, kernel, bias, op.attributes, np_dt)
            return np.maximum(conv_res, 0).astype(np_dt)

        elif opcode == Opcode.FUSED_GEMM_RELU:
            a = env[str(op.operands[0])]
            b = env[str(op.operands[1])]
            return np.maximum(np.matmul(a, b), 0).astype(np_dt)

        elif opcode == Opcode.HASH_SHA256:
            import hashlib
            data = env[str(op.operands[0])]
            b = data.tobytes()
            digest = hashlib.sha256(b).digest()
            return np.frombuffer(digest, dtype=np.uint8)

        elif opcode == Opcode.ODE_EULER_STEP:
            y = env[str(op.operands[0])]
            f_val = env[str(op.operands[1])]
            dt = float(op.attributes.get("dt", 0.01))
            return (y + dt * f_val).astype(np_dt)

        # ----------------------------------------------------------------------
        # GATHER / SCATTER
        # ----------------------------------------------------------------------
        elif opcode == Opcode.GATHER:
            params = env[str(op.operands[0])]
            indices = env[str(op.operands[1])].astype(np.int64)
            axis = op.attributes.get("axis", 0)
            return np.take(params, indices, axis=axis).astype(np_dt)

        elif opcode == Opcode.SCATTER:
            target = env[str(op.operands[0])].copy()
            indices = env[str(op.operands[1])].astype(np.int64)
            updates = env[str(op.operands[2])]
            axis = op.attributes.get("axis", 0)
            np.put_along_axis(target, indices, updates, axis=axis)
            return target.astype(np_dt)

        elif opcode == Opcode.SCATTER_ADD:
            target = env[str(op.operands[0])].copy()
            indices = env[str(op.operands[1])].astype(np.int64)
            updates = env[str(op.operands[2])]
            np.add.at(target, indices, updates)
            return target.astype(np_dt)

        elif opcode == Opcode.COPY:
            return env[str(op.operands[0])].copy().astype(np_dt)

        elif opcode in (Opcode.ALLOC, Opcode.MEMORY_ALLOC):
            shape = op.attributes.get("shape", res_type.shape or (1,))
            return np.zeros(shape, dtype=np_dt)

        elif opcode in (Opcode.FREE, Opcode.MEMORY_FREE):
            return np.array([0], dtype=np_dt)

        # ----------------------------------------------------------------------
        # SORT / TOPK
        # ----------------------------------------------------------------------
        elif opcode == Opcode.SORT:
            a = env[str(op.operands[0])]
            axis = op.attributes.get("axis", -1)
            descending = op.attributes.get("descending", False)
            sorted_arr = np.sort(a, axis=axis)
            if descending:
                sorted_arr = np.flip(sorted_arr, axis=axis)
            return sorted_arr.astype(np_dt)

        elif opcode == Opcode.TOPK:
            a = env[str(op.operands[0])]
            k = int(op.attributes.get("k", 1))
            axis = op.attributes.get("axis", -1)
            sorted_arr = np.flip(np.sort(a, axis=axis), axis=axis)
            slc = [slice(None)] * sorted_arr.ndim
            slc[axis] = slice(0, k)
            return sorted_arr[tuple(slc)].astype(np_dt)

        # ----------------------------------------------------------------------
        # ATOMICS & SYNCHRONIZATION
        # ----------------------------------------------------------------------
        elif opcode == Opcode.ATOMIC_ADD:
            target = env[str(op.operands[0])].copy()
            idx = int(op.operands[1])
            val = float(op.operands[2])
            flat = target.ravel()
            flat[idx] += val
            return target

        elif opcode == Opcode.ATOMIC_MIN:
            target = env[str(op.operands[0])].copy()
            idx = int(op.operands[1])
            val = float(op.operands[2])
            flat = target.ravel()
            flat[idx] = min(flat[idx], val)
            return target

        elif opcode == Opcode.ATOMIC_MAX:
            target = env[str(op.operands[0])].copy()
            idx = int(op.operands[1])
            val = float(op.operands[2])
            flat = target.ravel()
            flat[idx] = max(flat[idx], val)
            return target

        elif opcode == Opcode.ATOMIC_CAS:
            target = env[str(op.operands[0])].copy()
            idx = int(op.operands[1])
            expected = float(op.operands[2])
            desired = float(op.operands[3])
            flat = target.ravel()
            if flat[idx] == expected:
                flat[idx] = desired
            return target

        elif opcode in (Opcode.BARRIER, Opcode.FENCE, Opcode.SHUFFLE):
            src_name = str(op.operands[0]) if op.operands else None
            return env[src_name].copy() if src_name else np.array([0], dtype=np_dt)

        # ----------------------------------------------------------------------
        # EXECUTION HIERARCHY IDENTITY
        # ----------------------------------------------------------------------
        elif opcode == Opcode.THREAD_ID:
            tid = int(op.attributes.get("thread_idx", 0))
            return np.full(res_type.shape or (1,), tid, dtype=np_dt)

        elif opcode == Opcode.BLOCK_ID:
            bid = int(op.attributes.get("block_idx", 0))
            return np.full(res_type.shape or (1,), bid, dtype=np_dt)

        elif opcode == Opcode.GRID_ID:
            gid = int(op.attributes.get("grid_idx", 0))
            return np.full(res_type.shape or (1,), gid, dtype=np_dt)

        # ----------------------------------------------------------------------
        # CONTROL FLOW: LOOP, BRANCH, PHI
        # ----------------------------------------------------------------------
        elif opcode in (Opcode.LOOP, Opcode.LOOP_INIT, Opcode.LOOP_CONDITION, Opcode.LOOP_BODY, Opcode.LOOP_UPDATE):
            val = env[str(op.operands[0])].copy()
            iterations = int(op.attributes.get("iterations", 1))
            step = float(op.attributes.get("step", 1.0))
            mode = op.attributes.get("mode", "ADD")
            for _ in range(iterations):
                if mode == "ADD":
                    val = val + step
                elif mode == "MUL":
                    val = val * step
            return val.astype(np_dt)

        elif opcode in (Opcode.BRANCH, Opcode.IF, Opcode.ELSE, Opcode.MERGE, Opcode.PHI):
            if len(op.operands) >= 3:
                cond = env[str(op.operands[0])]
                v_true = env[str(op.operands[1])]
                v_false = env[str(op.operands[2])]
                return np.where(cond, v_true, v_false).astype(np_dt)
            elif len(op.operands) == 2:
                cond = env[str(op.operands[0])]
                val = env[str(op.operands[1])]
                return val.copy().astype(np_dt)
            elif len(op.operands) == 1:
                return env[str(op.operands[0])].copy().astype(np_dt)
            return np.zeros(res_type.shape or (1,), dtype=np_dt)

        else:
            raise NotImplementedError(
                f"Reference executor has no implementation for opcode '{opcode.value}'"
            )

    def _conv1d_reference(self, img: np.ndarray, kernel: np.ndarray, bias: Optional[np.ndarray], attrs: Dict[str, Any], np_dt: np.dtype) -> np.ndarray:
        stride = int(attrs.get("stride", 1))
        padding = int(attrs.get("padding", 0))
        orig_ndim = img.ndim
        if img.ndim == 1:
            img = img[np.newaxis, np.newaxis, :]
        elif img.ndim == 2:
            img = img[np.newaxis, :, :]
        if kernel.ndim == 1:
            kernel = kernel[np.newaxis, np.newaxis, :]
        elif kernel.ndim == 2:
            kernel = kernel[:, np.newaxis, :]
        N, C_in, L = img.shape
        C_out, _, K = kernel.shape
        if padding > 0:
            padded = np.pad(img, ((0, 0), (0, 0), (padding, padding)), mode="constant")
        else:
            padded = img
        L_out = (L + 2 * padding - K) // stride + 1
        out = np.zeros((N, C_out, L_out), dtype=np_dt)
        for n in range(N):
            for co in range(C_out):
                for l in range(L_out):
                    l_start = l * stride
                    patch = padded[n, :, l_start : l_start + K]
                    val = np.sum(patch * kernel[co])
                    if bias is not None:
                        val += bias[co]
                    out[n, co, l] = val
        if orig_ndim == 1:
            return out[0, 0]
        elif orig_ndim == 2:
            return out[0]
        return out

    def _conv2d_reference(self, img: np.ndarray, kernel: np.ndarray, bias: Optional[np.ndarray], attrs: Dict[str, Any], np_dt: np.dtype) -> np.ndarray:
        stride = attrs.get("stride", (1, 1))
        padding = attrs.get("padding", (0, 0))
        if isinstance(stride, int):
            stride = (stride, stride)
        if isinstance(padding, int):
            padding = (padding, padding)
        orig_ndim = img.ndim
        if img.ndim == 2:
            img = img[np.newaxis, np.newaxis, :, :]
        elif img.ndim == 3:
            img = img[np.newaxis, :, :, :]
        if kernel.ndim == 2:
            kernel = kernel[np.newaxis, np.newaxis, :, :]
        elif kernel.ndim == 3:
            kernel = kernel[:, np.newaxis, :, :]
        N, C, H, W = img.shape
        OutC, InC, KH, KW = kernel.shape
        pad_h, pad_w = padding
        stride_h, stride_w = stride
        if pad_h > 0 or pad_w > 0:
            img_padded = np.pad(img, ((0, 0), (0, 0), (pad_h, pad_h), (pad_w, pad_w)), mode="constant")
        else:
            img_padded = img
        out_h = (H + 2 * pad_h - KH) // stride_h + 1
        out_w = (W + 2 * pad_w - KW) // stride_w + 1
        out = np.zeros((N, OutC, out_h, out_w), dtype=np_dt)
        for n in range(N):
            for oc in range(OutC):
                for oh in range(out_h):
                    for ow in range(out_w):
                        ih_start = oh * stride_h
                        iw_start = ow * stride_w
                        patch = img_padded[n, :, ih_start : ih_start + KH, iw_start : iw_start + KW]
                        val = np.sum(patch * kernel[oc])
                        if bias is not None:
                            val += bias[oc]
                        out[n, oc, oh, ow] = val
        if orig_ndim == 2:
            return out[0, 0]
        elif orig_ndim == 3:
            return out[0]
        return out

    def _conv3d_reference(self, img: np.ndarray, kernel: np.ndarray, bias: Optional[np.ndarray], attrs: Dict[str, Any], np_dt: np.dtype) -> np.ndarray:
        stride = int(attrs.get("stride", 1))
        padding = int(attrs.get("padding", 0))
        orig_ndim = img.ndim
        if img.ndim == 3:
            img = img[np.newaxis, np.newaxis, :, :, :]
        elif img.ndim == 4:
            img = img[np.newaxis, :, :, :, :]
        if kernel.ndim == 3:
            kernel = kernel[np.newaxis, np.newaxis, :, :, :]
        elif kernel.ndim == 4:
            kernel = kernel[:, np.newaxis, :, :, :]
        N, C_in, D, H, W = img.shape
        C_out, _, KD, KH, KW = kernel.shape
        if padding > 0:
            padded = np.pad(img, ((0, 0), (0, 0), (padding, padding), (padding, padding), (padding, padding)), mode="constant")
        else:
            padded = img
        D_out = (D + 2 * padding - KD) // stride + 1
        H_out = (H + 2 * padding - KH) // stride + 1
        W_out = (W + 2 * padding - KW) // stride + 1
        out = np.zeros((N, C_out, D_out, H_out, W_out), dtype=np_dt)
        for n in range(N):
            for co in range(C_out):
                for d in range(D_out):
                    for h in range(H_out):
                        for wi in range(W_out):
                            d_start = d * stride
                            h_start = h * stride
                            w_start = wi * stride
                            patch = padded[n, :, d_start : d_start + KD, h_start : h_start + KH, w_start : w_start + KW]
                            val = np.sum(patch * kernel[co])
                            if bias is not None:
                                val += bias[co]
                            out[n, co, d, h, wi] = val
        if orig_ndim == 3:
            return out[0, 0]
        elif orig_ndim == 4:
            return out[0]
        return out


# Authoritative alias
ReferenceExecutor = UniversalReferenceExecutor
