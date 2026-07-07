import os
import logging
from typing import Generator
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

logger = logging.getLogger(__name__)

class IntelInferenceEngine:
    """
    LAYER 1 & 2: MODEL & EXECUTION ENGINE
    - Optimized for Intel CPU + Iris Xe via llama.cpp.
    - Uses GGUF quantized models (INT4).
    """
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.llm = None
        if Llama and os.path.exists(model_path):
            logger.info(f"Loading Intel-optimized model: {model_path}")
            # Hardware optimization for Intel:
            # - n_threads: Match physical cores for efficiency.
            # - n_gpu_layers: Offload to Iris Xe via Vulkan/OpenCL (if supported by build).
            # - n_batch: Small batch size for low latency.
            self.llm = Llama(
                model_path=model_path,
                n_threads=max(1, os.cpu_count() // 2), # Avoid thermal throttling
                n_gpu_layers=1, # Minimal offload to iGPU to keep bandwidth clear
                n_ctx=2048,
                n_batch=512,
                verbose=False,
                use_mlock=True # Pin to RAM to avoid swap latency
            )
        else:
            logger.warning("LLM initialization skipped: model or library missing.")

    def generate_stream(self, prompt: str, system_prompt: str = "You are a helpful AI.") -> Generator[str, None, None]:
        if not self.llm:
            yield "Local LLM offline. Falling back to deterministic logic."
            return

        full_prompt = f"<|system|>\n{system_prompt}<|end|>\n<|user|>\n{prompt}<|end|>\n<|assistant|>"
        
        response = self.llm.create_completion(
            prompt=full_prompt,
            max_tokens=512,
            stream=True,
            temperature=0.7,
            stop=["<|end|>", "User:", "Assistant:"]
        )
        
        for chunk in response:
            text = chunk['choices'][0]['text']
            if text:
                yield text
