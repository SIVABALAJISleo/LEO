"""
backend/micro_models/router.py
Real micro-model router using llm_loader (no fake imports).
"""
import logging
import asyncio
from typing import Optional
from backend.models.llm_loader import generate_response

logger = logging.getLogger(__name__)


class MicroModelRouter:
    """
    Routes specialized intents (math, code, summary) to optimized generation.
    Uses the real llm_loader (TinyLlama or fallback) instead of mocked models.
    """
    def route(self, query: str) -> Optional[str]:
        q = query.lower()
        if any(w in q for w in ["calculate", "math", "solve", "+", "-", "*", "/", " = ", "sum of", "percentage"]):
            return "math"
        if any(w in q for w in ["summarize", "tl;dr", "shorten", "brief", "summary"]):
            return "summarization"
        if any(w in q for w in ["python", "javascript", "typescript", "code", "function", "class", "debug", "script"]):
            return "code"
        return None

    async def execute(self, query: str, specialty: str) -> str:
        system_prompts = {
            "math": "You are a precise math assistant. Show working steps and give the final answer clearly.",
            "summarization": "You are a summarization expert. Produce a concise TL;DR in 3-5 bullet points.",
            "code": "You are a senior software engineer. Provide clean, commented code with brief explanation.",
        }
        system_prompt = system_prompts.get(specialty, "You are a helpful, concise AI assistant.")
        logger.info("micro_model: routing specialty=%s", specialty)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, generate_response, query, 256, 0.5, system_prompt
        )
        return result


global_micro_router = MicroModelRouter()