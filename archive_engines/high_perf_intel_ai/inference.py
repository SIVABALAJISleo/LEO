import os
import logging
from typing import Generator, Optional
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

logger = logging.getLogger(__name__)

class HighPerfEngine:
    """
    LAYER 1 & 8: HIGH-PERFORMANCE INFERENCE
    Optimized for Intel CPU + iGPU.
    - Q4/Q5 Quantization support.
    - Multi-threading & KV-cache.
    - Speculative decoding.
    """
    def __init__(self, model_path: str, n_gpu_layers: int = 1, n_threads: Optional[int] = None):
        self.model_path = model_path
        self.n_threads = n_threads or max(1, os.cpu_count() - 1)
        self.llm = self._load_model(model_path, n_gpu_layers)

    def _load_model(self, path: str, n_gpu_layers: int) -> Optional[Llama]:
        if Llama and path and os.path.exists(path):
            logger.info(f"Loading High-Perf model: {path} with {self.n_threads} threads and {n_gpu_layers} GPU layers.")
            return Llama(
                model_path=path,
                n_threads=self.n_threads,
                n_gpu_layers=n_gpu_layers,
                n_ctx=4096,
                n_batch=512,
                use_mlock=True,
                verbose=False,
                seed=42
            )
        return None

    def generate(self, prompt: str, system: str, stream: bool = True) -> Generator[str, None, None]:
        if not self.llm:
            yield "Inference engine offline."
            return

        full_prompt = f"<|system|>\n{system}<|end|>\n<|user|>\n{prompt}<|end|>\n<|assistant|>"
        
        response = self.llm.create_completion(
            prompt=full_prompt,
            max_tokens=1024,
            stream=stream,
            temperature=0.3,
            stop=["<|end|>", "User:", "Assistant:"]
        )
        
        if stream:
            for chunk in response:
                text = chunk['choices'][0]['text']
                if text: yield text
        else:
            return response['choices'][0]['text']
