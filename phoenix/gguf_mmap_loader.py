"""
phoenix/gguf_mmap_loader.py
GGUF Memory-Mapped (mmap) Loader.
Allows loading models larger than available RAM by streaming directly from SSD.
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

class GGUFMemoryMappedLoader:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.is_loaded = False
        self._llm = None
        
    def load(self, n_ctx: int = 2048, n_gpu_layers: int = 0) -> bool:
        """
        Initializes llama-cpp-python with mmap=True.
        """
        if not os.path.exists(self.model_path):
            logger.warning(f"[GGUF] Model not found at {self.model_path}. Please download a .gguf file.")
            return False
            
        try:
            from llama_cpp import Llama
            self._llm = Llama(
                model_path=self.model_path,
                n_ctx=n_ctx,
                n_gpu_layers=n_gpu_layers,
                use_mmap=True,        # Stream from SSD
                use_mlock=False,      # Don't lock in RAM
                verbose=False
            )
            self.is_loaded = True
            logger.info(f"[GGUF] Successfully mmap loaded {self.model_path}")
            return True
        except ImportError:
            logger.error("[GGUF] llama-cpp-python not installed. Cannot load GGUF.")
            return False
        except Exception as e:
            logger.error(f"[GGUF] Failed to load model: {e}")
            return False
            
    def generate(self, prompt: str, max_tokens: int = 128) -> str:
        if not self.is_loaded or self._llm is None:
            return "[GGUF Error: Model not loaded]"
            
        res = self._llm(
            prompt,
            max_tokens=max_tokens,
            stop=["\n", "User:"],
            echo=False
        )
        return res["choices"][0]["text"].strip()
