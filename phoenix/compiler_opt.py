"""
phoenix/compiler_opt.py
Compiler & ONNX Optimizations.
Applies torch.compile and Graph Fusions to maximize hardware execution efficiency.
"""

import logging
import torch
import torch.nn as nn
from typing import Any

logger = logging.getLogger(__name__)

class CompilerOptimizer:
    def __init__(self):
        # Set thread affinity for Intel Core i5-12450H (8 Cores: 4P + 4E)
        # 12 threads total. Optimal intra-op threads is usually physical core count.
        torch.set_num_threads(8) 
        torch.set_num_interop_threads(2)
        logger.info("[Compiler] Thread affinity configured for i5-12450H (8 threads intra-op).")

    def optimize_pytorch(self, model: nn.Module) -> nn.Module:
        """
        Applies torch.compile with inductor backend for operator fusion and kernel selection.
        """
        try:
            # Requires PyTorch 2.0+
            compiled_model = torch.compile(model, mode="reduce-overhead", backend="inductor")
            logger.info("[Compiler] Successfully applied torch.compile (reduce-overhead).")
            return compiled_model
        except Exception as e:
            logger.warning(f"[Compiler] torch.compile failed or unsupported: {e}. Returning eager model.")
            return model

    def optimize_onnx(self, model_path: str, output_path: str):
        """
        Applies ONNX Runtime graph optimizations (Constant Folding, Node Fusion).
        """
        try:
            import onnxruntime as ort
            sess_options = ort.SessionOptions()
            # Enable all graph optimizations (Level 99)
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            sess_options.optimized_model_filepath = output_path
            
            # Creating the session applies and saves the optimized model
            ort.InferenceSession(model_path, sess_options, providers=['CPUExecutionProvider'])
            logger.info(f"[Compiler] ONNX optimizations applied. Saved to {output_path}")
        except ImportError:
            logger.warning("[Compiler] onnxruntime not installed. Skipping ONNX optimization.")
        except Exception as e:
            logger.error(f"[Compiler] ONNX optimization failed: {e}")
