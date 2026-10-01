"""
hyper/backends/igpu_backend.py
==============================
Intel UHD Integrated GPU Backend for LEO/HYPER.
Uses OpenVINO GPU runtime to execute on-die Intel UHD Graphics silicon.
Detects runtime availability dynamically; if unavailable, strictly reports
BACKEND_UNAVAILABLE with zero fake/simulated execution.
"""

from __future__ import annotations
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from hyper.universal_ir.opcodes import Opcode
from hyper.universal_ir.instruction import UniversalOp
from hyper.universal_ir.program import UniversalIRProgram


class IntelUhdBackend:
    """
    Genuine Intel UHD Graphics execution backend via OpenVINO.
    """

    def __init__(self) -> None:
        self._available: bool = False
        self._device_name: str = "Unavailable"
        self._core: Optional[Any] = None

        try:
            import openvino as ov
            self._core = ov.Core()
            if "GPU" in self._core.available_devices:
                self._available = True
                self._device_name = self._core.get_property("GPU", "FULL_DEVICE_NAME")
            else:
                self._available = False
                self._device_name = "Intel UHD (OpenVINO GPU not in available_devices)"
        except Exception as e:
            self._available = False
            self._device_name = f"Unavailable ({str(e)})"

    def is_available(self) -> bool:
        return self._available

    def get_device_name(self) -> str:
        return self._device_name

    def execute(
        self,
        program: UniversalIRProgram,
        inputs: Dict[str, np.ndarray],
    ) -> Tuple[Dict[str, np.ndarray], float]:
        """
        Executes supported operations on genuine Intel UHD iGPU silicon via OpenVINO.
        If GPU is unavailable, raises RuntimeError("BACKEND_UNAVAILABLE").
        """
        if not self._available or self._core is None:
            raise RuntimeError("BACKEND_UNAVAILABLE: Intel UHD GPU is not accessible via OpenVINO runtime")

        import openvino as ov
        import openvino.opset13 as ops

        t0 = time.perf_counter()

        # Build OpenVINO computational graph from Universal IR
        ov_params: Dict[str, Any] = {}
        for inp_name, tensor_type in program.inputs.items():
            np_dt = tensor_type.dtype.to_numpy_dtype()
            ov_params[inp_name] = ops.parameter(list(tensor_type.shape), np_dt, name=inp_name)

        ov_nodes: Dict[str, Any] = dict(ov_params)

        for op in program.instructions:
            opcode = op.opcode
            res_dt = op.result_type.dtype.to_numpy_dtype()

            if opcode in (Opcode.MATMUL, Opcode.GEMM):
                a_node = ov_nodes[str(op.operands[0])]
                b_node = ov_nodes[str(op.operands[1])]
                trans_a = op.attributes.get("trans_a", False)
                trans_b = op.attributes.get("trans_b", False)
                mm = ops.matmul(a_node, b_node, trans_a, trans_b)
                ov_nodes[op.result_id] = mm

            elif opcode == Opcode.ADD:
                a_node = ov_nodes[str(op.operands[0])]
                b_node = ov_nodes[str(op.operands[1])]
                ov_nodes[op.result_id] = ops.add(a_node, b_node)

            elif opcode == Opcode.SUB:
                a_node = ov_nodes[str(op.operands[0])]
                b_node = ov_nodes[str(op.operands[1])]
                ov_nodes[op.result_id] = ops.subtract(a_node, b_node)

            elif opcode == Opcode.MUL:
                a_node = ov_nodes[str(op.operands[0])]
                b_node = ov_nodes[str(op.operands[1])]
                ov_nodes[op.result_id] = ops.multiply(a_node, b_node)

            elif opcode == Opcode.DIV:
                a_node = ov_nodes[str(op.operands[0])]
                b_node = ov_nodes[str(op.operands[1])]
                ov_nodes[op.result_id] = ops.divide(a_node, b_node)

            elif opcode == Opcode.FMA:
                a_node = ov_nodes[str(op.operands[0])]
                b_node = ov_nodes[str(op.operands[1])]
                c_node = ov_nodes[str(op.operands[2])]
                prod = ops.multiply(a_node, b_node)
                ov_nodes[op.result_id] = ops.add(prod, c_node)

            elif opcode == Opcode.RELU:
                a_node = ov_nodes[str(op.operands[0])]
                ov_nodes[op.result_id] = ops.relu(a_node)

            else:
                # Unsupported iGPU opcode: fail closed to indicate partial iGPU support
                raise NotImplementedError(
                    f"Intel UHD OpenVINO backend does not yet support opcode '{opcode.value}'"
                )

        # Assemble OpenVINO Model
        out_nodes = [ov_nodes[out_name] for out_name in program.outputs]
        param_nodes = list(ov_params.values())
        model = ov.Model(out_nodes, param_nodes, program.name)

        # Compile for genuine Intel UHD GPU device
        compiled_model = self._core.compile_model(model, "GPU")
        infer_req = compiled_model.create_infer_request()

        # Feed input tensors
        feed_dict = {ov_params[k]: inputs[k].astype(ov_params[k].get_element_type().to_dtype()) for k in inputs}
        raw_outputs = infer_req.infer(feed_dict)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        # Extract output mapping
        results: Dict[str, np.ndarray] = {}
        for out_name, out_node in zip(program.outputs, out_nodes):
            results[out_name] = raw_outputs[out_node]

        return results, elapsed_ms
