import time
import logging
from typing import Dict, Any
from universal_compute_router.hw_detector import HardwareDetector
from universal_compute_router.router_logic import UniversalComputeRouter
from intel_core_ai.inference import IntelInferenceEngine

logger = logging.getLogger(__name__)

class UniversalOrchestrator:
    """
    [SYSTEM DIRECTIVE — UNIVERSAL COMPUTE ROUTER]
    Orchestrates execution across AI, Video, Data, and Optimization engines.
    """
    def __init__(self, engine: IntelInferenceEngine):
        self.engine = engine
        self.hw = HardwareDetector()
        self.router = UniversalComputeRouter()

    async def execute_task(self, query: str) -> Dict[str, Any]:
        start_time = time.time()
        
        # [1] TASK CLASSIFICATION
        task_metadata = self.router.classify_task(query)
        
        # [2] CACHE FIRST (Placeholder for actual implementation)
        # result = self.router.check_cache(query) ...
        
        # [3] ROUTING DECISION
        route = self.router.decide_route(task_metadata)
        logger.info(f"Routing {task_metadata['task_type']} task to {route}")
        
        # [4] EXECUTION LAYER
        try:
            if route == "video_engine":
                answer = self._execute_video_task(query)
            elif route == "data_engine":
                answer = self._execute_data_task(query)
            elif route == "solver_engine":
                answer = self._execute_solver_task(query)
            elif route == "api_fallback":
                answer = "[API_FALLBACK] Executing on cloud..."
            else:
                # Default AI routes (tiny_model / main_model)
                system_prompt = f"Route: {route}. Optimization: CPU/Quantized."
                gen = self.engine.generate_stream(query, system_prompt)
                answer = "".join(list(gen))
                
            success = True
        except Exception as e:
            logger.error(f"Execution failed on {route}: {e}")
            success = False
            answer = f"Error during execution on {route}."

        latency = time.time() - start_time
        
        # [9] ROUTER LEARNING UPDATE
        self.router.update_learning(task_metadata, route, success, latency)
        
        return {
            "result": answer,
            "calibrated_confidence": 0.95 if success else 0.1,
            "route_used": route,
            "task_metadata": task_metadata,
            "latency_ms": f"{latency*1000:.1f}ms"
        }

    def _execute_video_task(self, query: str) -> str:
        """[4] VIDEO: FFmpeg (CPU) / AI upscaling (ONNX)"""
        # Mocking specialized engine call
        return f"[VIDEO_ENGINE] Processing request with FFmpeg/ONNX: {query}"

    def _execute_data_task(self, query: str) -> str:
        """[4] DATA: Polars / DuckDB"""
        # Mocking specialized engine call
        return f"[DATA_ENGINE] Querying local data via Polars/DuckDB: {query}"

    def _execute_solver_task(self, query: str) -> str:
        """[4] OPTIMIZATION: OR-Tools / A*"""
        # Mocking specialized engine call
        return f"[SOLVER_ENGINE] Resolving constraints using OR-Tools: {query}"
