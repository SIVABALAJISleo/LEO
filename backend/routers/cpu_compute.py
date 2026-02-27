import time
import psutil
from fastapi import APIRouter
from pydantic import BaseModel

from backend.core.hyper_config import config
from backend.engine.llm_cpu_inference import llm_engine

router = APIRouter(prefix="/api/v1/compute", tags=["Compute"])

class BenchmarkRequest(BaseModel):
    prompt: str = "Explain the architecture of a high-performance system."
    max_tokens: int = 150

@router.post("/benchmark")
async def benchmark_inference(req: BenchmarkRequest):
    """
    Measures the token generation speed using the CPU Inference Engine.
    """
    if not llm_engine.llm:
        return {"status": "error", "message": "LLM model not loaded. Check model path in config."}

    start_time = time.time()
    response = await llm_engine.generate_response(
        prompt=req.prompt,
        max_tokens=req.max_tokens
    )
    end_time = time.time()
    
    duration = end_time - start_time
    
    # Very rough token count approximation for benchmarking (word count * 1.3)
    estimated_tokens = int(len(response.split()) * 1.3)
    tokens_per_second = estimated_tokens / duration if duration > 0 else 0
    
    return {
        "status": "success",
        "duration_seconds": round(duration, 3),
        "estimated_tokens": estimated_tokens,
        "tokens_per_second": round(tokens_per_second, 2),
        "response_sample": response[:100] + "...",
        "config_used": {
            "threads": config.LLM_THREADS,
            "batch_size": config.LLM_BATCH_SIZE
        }
    }

@router.get("/telemetry")
async def get_telemetry():
    """Returns active CPU utilization, memory, and thread metrics."""
    cpu_percent = psutil.cpu_percent(interval=None, percpu=True)
    memory_info = psutil.virtual_memory()
    
    return {
        "cpu": {
            "average_utilization": sum(cpu_percent) / len(cpu_percent),
            "per_core_utilization": cpu_percent,
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True)
        },
        "memory": {
            "total_gb": round(memory_info.total / (1024**3), 2),
            "used_gb": round(memory_info.used / (1024**3), 2),
            "percent_used": memory_info.percent
        }
    }
