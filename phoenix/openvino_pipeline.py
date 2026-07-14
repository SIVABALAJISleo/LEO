"""
phoenix/openvino_pipeline.py
Intel OpenVINO Pipeline for iGPU Acceleration.
Converts PyTorch models to OpenVINO IR and executes them on the iGPU.
"""

import logging
import torch
import torch.nn as nn
from typing import Any, Dict

logger = logging.getLogger(__name__)

class OpenVINOAccelerator:
    """
    Orchestrates OpenVINO IR export and compilation.
    """
    def __init__(self, device: str = "GPU"):
        self.device = device
        self.core = None
        
        try:
            from openvino.runtime import Core
            self.core = Core()
            logger.info(f"[OpenVINO] Initialized. Available devices: {self.core.available_devices}")
        except ImportError:
            logger.warning("[OpenVINO] openvino package not installed. OpenVINO acceleration disabled.")

    def compile_model(self, model: nn.Module, dummy_input: torch.Tensor, model_id: str) -> Any:
        """
        Exports the model to ONNX, then to OpenVINO IR, and compiles for the target device (iGPU).
        """
        if self.core is None:
            logger.warning(f"[OpenVINO] Cannot compile {model_id}, missing core. Returning original model.")
            return model

        import os
        onnx_path = f"{model_id}.onnx"
        xml_path = f"{model_id}.xml"
        
        # 1. Export to ONNX
        torch.onnx.export(
            model, dummy_input, onnx_path,
            input_names=["input"], output_names=["output"],
            dynamic_axes={"input": {0: "batch_size", 1: "seq_len"}}
        )
        logger.info(f"[OpenVINO] Exported ONNX to {onnx_path}")
        
        # 2. Read into OpenVINO
        ov_model = self.core.read_model(onnx_path)
        
        # 3. Compile for iGPU
        compiled_model = self.core.compile_model(ov_model, self.device)
        logger.info(f"[OpenVINO] Compiled IR for {self.device} device.")
        
        return compiled_model

class OVInferenceWrapper(nn.Module):
    """
    Wraps an OpenVINO compiled model to behave like a PyTorch module.
    """
    def __init__(self, compiled_model: Any):
        super().__init__()
        self.compiled = compiled_model
        self.infer_request = self.compiled.create_infer_request()
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Convert PyTorch tensor to numpy for OpenVINO
        x_np = x.detach().cpu().numpy()
        self.infer_request.infer([x_np])
        
        # Get output and convert back to PyTorch tensor
        out_tensor = self.infer_request.get_output_tensor()
        return torch.from_numpy(out_tensor.data).clone()
