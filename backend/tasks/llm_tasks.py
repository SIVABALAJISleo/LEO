from backend.celery_app import app
import time
import logging

logger = logging.getLogger(__name__)

# To prevent loading huge LLM weights into the master process or memory leaks
# we lazy load the inference engine only WHEN the worker process spawns and picks a task.
llm_engine = None

def get_llm_engine():
    global llm_engine
    if llm_engine is None:
        logger.info("Initializing LLM Engine on Worker Process...")
        from backend.engine.llm_cpu_inference import LlmCpuInferenceEngine
        llm_engine = LlmCpuInferenceEngine()
    return llm_engine

@app.task(
    bind=True, 
    name="llm.generate", 
    max_retries=3, 
    autoretry_for=(Exception,), 
    retry_backoff=True, 
    time_limit=300, 
    soft_time_limit=250
)
def generate_llm_response(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7):
    """
    Celery task wrapper for llamas.cpp text generation.
    Because Celery executes sync functions, we use the engine's underlying sync calls 
    or run an asyncio loop internally.
    """
    try:
        engine = get_llm_engine()
        if not engine.llm:
            raise RuntimeError("LLM model failed to load in worker.")
            
        start_time = time.time()
        
        # We need to bridge the async core logic since Celery tasks are blocking
        # But for llama.cpp, the actual inference is fully blocking in C++ anyway
        response = engine.llm(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            echo=False
        )
        
        text_output = response['choices'][0]['text'].strip()
        duration = time.time() - start_time
        
        # Log telemetry for billing
        tokens_generated = response['usage']['completion_tokens']
        
        return {
            "status": "success",
            "text": text_output,
            "metrics": {
                "duration_seconds": round(duration, 3),
                "tokens_generated": tokens_generated
            }
        }
        
    except Exception as exc:
        logger.error(f"LLM Task Failed: {exc}")
        # Automatically retry the task if we hit OOM or temporary glitches
        raise self.retry(exc=exc, countdown=5)
