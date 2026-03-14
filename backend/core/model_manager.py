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

    async def get_model(self, tier: str = "small"):
        """
        Retrieves a model based on tier: 'tiny', 'small', or 'large'.
        large -> Remote Model Server
        small -> Local 1.1B Model
        tiny -> Local 0.5B / Fast Mock
        """
        async with self._lock:
            if not self.initialized:
                server_url = os.getenv("MODEL_SERVER_URL")
                self.remote_model = None
                if server_url:
                    from backend.core.remote_inference import RemoteInference
                    self.remote_model = RemoteInference(server_url)
                
                from rag.inference import LocalInference
                self.local_model = LocalInference() # Small (1.1B)
                self.tiny_model = LocalInference(n_threads=2) # Simulated tiny
                
                self.initialized = True
        
        if tier == "large" and self.remote_model:
            return self.remote_model
        elif tier == "tiny":
            return self.tiny_model
        return self.local_model

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

    async def generate_stream(self, prompt: str, max_tokens: int = 512):
        """
        Gated streaming inference.
        """
        model = await self.get_model()
        async with self._semaphore:
            try:
                # We expect model.generate(..., stream=True) to return an iterator
                # Since model.generate is sync (llama-cpp), we run the iteration logic carefully
                # or assume it's safe if it's a generator.
                logger.info("inference_stream_start")
                stream = model.generate(prompt, max_tokens=max_tokens, stream=True)
                for chunk in stream:
                    if isinstance(chunk, dict) and 'choices' in chunk:
                        text = chunk['choices'][0]['text']
                        yield text
                        await asyncio.sleep(0) # Yield control
            except Exception as e:
                logger.error("inference_stream_failure", error=str(e))
                yield f"Error: {e}"

model_manager = ModelManager()
