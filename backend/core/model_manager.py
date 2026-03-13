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

    async def get_model(self, version: str = "v1"):
        async with self._lock:
            if not self.initialized:
                logger.info("initializing_model_manager", version=version)
                from rag.inference import LocalInference
                # In a real system, version would map to a specific path
                self.model = LocalInference()
                self.initialized = True
                self.current_version = version
        return self.model

    async def generate_safe(self, prompt: str, max_tokens: int = 512):
        """
        Gated inference with version tracking and telemetry.
        """
        model = await self.get_model()
        start = time.time()
        async with self._semaphore:
            try:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, model.generate, prompt, max_tokens)
                duration = time.time() - start
                logger.info("inference_success", 
                            version=getattr(self, 'current_version', 'unknown'), 
                            latency_ms=round(duration*1000, 2))
                return result
            except Exception as e:
                logger.error("inference_failure", error=str(e), version=getattr(self, 'current_version', 'unknown'))
                raise

model_manager = ModelManager()
