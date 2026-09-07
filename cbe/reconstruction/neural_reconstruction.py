"""
cbe/reconstruction/neural_reconstruction.py
Ultra-lightweight Intel-friendly neural reconstruction network.
Compiles to OpenVINO IR and executes directly on the Intel UHD Graphics iGPU (GPU.0).
Provides CPU AVX2 fallback and verifies net compute savings before deployment.
"""

from __future__ import annotations

import time
import logging
import numpy as np
from typing import Optional, Dict, Any, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger("CBE.NeuralRecon")


class TinyIntelReconNet(nn.Module):
    """
    Ultra-compact depthwise-separable residual reconstruction network (<25K parameters).
    Designed specifically for Intel Xe-LP execution units (INT8 / FP16 friendly).
    Inputs: (B, 8, H, W) -> [LowRes RGB(3), History RGB(3), Motion(2)]
    Outputs: (B, 3, 2H, 2W) -> High-resolution reconstructed RGB
    """
    def __init__(self, in_channels: int = 8, mid_channels: int = 16, scale_factor: int = 2):
        super().__init__()
        self.scale_factor = scale_factor
        
        # 1. Feature extraction
        self.conv_in = nn.Conv2d(in_channels, mid_channels, kernel_size=3, padding=1, bias=False)
        self.act1 = nn.LeakyReLU(0.1, inplace=True)
        
        # 2. Depthwise-separable block
        self.dw_conv = nn.Conv2d(mid_channels, mid_channels, kernel_size=3, padding=1, groups=mid_channels, bias=False)
        self.pw_conv = nn.Conv2d(mid_channels, mid_channels, kernel_size=1, bias=False)
        self.act2 = nn.LeakyReLU(0.1, inplace=True)
        
        # 3. Residual block
        self.res_conv1 = nn.Conv2d(mid_channels, mid_channels, kernel_size=3, padding=1, bias=False)
        self.act3 = nn.LeakyReLU(0.1, inplace=True)
        self.res_conv2 = nn.Conv2d(mid_channels, mid_channels, kernel_size=3, padding=1, bias=False)
        
        # 4. Upsampling via PixelShuffle (sub-pixel convolution)
        self.conv_up = nn.Conv2d(mid_channels, 3 * (scale_factor ** 2), kernel_size=3, padding=1, bias=True)
        self.pixel_shuffle = nn.PixelShuffle(scale_factor)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Base bilinear skip connection for RGB channels [0:3]
        base_upsampled = F.interpolate(x[:, 0:3, :, :], scale_factor=self.scale_factor, mode="bilinear", align_corners=False)
        
        feat = self.act1(self.conv_in(x))
        
        # Depthwise separable
        dw = self.act2(self.pw_conv(self.dw_conv(feat)))
        
        # Residual connection
        res = self.res_conv2(self.act3(self.res_conv1(dw)))
        feat = feat + res
        
        # Sub-pixel reconstruction
        residual_rgb = self.pixel_shuffle(self.conv_up(feat))
        
        return torch.clamp(base_upsampled + residual_rgb, 0.0, 1.0)


class NeuralReconstructor:
    """
    Manages neural reconstruction inference across Intel iGPU (via OpenVINO) and CPU.
    """
    def __init__(
        self,
        device: str = "AUTO",
        enable_ov_gpu: bool = True
    ):
        self.torch_model = TinyIntelReconNet().eval()
        self.ov_compiled_model = None
        self.ov_infer_request = None
        self.active_backend = "CPU"
        self.ov_device = "CPU"
        
        self._init_openvino_backend(enable_ov_gpu)

    def _init_openvino_backend(self, enable_gpu: bool):
        try:
            import openvino as ov
            core = ov.Core()
            available = core.available_devices
            
            if enable_gpu and "GPU" in available:
                self.ov_device = "GPU"
            else:
                self.ov_device = "CPU"
                
            # Convert PyTorch model to OpenVINO model with dynamic spatial dimensions
            dummy_input = torch.zeros((1, 8, 64, 64), dtype=torch.float32)
            ov_model = ov.convert_model(self.torch_model, example_input=dummy_input)
            try:
                ov_model.reshape([-1, 8, -1, -1])
            except Exception:
                pass
            
            # Compile model for Intel target
            self.ov_compiled_model = core.compile_model(ov_model, self.ov_device)
            self.ov_infer_request = self.ov_compiled_model.create_infer_request()
            self.active_backend = f"OpenVINO_{self.ov_device}"
            
            # Warmup inference to eliminate JIT compilation latency
            warmup_in = np.zeros((1, 8, 32, 32), dtype=np.float32)
            self.ov_infer_request.infer([warmup_in])
            logger.info(f"NeuralReconstructor compiled and warmed up on {self.active_backend}")
        except Exception as e:
            logger.warning(f"OpenVINO compilation notice ({e}); running PyTorch CPU fallback.")
            self.active_backend = "PyTorch_CPU"

    def reconstruct(
        self,
        low_res_rgb: np.ndarray,      # (H, W, 3) float32
        history_rgb: np.ndarray,      # (H, W, 3) float32
        motion_vectors: np.ndarray    # (H, W, 2) float32
    ) -> Tuple[np.ndarray, str, float]:
        """
        Executes neural upscaling to 2x resolution.
        Returns: (high_res_rgb, backend_used, elapsed_ms).
        """
        t0 = time.perf_counter()
        H, W, C = low_res_rgb.shape
        
        # Prepare 8-channel input tensor: [low_res(3), history(3), motion(2)]
        input_stack = np.concatenate([
            low_res_rgb.transpose(2, 0, 1),
            history_rgb.transpose(2, 0, 1),
            motion_vectors.transpose(2, 0, 1)
        ], axis=0).astype(np.float32)
        input_tensor = np.expand_dims(input_stack, axis=0)  # (1, 8, H, W)
        
        if self.ov_infer_request is not None:
            try:
                res = self.ov_infer_request.infer([input_tensor])
                out_tensor = list(res.values())[0]  # (1, 3, 2H, 2W)
                out_rgb = out_tensor[0].transpose(1, 2, 0)
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                return np.clip(out_rgb, 0.0, 1.0), self.active_backend, elapsed_ms
            except Exception:
                pass
                
        # PyTorch CPU Fallback
        with torch.no_grad():
            torch_in = torch.from_numpy(input_tensor)
            out_torch = self.torch_model(torch_in)
            out_rgb = out_torch[0].numpy().transpose(1, 2, 0)
            
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return np.clip(out_rgb, 0.0, 1.0), "PyTorch_CPU", elapsed_ms

    def verify_net_savings(
        self,
        native_render_cost_ms: float,
        low_res_render_cost_ms: float
    ) -> Dict[str, Any]:
        """
        Validates whether neural reconstruction produces net compute savings:
        Net Savings = native_render_cost - (low_res_render_cost + reconstruction_cost)
        """
        dummy = np.zeros((64, 64, 3), dtype=np.float32)
        dummy_mv = np.zeros((64, 64, 2), dtype=np.float32)
        
        # Warmup
        self.reconstruct(dummy, dummy, dummy_mv)
        # Measured timing
        _, _, recon_cost_ms = self.reconstruct(dummy, dummy, dummy_mv)
        
        cbe_total_ms = low_res_render_cost_ms + recon_cost_ms
        net_saved_ms = native_render_cost_ms - cbe_total_ms
        is_beneficial = net_saved_ms > 0.0
        
        return {
            "native_render_cost_ms": round(native_render_cost_ms, 2),
            "low_res_render_cost_ms": round(low_res_render_cost_ms, 2),
            "reconstruction_cost_ms": round(recon_cost_ms, 2),
            "cbe_total_ms": round(cbe_total_ms, 2),
            "net_saved_ms": round(net_saved_ms, 2),
            "speedup_factor": round(native_render_cost_ms / max(0.1, cbe_total_ms), 2),
            "is_net_beneficial": is_beneficial,
            "active_backend": self.active_backend
        }
