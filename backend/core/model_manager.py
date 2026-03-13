import os
import time
import asyncio
from typing import Optional
import structlog

logger = structlog.get_logger()

class ModelManager:
    """
    Singleton Manager for AI Models.
    Ensures only one instance is loaded and gates inference via a semaphore.
    """
    _instance = None
    _lock = asyncio.Lock()
    _semaphore = asyncio.Semaphore(1) # Only 1 concurrent inference on CPU

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.initialized = False
        return cls._instance

    async def get_model(self):
        async with self._lock:
            if not self.initialized:
                logger.info("initializing_model_manager")
                from rag.inference import LocalInference
                self.model = LocalInference()
                self.initialized = True
        return self.model

    async def generate_safe(self, prompt: str, max_tokens: int = 512):
        """
        Gated inference to prevent CPU spikes and OOM.
        """
        model = await self.get_model()
        async with self._semaphore:
            # Run inference in a threadpool to prevent blocking the event loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, model.generate, prompt, max_tokens)
            return result

model_manager = ModelManager()
