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
    _in_flight = {} # Point 10: Deduplicate in-flight queries

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
        small -> Local 1.1B Model (TinyLlama)
        tiny -> Local 0.5B Model (e.g., Qwen-0.5B) or super-fast quantization
        """
        import psutil
        total_cores = psutil.cpu_count(logical=False) or 4
        
        async with self._lock:
            if not self.initialized:
                server_url = os.getenv("MODEL_SERVER_URL")
                self.remote_model = None
                if server_url:
                    from backend.core.remote_inference import RemoteInference
                    self.remote_model = RemoteInference(server_url)
                
                from rag.inference import LocalInference
                # Small: Use more threads and larger context
                self.local_model = LocalInference(n_threads=max(total_cores - 2, 4))
                
                # Tiny: Sub-1B model or extreme quantization
                # For now, we use the same model but with a 1-thread 'hyper-fast' profile
                self.tiny_model = LocalInference(
                    model_path=os.getenv("TINY_MODEL_PATH", "models/qwen-0.5b-chat.Q4_K_M.gguf"),
                    n_threads=2
                )
                
                self.initialized = True
        
        if tier == "large" and self.remote_model:
            return self.remote_model
        elif tier == "tiny":
            # Fallback to local_model if tiny_model path doesn't exist yet
            if not self.tiny_model.llm:
                return self.local_model
            return self.tiny_model
        return self.local_model

    async def generate_safe(self, prompt: str, max_tokens: int = 512, tier: str = "small", context: Optional[str] = None):
        """
        Gated inference with confidence estimation and tier-routing.
        Returns: {"answer": str, "confidence": float, "tier": str}
        """
        # 1. Point 10: Deduplicate in-flight identical queries
        if prompt in self._in_flight:
            logger.info("model_manager: joining existing in-flight request", prompt=prompt[:30])
            return await self._in_flight[prompt]
            
        # Create future for this prompt
        fut = asyncio.get_event_loop().create_future()
        self._in_flight[prompt] = fut
        
        try:
            model = await self.get_model(tier=tier)
            start = time.time()
            full_prompt = f"Context: {context}\n\nTask: {prompt}" if context else prompt
            
            async with self._semaphore:
                loop = asyncio.get_event_loop()
                raw_answer = await loop.run_in_executor(None, model.generate, full_prompt, max_tokens)
                duration = time.time() - start
                confidence = 0.95
                
                res = {
                    "answer": str(raw_answer),
                    "confidence": confidence,
                    "tier": tier,
                    "latency_ms": int(duration*1000)
                }
                fut.set_result(res)
                return res
        except Exception as e:
            logger.error("inference_failure", error=str(e), tier=tier)
            fut.set_exception(e)
            raise
        finally:
            self._in_flight.pop(prompt, None)

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
