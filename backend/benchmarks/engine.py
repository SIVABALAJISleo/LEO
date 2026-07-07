import os
import json
import time
import logging
from typing import List, Dict, Any
import aiohttp

logger = logging.getLogger(__name__)

class BenchmarkEngine:
    def __init__(self, dataset_path: str = "msr_dataset_500.json"):
        self.dataset_path = dataset_path
        self.dataset: List[Dict[str, Any]] = []
        self.results: Dict[str, Any] = {
            "status": "idle",
            "models": {
                "LEO_AI_VNext": {"latency_ms": 0, "accuracy": 0, "cost": 0, "queries_run": 0},
                "GPT_4o": {"latency_ms": 0, "accuracy": 0, "cost": 0, "queries_run": 0},
                "Claude_35_Sonnet": {"latency_ms": 0, "accuracy": 0, "cost": 0, "queries_run": 0},
                "Gemini_15_Pro": {"latency_ms": 0, "accuracy": 0, "cost": 0, "queries_run": 0},
            },
            "history": []
        }
        self.load_dataset()

    def load_dataset(self):
        try:
            with open(self.dataset_path, "r", encoding="utf-8") as f:
                self.dataset = json.load(f)
            logger.info(f"Loaded {len(self.dataset)} items from {self.dataset_path}")
        except Exception as e:
            logger.error(f"Failed to load dataset {self.dataset_path}: {e}")
            self.dataset = []

    async def run_benchmark(self, num_queries: int = 10):
        if not self.dataset:
            self.results["status"] = "error"
            self.results["error"] = "Dataset not loaded."
            return self.results
            
        self.results["status"] = "running"
        self.results["history"] = []
        
        # Reset counters
        for k in self.results["models"]:
            self.results["models"][k] = {"latency_ms": 0, "accuracy": 0, "cost": 0, "queries_run": 0}

        queries_to_run = self.dataset[:num_queries]

        async with aiohttp.ClientSession() as session:
            for i, item in enumerate(queries_to_run):
                query = item.get("question", "")
                expected = item.get("answer", "")
                
                logger.info(f"Running benchmark query {i+1}/{num_queries}: {query[:50]}...")
                
                # Run LEO AI
                leo_start = time.time()
                leo_response = await self._run_leo_ai(query)
                leo_latency = (time.time() - leo_start) * 1000
                leo_accuracy = self._evaluate_accuracy(expected, leo_response)
                self._update_model_stats("LEO_AI_VNext", leo_latency, leo_accuracy, 0.0)

                # Run External APIs if keys are available
                gpt_latency, gpt_acc, gpt_cost = await self._run_openai(session, query, expected)
                self._update_model_stats("GPT_4o", gpt_latency, gpt_acc, gpt_cost)

                claude_latency, claude_acc, claude_cost = await self._run_anthropic(session, query, expected)
                self._update_model_stats("Claude_35_Sonnet", claude_latency, claude_acc, claude_cost)
                
                gemini_latency, gemini_acc, gemini_cost = await self._run_gemini(session, query, expected)
                self._update_model_stats("Gemini_15_Pro", gemini_latency, gemini_acc, gemini_cost)

                self.results["history"].append({
                    "query": query,
                    "leo": {"latency": leo_latency, "accuracy": leo_accuracy},
                    "gpt": {"latency": gpt_latency, "accuracy": gpt_acc},
                    "claude": {"latency": claude_latency, "accuracy": claude_acc},
                    "gemini": {"latency": gemini_latency, "accuracy": gemini_acc}
                })
        
        self.results["status"] = "completed"
        return self.results

    def _update_model_stats(self, model: str, latency: float, accuracy: float, cost: float):
        if latency <= 0 and accuracy == 0:
            return # Skipped (e.g. no API key)
            
        stats = self.results["models"][model]
        curr_queries = stats["queries_run"]
        
        stats["latency_ms"] = ((stats["latency_ms"] * curr_queries) + latency) / (curr_queries + 1)
        stats["accuracy"] = ((stats["accuracy"] * curr_queries) + accuracy) / (curr_queries + 1)
        stats["cost"] += cost
        stats["queries_run"] += 1

    def _evaluate_accuracy(self, expected: str, actual: str) -> float:
        # A simple keyword inclusion heuristic for now
        # In a real system, you'd use LLM-as-a-judge or exact match
        if not actual:
            return 0.0
        expected_tokens = set(expected.lower().split())
        actual_tokens = set(actual.lower().split())
        if not expected_tokens:
            return 100.0
        overlap = expected_tokens.intersection(actual_tokens)
        return (len(overlap) / len(expected_tokens)) * 100.0

    async def _run_leo_ai(self, query: str) -> str:
        # Avoid circular imports by importing orchestrator here
        from backend.layers.v10_beta_orchestrator import global_v10_beta_orchestrator
        try:
            result = global_v10_beta_orchestrator.execute_semantic_workflow(
                query=query,
                context={"workspace_id": "benchmark"}
            )
            return result.get("final_response", "")
        except Exception as e:
            logger.error(f"LEO AI error: {e}")
            return ""

    async def _run_openai(self, session: aiohttp.ClientSession, query: str, expected: str):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key: return 0, 0, 0
        
        start = time.time()
        try:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": query}]
            }
            async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload) as resp:
                data = await resp.json()
                latency = (time.time() - start) * 1000
                answer = data["choices"][0]["message"]["content"] if "choices" in data else ""
                acc = self._evaluate_accuracy(expected, answer)
                return latency, acc, 0.01 # Mock cost
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return 0, 0, 0

    async def _run_anthropic(self, session: aiohttp.ClientSession, query: str, expected: str):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key: return 0, 0, 0
        
        start = time.time()
        try:
            headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
            payload = {
                "model": "claude-3-5-sonnet-20240620",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": query}]
            }
            async with session.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload) as resp:
                data = await resp.json()
                latency = (time.time() - start) * 1000
                answer = data["content"][0]["text"] if "content" in data else ""
                acc = self._evaluate_accuracy(expected, answer)
                return latency, acc, 0.01
        except Exception as e:
            logger.error(f"Anthropic error: {e}")
            return 0, 0, 0

    async def _run_gemini(self, session: aiohttp.ClientSession, query: str, expected: str):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key: return 0, 0, 0
        
        start = time.time()
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts":[{"text": query}]}]
            }
            async with session.post(url, json=payload) as resp:
                data = await resp.json()
                latency = (time.time() - start) * 1000
                answer = data["candidates"][0]["content"]["parts"][0]["text"] if "candidates" in data else ""
                acc = self._evaluate_accuracy(expected, answer)
                return latency, acc, 0.01
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return 0, 0, 0

global_benchmark_engine = BenchmarkEngine()
