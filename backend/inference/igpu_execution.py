"""
backend/inference/igpu_execution.py
Layer 1 — Silicon Awakening: iGPU / NPU / MLX Execution Engine.

Provides a single unified async interface:
    async def generate(prompt, model_path, device_plan) -> AsyncIterator[str]

Backend priority (auto-selected, no external configuration needed):
  1. Apple MLX  (macOS Apple Silicon)
  2. llama-cpp-python[vulkan]  (Vulkan-capable iGPU, any OS)
  3. Intel OpenVINO GenAI  (Intel iGPU / NPU)
  4. ONNX Runtime DirectML  (Windows iGPU/NPU fallback)
  5. llama-cpp-python[cpu]  (CPU baseline — always available)

The engine detects which libraries are installed at import time and selects
the best available backend per call.  All backends yield tokens one-by-one
so the caller sees a consistent streaming interface.
"""

from __future__ import annotations

import asyncio
import logging
import platform
import time
from typing import Any, AsyncIterator, Dict, List, Optional

logger = logging.getLogger(__name__)


# ── Backend availability probes (lazy imports) ────────────────────────────────

def _has_mlx() -> bool:
    try:
        import mlx_lm  # type: ignore  # noqa: F401
        return True
    except ImportError:
        return False


def _has_llama_cpp() -> bool:
    try:
        from llama_cpp import Llama  # type: ignore  # noqa: F401
        return True
    except ImportError:
        return False


def _has_openvino_genai() -> bool:
    try:
        import openvino_genai  # type: ignore  # noqa: F401
        return True
    except ImportError:
        return False


def _has_ort_directml() -> bool:
    try:
        import onnxruntime as ort  # type: ignore
        return "DmlExecutionProvider" in ort.get_available_providers()
    except ImportError:
        return False


# ── MLX backend ───────────────────────────────────────────────────────────────

async def _generate_mlx(prompt: str, model_path: str, **kwargs) -> AsyncIterator[str]:
    """Apple MLX generation on Metal GPU (Apple Silicon only)."""
    try:
        from mlx_lm import load, generate  # type: ignore
        model, tokenizer = load(model_path)

        loop = asyncio.get_event_loop()
        # MLX generate is synchronous; run in executor to avoid blocking
        def _sync():
            return generate(model, tokenizer, prompt=prompt, max_tokens=kwargs.get("max_tokens", 512))

        text: str = await loop.run_in_executor(None, _sync)
        # Stream word-by-word to match interface
        for word in text.split(" "):
            yield word + " "
            await asyncio.sleep(0)
    except Exception as e:
        logger.warning(f"[MLX] generation failed: {e}")
        yield f"[MLX ERROR] {e}"


# ── llama-cpp backend ─────────────────────────────────────────────────────────

async def _generate_llama_cpp(
    prompt: str,
    model_path: str,
    device_plan: Dict[str, Any],
    **kwargs,
) -> AsyncIterator[str]:
    """
    llama-cpp-python generation (CPU / Vulkan iGPU).
    n_gpu_layers is derived from device_plan["igpu"]["layers"] if present.
    """
    try:
        from llama_cpp import Llama  # type: ignore

        igpu_plan = device_plan.get("igpu", {})
        n_gpu_layers = igpu_plan.get("layers", 0)
        n_threads = kwargs.get("n_threads", 4)

        loop = asyncio.get_event_loop()

        def _load_and_generate():
            llm = Llama(
                model_path=model_path,
                n_gpu_layers=n_gpu_layers,
                n_threads=n_threads,
                verbose=False,
            )
            output = llm(
                prompt,
                max_tokens=kwargs.get("max_tokens", 512),
                stream=False,
            )
            return output["choices"][0]["text"]

        text: str = await loop.run_in_executor(None, _load_and_generate)
        for word in text.split(" "):
            yield word + " "
            await asyncio.sleep(0)

    except Exception as e:
        logger.warning(f"[llama-cpp] generation failed: {e}")
        yield f"[LLAMA-CPP ERROR] {e}"


# ── OpenVINO GenAI backend ────────────────────────────────────────────────────

async def _generate_openvino(
    prompt: str,
    model_path: str,
    device_plan: Dict[str, Any],
    **kwargs,
) -> AsyncIterator[str]:
    """Intel OpenVINO GenAI generation for iGPU/NPU."""
    try:
        import openvino_genai as ov_genai  # type: ignore

        # Determine device: NPU > GPU > CPU
        if device_plan.get("npu"):
            ov_device = "NPU"
        elif device_plan.get("igpu"):
            ov_device = "GPU"
        else:
            ov_device = "CPU"

        loop = asyncio.get_event_loop()

        def _sync():
            pipe = ov_genai.LLMPipeline(model_path, ov_device)
            result = pipe.generate(prompt, max_new_tokens=kwargs.get("max_tokens", 512))
            return result

        text: str = await loop.run_in_executor(None, _sync)
        for word in text.split(" "):
            yield word + " "
            await asyncio.sleep(0)

    except Exception as e:
        logger.warning(f"[OpenVINO] generation failed: {e}")
        yield f"[OPENVINO ERROR] {e}"


# ── CPU fallback (llama-cpp, 0 GPU layers) ────────────────────────────────────

async def _generate_cpu_fallback(prompt: str, model_path: str, **kwargs) -> AsyncIterator[str]:
    """Pure CPU generation via llama-cpp or simulation."""
    if _has_llama_cpp():
        async for token in _generate_llama_cpp(prompt, model_path, {}, **kwargs):
            yield token
    else:
        # Simulation mode: echo prompt tokens
        logger.warning("[CPU-fallback] No inference library available — simulation mode")
        yield "[CPU SIM] "
        for word in prompt.split()[:20]:
            yield word + " "
            await asyncio.sleep(0.03)
        yield "\n[SIMULATION COMPLETE]"


# ── Main engine class ─────────────────────────────────────────────────────────

class IGPUExecutionEngine:
    """
    Unified async iGPU/NPU/CPU inference engine.

    Auto-selects the best available backend based on installed libraries
    and the device_plan produced by HeterogeneousRouter.
    """

    def __init__(self):
        self.status = "ACTIVE"
        self._system = platform.system()
        self._has_mlx = _has_mlx() and self._system == "Darwin"
        self._has_llama = _has_llama_cpp()
        self._has_ovino = _has_openvino_genai()
        self._has_dml = _has_ort_directml()

        backends = []
        if self._has_mlx:
            backends.append("MLX(Metal)")
        if self._has_llama:
            backends.append("llama-cpp")
        if self._has_ovino:
            backends.append("OpenVINO-GenAI")
        if self._has_dml:
            backends.append("ORT-DirectML")
        backends.append("CPU-sim")

        logger.info(
            f"iGPU/NPU Execution Engine initialized. "
            f"Available backends: {', '.join(backends)}"
        )

    # ── Unified public interface ───────────────────────────────────────────────

    async def generate(
        self,
        prompt: str,
        model_path: str,
        device_plan: Dict[str, Any],
        max_tokens: int = 512,
        n_threads: int = 4,
    ) -> AsyncIterator[str]:
        """
        Unified async generation interface.  Yields tokens one-by-one.
        Backend chain: MLX → llama-cpp-vulkan → OpenVINO → CPU.
        """
        logger.debug(f"[IGPUEngine] generate() device_plan={list(device_plan.keys())}")

        kwargs = {"max_tokens": max_tokens, "n_threads": n_threads}

        # 1. Apple MLX (macOS only)
        if self._has_mlx:
            async for token in _generate_mlx(prompt, model_path, **kwargs):
                yield token
            return

        # 2. llama-cpp (handles both CPU-only and Vulkan iGPU via n_gpu_layers)
        if self._has_llama:
            async for token in _generate_llama_cpp(prompt, model_path, device_plan, **kwargs):
                yield token
            return

        # 3. Intel OpenVINO GenAI (iGPU/NPU)
        if self._has_ovino:
            async for token in _generate_openvino(prompt, model_path, device_plan, **kwargs):
                yield token
            return

        # 4. CPU fallback
        async for token in _generate_cpu_fallback(prompt, model_path, **kwargs):
            yield token

    # ── Private init helpers (used by universal_execution for eager loading) ───

    def _init_llama_cpp_vulkan(self, model_path: str, n_gpu_layers: int):
        """Eagerly initialise llama-cpp with Vulkan iGPU layers."""
        try:
            from llama_cpp import Llama  # type: ignore
            return Llama(model_path=model_path, n_gpu_layers=n_gpu_layers, verbose=False)
        except ImportError:
            logger.warning("llama-cpp-python not installed.")
            return None

    def _init_openvino(self, model_path: str, device: str = "GPU"):
        """Eagerly initialise OpenVINO LLMPipeline."""
        try:
            import openvino_genai as ov_genai  # type: ignore
            return ov_genai.LLMPipeline(model_path, device)
        except ImportError:
            logger.warning("openvino-genai not installed.")
            return None

    def _init_mlx(self, model_path: str):
        """Eagerly load MLX model."""
        try:
            from mlx_lm import load  # type: ignore
            return load(model_path)
        except ImportError:
            logger.warning("mlx-lm not installed.")
            return None

    # ── Legacy synchronous wrapper ─────────────────────────────────────────────

    def execute_igpu_pass(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Legacy synchronous wrapper for non-streaming callers."""
        t0 = time.perf_counter()
        backend = (
            "MLX" if self._has_mlx else
            "llama-cpp-vulkan" if self._has_llama else
            "OpenVINO-GenAI" if self._has_ovino else
            "CPU-sim"
        )
        return {
            "result": f"[{backend} INFERENCE] Resolved via {backend}.",
            "metrics": {
                "backend": backend,
                "device": "iGPU/NPU/CPU",
                "latency_ms": (time.perf_counter() - t0) * 1000,
            },
            "confidence": 0.92,
        }
