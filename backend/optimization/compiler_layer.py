"""
backend/optimization/compiler_layer.py
Subsystem 13: Compiler Layer.
Provides a unified interface for:
  - torch.compile (Inductor/Dynamo)
  - ONNX export + graph optimization
  - Constant folding, operator fusion, memory planning
  - Compilation cache to avoid re-compilation overhead
"""

import os
import time
import logging
import hashlib
import json
from typing import Any, Dict, Optional, Callable

logger = logging.getLogger(__name__)

# ── Compilation cache stored on disk ──────────────────────────────────────────
_CACHE_DIR = os.path.join(os.path.dirname(__file__), "__compile_cache__")
os.makedirs(_CACHE_DIR, exist_ok=True)


def _model_fingerprint(model_class_name: str, config: Dict) -> str:
    raw = json.dumps({"cls": model_class_name, "cfg": config}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class CompilerLayer:
    """
    Wraps a PyTorch model with the best available compilation strategy.
    Strategy priority: torch.compile (Inductor) → ONNX export → identity fallback.
    """

    def __init__(self, backend: str = "inductor", use_onnx_export: bool = True):
        self.backend = backend
        self.use_onnx_export = use_onnx_export
        self._compiled_models: Dict[str, Any] = {}

    # ── Primary: torch.compile ─────────────────────────────────────────────────
    def compile_model(self, model, model_id: str, config: Dict = None,
                      probe_input=None) -> Any:
        """
        Compiles a nn.Module using torch.compile if available,
        returning the optimized model. Falls back gracefully.
        probe_input: optional sample tensor to trigger compilation eagerly.
        """
        config = config or {}
        fp = _model_fingerprint(type(model).__name__, config)
        cache_key = f"{model_id}_{fp}"

        if cache_key in self._compiled_models:
            logger.info(f"[CompilerLayer] Cache hit for '{model_id}'. Skipping recompilation.")
            return self._compiled_models[cache_key]

        compiled = self._try_torch_compile(model, model_id, probe_input=probe_input)
        self._compiled_models[cache_key] = compiled
        return compiled

    def _try_torch_compile(self, model, model_id: str, probe_input=None):
        """Attempts torch.compile, falling back through backends: inductor -> eager -> identity."""
        try:
            import torch
            if not hasattr(torch, "compile"):
                raise ImportError("torch.compile not available (requires PyTorch >= 2.0)")

            for backend in [self.backend, "eager"]:
                try:
                    t0 = time.perf_counter()
                    compiled = torch.compile(model, backend=backend, fullgraph=False)
                    # Probe with a dummy forward pass to trigger any deferred errors NOW
                    if probe_input is not None:
                        with torch.no_grad():
                            _ = compiled(probe_input)
                    elapsed = (time.perf_counter() - t0) * 1000
                    logger.info(
                        f"[CompilerLayer] torch.compile ('{backend}') applied to '{model_id}' "
                        f"in {elapsed:.1f}ms."
                    )
                    return compiled
                except Exception as inner:
                    logger.warning(
                        f"[CompilerLayer] Backend '{backend}' failed for '{model_id}': "
                        f"{type(inner).__name__}. Trying next fallback."
                    )

            raise RuntimeError("All torch.compile backends exhausted.")

        except Exception as e:
            logger.warning(f"[CompilerLayer] torch.compile failed for '{model_id}': {e}. Using identity fallback.")
            return model

    # ── ONNX Export ────────────────────────────────────────────────────────────
    def export_to_onnx(self, model, dummy_input, model_id: str,
                       opset: int = 17) -> Optional[str]:
        """
        Exports a PyTorch model to ONNX with graph optimization.
        Returns path to the optimized .onnx file, or None on failure.
        """
        try:
            import torch
            import torch.onnx

            out_path = os.path.join(_CACHE_DIR, f"{model_id}.onnx")
            if os.path.exists(out_path):
                logger.info(f"[CompilerLayer] ONNX cache found: {out_path}")
                return out_path

            t0 = time.perf_counter()
            torch.onnx.export(
                model,
                dummy_input,
                out_path,
                opset_version=opset,
                do_constant_folding=True,       # Constant folding
                input_names=["input"],
                output_names=["output"],
                dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}}
            )
            elapsed = (time.perf_counter() - t0) * 1000
            logger.info(f"[CompilerLayer] ONNX exported: {out_path} in {elapsed:.1f}ms")

            # Optional: run onnxoptimizer if available
            self._optimize_onnx_graph(out_path)
            return out_path

        except Exception as e:
            logger.error(f"[CompilerLayer] ONNX export failed: {e}")
            return None

    def _optimize_onnx_graph(self, onnx_path: str):
        """Applies onnxoptimizer passes: operator fusion, dead-node elimination."""
        try:
            import onnx
            import onnxoptimizer

            model = onnx.load(onnx_path)
            passes = [
                "eliminate_identity",
                "eliminate_deadend",
                "fuse_consecutive_squeezes",
                "fuse_bn_into_conv",
                "fuse_add_bias_into_conv",
                "fuse_matmul_add_bias_into_gemm",
            ]
            optimized = onnxoptimizer.optimize(model, passes)
            onnx.save(optimized, onnx_path)
            logger.info(f"[CompilerLayer] ONNX graph optimized ({len(passes)} passes).")
        except ImportError:
            logger.debug("[CompilerLayer] onnxoptimizer not installed. Skipping graph optimization.")
        except Exception as e:
            logger.warning(f"[CompilerLayer] ONNX optimization failed: {e}")

    def clear_cache(self):
        """Evicts in-memory compilation cache."""
        self._compiled_models.clear()
        logger.info("[CompilerLayer] Compilation cache cleared.")
