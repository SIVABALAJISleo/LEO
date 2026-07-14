import logging
import time
import asyncio
from typing import Dict, Any

from backend.os.resource_manager import IntelligentResourceManager
from backend.routing.adaptive_router import AdaptiveModelRouter
from backend.compute.heterogeneous import HeterogeneousComputeEngine
from backend.execution.parallel_framework import ParallelExecutionFramework

logger = logging.getLogger(__name__)

class LEOOperatingSystem:
    """
    Subsystem 1: Adaptive AI Operating System.
    The central runtime scheduler for LEO AI V∞ Research Edition.
    """
    def __init__(self):
        logger.info("Initializing LEO Adaptive AI OS...")
        
        self.resource_manager = IntelligentResourceManager(check_interval=1.0)
        self.router = AdaptiveModelRouter()
        self.compute = HeterogeneousComputeEngine()
        self.parallel_executor = ParallelExecutionFramework(max_workers=6) # Fits i5-12450H 8c/12t comfortably
        
        # Start background telemetry
        self.resource_manager.start()
        
    def _mock_retrieval(self, query: str) -> list:
        # Placeholder for Subsystem 14 (Retrieval)
        time.sleep(0.05)
        return [f"Mock doc matching {query}"]
        
    def _mock_embedding(self, query: str) -> list:
        # Placeholder for embedding generation
        time.sleep(0.03)
        return [0.1, 0.2, 0.3]
        
    def _mock_graph_search(self, query: str) -> list:
        # Placeholder for Subsystem 6 (Knowledge Graph)
        time.sleep(0.02)
        return [f"Mock entity matching {query}"]

    async def execute_request(self, query: str) -> Dict[str, Any]:
        """The main entrypoint for any AI request."""
        t0 = time.perf_counter()
        
        # Step 1: Check Resource Headroom
        if not self.resource_manager.can_accept_heavy_task():
            logger.warning("System throttled. Degrading gracefully to Tiny Model / Rules only.")
            # Forced override to rule engine or fallback cache
            
        # Step 2: Adaptive Routing (Inference Avoidance)
        route_destination = self.router.route_query(query)
        
        response_payload = {
            "query": query,
            "route": route_destination,
            "status": "SUCCESS"
        }
        
        # Step 3: Execution based on route
        if route_destination in ["RULE_ENGINE", "CALCULATOR"]:
            # Zero-inference execution
            is_rule, rule_res = self.router._check_rules(query)
            if is_rule:
                response_payload["answer"] = rule_res
            else:
                is_math, math_res = self.router._check_calculator(query)
                response_payload["answer"] = math_res
                
        else:
            # Step 4: Parallel Context Gathering (Retrieval, Embeddings, Graph)
            context = await self.parallel_executor.execute_concurrent_pipeline(
                query,
                self._mock_retrieval,
                self._mock_embedding,
                self._mock_graph_search
            )
            response_payload["context"] = context
            
            # Step 5: Execute Model (Heterogeneous Compute)
            if route_destination == "LARGE_MODEL":
                # Simulated large model invocation
                # self.compute.execute_inference(model_id="llama3", input_dict=...)
                response_payload["answer"] = f"[LARGE_MODEL Simulated Response] Synthesized context for: {query}"
            elif route_destination == "TINY_MODEL":
                response_payload["answer"] = f"[TINY_MODEL Simulated Response] Fast answer for: {query}"
            elif route_destination == "RETRIEVAL_ENGINE":
                response_payload["answer"] = f"Here is what I found in memory: {context['retrieval_results'][0]}"

        total_latency = (time.perf_counter() - t0) * 1000
        response_payload["latency_ms"] = round(total_latency, 2)
        
        logger.info(f"Request completed in {total_latency:.2f}ms. Route: {route_destination}")
        return response_payload

    def shutdown(self):
        logger.info("Shutting down LEO Adaptive AI OS...")
        self.resource_manager.stop()
        self.parallel_executor.shutdown()
        self.compute.flush_cache()
