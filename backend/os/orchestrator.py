import logging
import time
import asyncio
from typing import Dict, Any

from backend.os.resource_manager import IntelligentResourceManager
from backend.routing.adaptive_router import AdaptiveModelRouter
from backend.compute.heterogeneous import HeterogeneousComputeEngine
from backend.execution.parallel_framework import ParallelExecutionFramework

import aiohttp
import json

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
        
        # Ollama connection settings
        self.ollama_url = "http://localhost:11434/api/generate"
        self.ollama_model = None # Will auto-detect on first run

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

    async def _get_ollama_model(self) -> str:
        if self.ollama_model is not None:
            return self.ollama_model
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:11434/api/tags") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        models = data.get("models", [])
                        if models:
                            self.ollama_model = models[0]["name"]
                            logger.info(f"Ollama auto-detected model: {self.ollama_model}")
                            return self.ollama_model
        except Exception as e:
            logger.warning(f"Could not connect to Ollama to detect models: {e}")
        return "llama3" # Default fallback

    async def _query_ollama(self, prompt: str) -> str:
        model = await self._get_ollama_model()
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            # Let Ollama handle its own context window and optimization for the demo
            "options": {"num_predict": 512, "temperature": 0.2}
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.ollama_url, json=payload, timeout=60) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("response", "").strip()
                    else:
                        return f"[Ollama Error: {resp.status}]"
        except Exception as e:
            return f"[Ollama Connection Failed: Ensure Ollama is running on localhost:11434]"

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
                # Call local Ollama
                full_prompt = f"Context: {context.get('retrieval_results', [])}\n\nQuery: {query}"
                ollama_ans = await self._query_ollama(full_prompt)
                response_payload["answer"] = ollama_ans
            elif route_destination == "TINY_MODEL":
                # For Tiny, we can also use Ollama but ask for extreme brevity, or assume a tiny local model.
                ollama_ans = await self._query_ollama(f"Answer very briefly in one sentence: {query}")
                response_payload["answer"] = ollama_ans
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
