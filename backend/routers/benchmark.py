from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from backend.benchmarks.engine import global_benchmark_engine

router = APIRouter(prefix="/api/v1/leo/benchmark", tags=["LEO Benchmarks"])

class BenchmarkRunRequest(BaseModel):
    num_queries: Optional[int] = 10

@router.post("/run")
async def start_benchmark(request: BenchmarkRunRequest, background_tasks: BackgroundTasks):
    """
    Start the benchmark engine in the background.
    """
    # Run in background to not block the API
    background_tasks.add_task(global_benchmark_engine.run_benchmark, request.num_queries)
    return {"status": "started", "message": f"Benchmark started for {request.num_queries} queries."}

@router.get("/results")
async def get_benchmark_results():
    """
    Get the current status and results of the benchmark.
    """
    return global_benchmark_engine.results
