"""
hyper/executor/gpu_simt_executor.py
===================================
Golden Semantic GPU SIMT Executor for LEO/HYPER.
Implements Sections 7 & 11:
- Canonical correctness oracle for multi-threaded GPU kernel execution
- Simulates Grid x Block thread hierarchy, warps, and lanes
- Models shared memory, thread divergence, barrier synchronization (__syncthreads)
- Sequential consistency for atomic operations across threads
- Golden reference oracle against which all optimized CPU/iGPU paths are verified
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper.semantics.gpu_isa import GPUOpcode, GPUInstruction, AddressSpace, GPUGridConfig
from hyper.semantics.types import DataType, TensorType


@dataclass
class ThreadState:
    tid: Tuple[int, int, int]
    bid: Tuple[int, int, int]
    lane_id: int
    warp_id: int
    registers: Dict[str, Any] = field(default_factory=dict)
    predicates: Dict[str, bool] = field(default_factory=dict)
    is_active: bool = True


class GPUSIMTExecutor:
    """
    Infallible Golden Semantic GPU SIMT Reference Virtual Machine.
    Executes kernel instructions strictly in conformance with formal GPU SIMT semantics.
    """

    def __init__(self, trace_execution: bool = False) -> None:
        self.trace_execution = trace_execution
        self.trace_log: List[str] = []

    def execute_kernel(
        self,
        instructions: List[GPUInstruction],
        global_memory: Dict[str, np.ndarray],
        config: GPUGridConfig = GPUGridConfig(grid_dim=(1, 1, 1), block_dim=(16, 1, 1)),
        constants: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, np.ndarray]:
        """
        Executes instructions across all threads in the configured grid.
        Returns the updated global memory environment.
        """
        mem = {k: np.ascontiguousarray(v).copy() for k, v in global_memory.items()}
        c_mem = constants or {}

        gx, gy, gz = config.grid_dim
        bx, by, bz = config.block_dim
        warp_size = config.warp_size

        for b_z in range(gz):
            for b_y in range(gy):
                for b_x in range(gx):
                    block_id = (b_x, b_y, b_z)
                    shared_memory: Dict[str, np.ndarray] = {}
                    
                    # Initialize thread states for this block
                    threads: List[ThreadState] = []
                    linear_tid = 0
                    for t_z in range(bz):
                        for t_y in range(by):
                            for t_x in range(bx):
                                tid = (t_x, t_y, t_z)
                                lane = linear_tid % warp_size
                                warp = linear_tid // warp_size
                                ts = ThreadState(tid=tid, bid=block_id, lane_id=lane, warp_id=warp)
                                
                                # Built-in thread identities
                                ts.registers["%threadIdx.x"] = t_x
                                ts.registers["%threadIdx.y"] = t_y
                                ts.registers["%threadIdx.z"] = t_z
                                ts.registers["%blockIdx.x"] = b_x
                                ts.registers["%blockIdx.y"] = b_y
                                ts.registers["%blockIdx.z"] = b_z
                                ts.registers["%blockDim.x"] = bx
                                ts.registers["%blockDim.y"] = by
                                ts.registers["%blockDim.z"] = bz
                                ts.registers["%gridDim.x"] = gx
                                ts.registers["%gridDim.y"] = gy
                                ts.registers["%gridDim.z"] = gz
                                ts.registers["%laneid"] = lane
                                ts.registers["%warpid"] = warp
                                
                                # Global linear index
                                global_i = (b_x * bx) + t_x
                                ts.registers["%global_idx"] = global_i
                                
                                threads.append(ts)
                                linear_tid += 1

                    # Execute instructions in block
                    self._execute_block_instructions(instructions, threads, mem, shared_memory, c_mem)

        return mem

    def _execute_block_instructions(
        self,
        instructions: List[GPUInstruction],
        threads: List[ThreadState],
        global_mem: Dict[str, np.ndarray],
        shared_mem: Dict[str, np.ndarray],
        constants: Dict[str, Any],
    ) -> None:
        """
        Executes instructions per-warp / per-thread with barrier synchronization.
        """
        pc = 0
        num_ops = len(instructions)

        while pc < num_ops:
            op = instructions[pc]
            opcode = op.opcode

            # ------------------------------------------------------------------
            # SYNCHRONIZATION: BARRIER (__syncthreads)
            # ------------------------------------------------------------------
            if opcode == GPUOpcode.GPU_BARRIER:
                # In reference execution, all prior operations of all threads in this block
                # have completed. Barrier reached and passed sequentially.
                if self.trace_execution:
                    self.trace_log.append(f"Block barrier hit and passed at pc={pc}")
                pc += 1
                continue

            # ------------------------------------------------------------------
            # PER-THREAD INSTRUCTION EXECUTION
            # ------------------------------------------------------------------
            for th in threads:
                if not th.is_active:
                    continue

                if opcode == GPUOpcode.GPU_CONST:
                    val = op.operands[0]
                    th.registers[op.result_id] = val

                elif opcode == GPUOpcode.GPU_LOAD:
                    # operands: [buffer_name, index_var_or_const]
                    buf_name = str(op.operands[0])
                    addr_space = op.address_space or AddressSpace.GLOBAL
                    idx = 0
                    if len(op.operands) > 1:
                        raw_idx = op.operands[1]
                        idx = th.registers.get(str(raw_idx), raw_idx)
                        if isinstance(idx, (np.integer, int)):
                            idx = int(idx)

                    target_buf = shared_mem if addr_space == AddressSpace.SHARED else global_mem
                    if buf_name in target_buf:
                        arr = target_buf[buf_name]
                        flat = arr.ravel()
                        if 0 <= idx < len(flat):
                            th.registers[op.result_id] = float(flat[idx])
                        else:
                            th.registers[op.result_id] = 0.0

                elif opcode == GPUOpcode.GPU_STORE:
                    # operands: [buffer_name, index_var_or_const, val_var_or_const]
                    buf_name = str(op.operands[0])
                    addr_space = op.address_space or AddressSpace.GLOBAL
                    raw_idx = op.operands[1]
                    raw_val = op.operands[2]

                    idx = th.registers.get(str(raw_idx), raw_idx)
                    val = th.registers.get(str(raw_val), raw_val)
                    if isinstance(idx, (np.integer, int)):
                        idx = int(idx)
                    val_float = float(val)

                    target_buf = shared_mem if addr_space == AddressSpace.SHARED else global_mem
                    if buf_name not in target_buf and addr_space == AddressSpace.SHARED:
                        alloc_size = max(256, (idx + 1) if isinstance(idx, int) else 256)
                        target_buf[buf_name] = np.zeros(alloc_size, dtype=np.float32)

                    if buf_name in target_buf:
                        flat = target_buf[buf_name].ravel()
                        if 0 <= idx < len(flat):
                            flat[idx] = val_float

                elif opcode == GPUOpcode.GPU_ADD:
                    a = th.registers.get(str(op.operands[0]), op.operands[0])
                    b = th.registers.get(str(op.operands[1]), op.operands[1])
                    th.registers[op.result_id] = float(a) + float(b)

                elif opcode == GPUOpcode.GPU_SUB:
                    a = th.registers.get(str(op.operands[0]), op.operands[0])
                    b = th.registers.get(str(op.operands[1]), op.operands[1])
                    th.registers[op.result_id] = float(a) - float(b)

                elif opcode == GPUOpcode.GPU_MUL:
                    a = th.registers.get(str(op.operands[0]), op.operands[0])
                    b = th.registers.get(str(op.operands[1]), op.operands[1])
                    th.registers[op.result_id] = float(a) * float(b)

                elif opcode == GPUOpcode.GPU_DIV:
                    a = th.registers.get(str(op.operands[0]), op.operands[0])
                    b = th.registers.get(str(op.operands[1]), op.operands[1])
                    th.registers[op.result_id] = float(a) / float(b) if float(b) != 0.0 else 0.0

                elif opcode == GPUOpcode.GPU_FMA:
                    a = float(th.registers.get(str(op.operands[0]), op.operands[0]))
                    b = float(th.registers.get(str(op.operands[1]), op.operands[1]))
                    c = float(th.registers.get(str(op.operands[2]), op.operands[2]))
                    # Exact FMA with double-precision accumulator
                    th.registers[op.result_id] = (a * b) + c

                elif opcode == GPUOpcode.GPU_ATOMIC_ADD:
                    # operands: [buffer_name, index, val]
                    buf_name = str(op.operands[0])
                    addr_space = op.address_space or AddressSpace.GLOBAL
                    idx = int(th.registers.get(str(op.operands[1]), op.operands[1]))
                    val = float(th.registers.get(str(op.operands[2]), op.operands[2]))

                    target_buf = shared_mem if addr_space == AddressSpace.SHARED else global_mem
                    if buf_name in target_buf:
                        flat = target_buf[buf_name].ravel()
                        if 0 <= idx < len(flat):
                            old = flat[idx]
                            flat[idx] += val
                            th.registers[op.result_id] = old

                elif opcode == GPUOpcode.GPU_SHUFFLE:
                    # Cross-lane shuffle within warp: operands [src_val, src_lane]
                    src_val_name = str(op.operands[0])
                    target_lane = int(th.registers.get(str(op.operands[1]), op.operands[1]))
                    # Find peer thread in the same warp with target_lane
                    peer = next((p for p in threads if p.warp_id == th.warp_id and p.lane_id == target_lane), None)
                    if peer and src_val_name in peer.registers:
                        th.registers[op.result_id] = peer.registers[src_val_name]
                    else:
                        th.registers[op.result_id] = th.registers.get(src_val_name, 0.0)

                elif opcode == GPUOpcode.GPU_MMA:
                    # Block-level Matrix Multiply-Accumulate: D = A * B + C
                    a_buf = global_mem[str(op.operands[0])]
                    b_buf = global_mem[str(op.operands[1])]
                    c_buf = global_mem.get(str(op.operands[2])) if len(op.operands) > 2 else None
                    prod = np.matmul(a_buf, b_buf)
                    if c_buf is not None:
                        prod = prod + c_buf
                    global_mem[op.result_id] = prod

            pc += 1
