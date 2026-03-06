import asyncio
import logging
from typing import AsyncGenerator, Optional
import os
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

from backend.core.hyper_config import config

logger = logging.getLogger(__name__)

class LlmCpuInferenceEngine:
    """
    CPU-optimized LLM Inference Engine using llama.cpp.
    Features: Thread optimization, memory-mapped GGUF loading, and async token streaming.
    """
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or config.LLM_MODEL_PATH
        self.llm = None
        self._load_model()

    def _load_model(self):
        if Llama is None:
            logger.error("llama-cpp-python is not installed. LLM inference unavailable.")
            return

        if not os.path.exists(self.model_path):
            logger.info(f"LLM model not found at {self.model_path}. CPU LLM disabled.")
            return

        logger.info(f"Loading LLM {self.model_path} with {config.LLM_THREADS} threads.")
        try:
            # CPU-First GPU-Independent Configuration
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=config.LLM_CONTEXT_WINDOW,
                n_threads=config.LLM_THREADS,
                n_batch=config.LLM_BATCH_SIZE,
                n_gpu_layers=0,  # Strictly force 0 GPU layers (CPU only)
                use_mmap=True,   # Memory map the model to save RAM
                use_mlock=False, # Don't lock to RAM entirely (allows swap if memory constrained)
                verbose=False
            )
            logger.info("LLM Loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load LLM: {e}")
            self.llm = None

    async def generate_response(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """Non-streaming whole completion, executed via async thread wrapper."""
        if not self.llm:
            raise ValueError("LLM Engine is not initialized or model is missing.")
            
        # Offload the blocking C++ call to a separate thread
        def _inference():
            return self.llm(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                echo=False
            )
            
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _inference)
        return response['choices'][0]['text'].strip()

    async def stream_response(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> AsyncGenerator[str, None]:
        """Parallel streaming of tokens."""
        if not self.llm:
            raise ValueError("LLM Engine is not initialized or model is missing.")

        # Llama.cpp natively supports streaming, but it's fundamentally synchronous under the hood in python.
        # We wrapper it in chunks if necessary, but for simplest integration, we can run the generator loop async.
        
        def _stream():
            return self.llm(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                echo=False
            )
            
        # Create the strict sync generator
        streamer = _stream()
        
        loop = asyncio.get_event_loop()
        
        while True:
            # Yielding the next token safely without blocking the main async loop
            try:
                chunk = await loop.run_in_executor(None, next, streamer)
                token = chunk['choices'][0]['text']
                yield token
            except StopIteration:
                break
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                break

# Singleton instance
llm_engine = LlmCpuInferenceEngine()
