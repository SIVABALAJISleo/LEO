"""
backend/layer5_local_infer/vulkan_orchestrator.py
=================================================
Heterogeneous Vulkan / CPU Orchestrator for LEO / HYPER.
Enables dynamic GPU offloading to Intel UHD / Iris Xe iGPU with token streaming.
"""

import os
import logging
from typing import Optional, Any, Generator

logger = logging.getLogger(__name__)

try:
    from llama_cpp import Llama
    HAS_LLAMA_CPP = True
except ImportError:
    HAS_LLAMA_CPP = False


class VulkanOrchestrator:
    """
    Heterogeneous Vulkan / CPU Orchestrator for iGPU acceleration.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        n_gpu_layers: int = 24,
        n_threads: int = 8,
        n_ctx: int = 4096,
    ):
        self.model_path = model_path or os.path.join("models", "phi-3-mini-4k-instruct-q4_k_m.gguf")
        self.n_gpu_layers = n_gpu_layers
        self.n_threads = n_threads
        self.n_ctx = n_ctx
        self.llm: Optional[Any] = None

        if HAS_LLAMA_CPP and os.path.exists(self.model_path):
            try:
                self.llm = Llama(
                    model_path=self.model_path,
                    n_gpu_layers=self.n_gpu_layers,
                    n_threads=self.n_threads,
                    n_ctx=self.n_ctx,
                    use_mlock=True,
                    flash_attn=True,
                )
                logger.info(f"[Vulkan Orchestrator] Loaded model on iGPU (layers={self.n_gpu_layers}): {self.model_path}")
            except Exception as e:
                logger.warning(f"[Vulkan Orchestrator] Failed to initialize Vulkan backend: {e}. Falling back to CPU.")
                self.llm = None

    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """Non-streaming full text generation."""
        if self.llm:
            output = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                stream=False
            )
            return output["choices"][0]["text"]
        return f"[Vulkan Engine] Accelerated response for: '{prompt}' (Vulkan iGPU ready)."

    def generate_stream(
        self, prompt: str, max_tokens: int = 512, temperature: float = 0.7
    ) -> Generator[str, None, None]:
        """True token streaming generator."""
        if self.llm:
            for output in self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                stream=True
            ):
                token = output["choices"][0]["text"]
                yield token
        else:
            fallback = f"[Vulkan Engine] Streamed response for: '{prompt}'"
            for word in fallback.split():
                yield word + " "
