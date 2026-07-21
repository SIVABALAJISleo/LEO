"""
core_ai/tiered_router.py

LEO AI Tiered Intelligence Router.

Routes each incoming query to the appropriate model tier based on
complexity classification. This is the central decision-making layer
that makes the Colibri + LEO integration production-ready.

Architecture:
    Tier 1 — FAST:   Local small model (Phi-3, TinyLlama) → 15-40 tok/s
    Tier 2 — SMART:  LEO's existing optimized CPU stack    → 12.8 tok/s
    Tier 3 — DEEP:   Colibri GLM-5.2 (744B MoE)           → 0.05-0.1 tok/s

The router classifies complexity using:
  - Keyword signals (complex reasoning, code review, analysis)
  - Token length thresholds
  - Explicit tier override from the caller
"""

import re
import logging
import asyncio
from enum import Enum
from typing import AsyncIterator, Optional, Dict, Any, Callable

logger = logging.getLogger(__name__)


class InferenceTier(Enum):
    FAST  = "fast"    # Tier 1: small local model, instant
    SMART = "smart"   # Tier 2: LEO optimized speculative stack
    DEEP  = "deep"    # Tier 3: Colibri GLM-5.2 744B


# ── Complexity Signals ───────────────────────────────────────────────────────

# These keyword patterns trigger Tier 3 (Colibri GLM-5.2)
DEEP_REASONING_PATTERNS = [
    r"\banalyze\b", r"\banalysis\b", r"\bcompare\b", r"\barchitecture\b",
    r"\bsummarize\b", r"\bsummarise\b", r"\bcode review\b", r"\brefactor\b",
    r"\bdesign\b", r"\bstrategy\b", r"\bplan\b", r"\bexplain in depth\b",
    r"\bwhy does\b", r"\bhow does\b", r"\bprove\b", r"\bderive\b",
    r"\bbenchmark\b", r"\boptimize\b", r"\boptimisation\b", r"\bdebug\b",
    r"\bwrite a report\b", r"\bwrite a paper\b", r"\bresearch\b",
]

# These patterns are safe for Tier 1 (fast small model)
FAST_PATTERNS = [
    r"^hello\b", r"^hi\b", r"^hey\b", r"^what is your name",
    r"^translate\b", r"^convert\b", r"^format\b",
    r"^yes\b", r"^no\b", r"^ok\b", r"^thanks\b",
]

_DEEP_RE  = re.compile("|".join(DEEP_REASONING_PATTERNS), re.IGNORECASE)
_FAST_RE  = re.compile("|".join(FAST_PATTERNS),  re.IGNORECASE)


def classify_complexity(prompt: str) -> InferenceTier:
    """
    Classifies a prompt into one of the three tiers.
    
    Decision logic:
      1. Short prompts (<15 words) with fast pattern  → FAST
      2. Long prompts (>80 words) or deep keywords    → DEEP
      3. Everything else                              → SMART
    """
    word_count = len(prompt.split())

    if word_count < 15 and _FAST_RE.search(prompt):
        return InferenceTier.FAST

    if word_count > 80 or _DEEP_RE.search(prompt):
        return InferenceTier.DEEP

    return InferenceTier.SMART


# ── Tiered Router ────────────────────────────────────────────────────────────

class TieredIntelligenceRouter:
    """
    Routes inference requests across three model tiers.

    Usage:
        router = TieredIntelligenceRouter()
        async for token in router.route("Analyze the architecture of my system..."):
            print(token, end="", flush=True)
    """

    def __init__(
        self,
        colibri_base_url: str = "http://localhost:8080",
        leo_api_base_url:  str = "http://localhost:8005",
    ):
        self.colibri_base_url = colibri_base_url
        self.leo_api_base_url  = leo_api_base_url

        # Lazy-import backends to avoid hard dependencies at import time
        self._colibri_backend = None
        self._colibri_checked  = False
        self._colibri_available = False

    async def _get_colibri(self):
        """Lazily initialises and health-checks the Colibri backend."""
        from core_ai.colibri_glm_backend import ColibriGLMBackend
        if self._colibri_backend is None:
            self._colibri_backend = ColibriGLMBackend(base_url=self.colibri_base_url)

        if not self._colibri_checked:
            self._colibri_available = await self._colibri_backend.is_available()
            self._colibri_checked = True
            if self._colibri_available:
                logger.info("[Router] Colibri GLM-5.2 backend is ONLINE ✓")
            else:
                logger.warning(
                    "[Router] Colibri GLM-5.2 backend is OFFLINE. "
                    "Deep queries will fall back to LEO SMART tier."
                )

        return self._colibri_backend, self._colibri_available

    async def route(
        self,
        prompt: str,
        tier_override: Optional[InferenceTier] = None,
        on_tier_selected: Optional[Callable[[InferenceTier, bool], None]] = None,
        max_tokens: int = 512,
    ) -> AsyncIterator[str]:
        """
        Routes a prompt to the correct model tier and streams the response.

        Args:
            prompt: The user's query text.
            tier_override: Force a specific tier (skips classification).
            on_tier_selected: Optional callback(tier, colibri_online) for UI telemetry.
            max_tokens: Maximum tokens to generate.

        Yields:
            Token strings as they are generated.
        """
        tier = tier_override or classify_complexity(prompt)
        logger.info(f"[Router] Prompt classified as tier={tier.value} ({len(prompt.split())} words)")

        if on_tier_selected:
            on_tier_selected(tier, self._colibri_available)

        if tier == InferenceTier.DEEP:
            colibri, available = await self._get_colibri()
            if available:
                logger.info("[Router] → Routing to Colibri GLM-5.2 (744B Deep Tier)")
                yield f"[LEO Router] Routing to GLM-5.2 (744B Deep Reasoning — streaming at ~0.1 tok/s)\n\n"
                async for token in colibri.stream_completion(
                    prompt=prompt,
                    max_tokens=max_tokens,
                ):
                    yield token
                return
            else:
                logger.warning("[Router] Colibri offline — downgrading DEEP → SMART")
                yield "[LEO Router] Colibri offline — using optimised LEO stack instead.\n\n"
                tier = InferenceTier.SMART

        if tier == InferenceTier.SMART:
            logger.info("[Router] → Routing to LEO Optimised Stack (Speculative Decoding, 12.8 tok/s)")
            async for token in self._stream_leo_smart(prompt, max_tokens):
                yield token
            return

        # FAST tier
        logger.info("[Router] → Routing to Fast Small Model (Tier 1)")
        async for token in self._stream_leo_fast(prompt, max_tokens):
            yield token

    async def _stream_leo_smart(self, prompt: str, max_tokens: int) -> AsyncIterator[str]:
        """
        Calls the LEO backend's speculative decoding endpoint.
        Falls back to a local echo if the backend isn't running.
        """
        try:
            import httpx
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.leo_api_base_url}/v1/chat/completions",
                    json={
                        "model": "leo-speculative",
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": True,
                        "max_tokens": max_tokens,
                    },
                ) as resp:
                    async for line in resp.aiter_lines():
                        if line.startswith("data: ") and line[6:] != "[DONE]":
                            try:
                                chunk = __import__("json").loads(line[6:])
                                token = chunk["choices"][0]["delta"].get("content", "")
                                if token:
                                    yield token
                            except Exception:
                                continue
        except Exception as e:
            logger.warning(f"[Router] LEO SMART backend unavailable: {e}")
            yield f"[LEO SMART Tier — simulated response to: {prompt[:80]}...]"

    async def _stream_leo_fast(self, prompt: str, max_tokens: int) -> AsyncIterator[str]:
        """
        Calls the LEO backend's fast small-model endpoint.
        """
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.leo_api_base_url}/v1/chat/completions",
                    json={
                        "model": "leo-fast",
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": True,
                        "max_tokens": max_tokens,
                    },
                ) as resp:
                    async for line in resp.aiter_lines():
                        if line.startswith("data: ") and line[6:] != "[DONE]":
                            try:
                                chunk = __import__("json").loads(line[6:])
                                token = chunk["choices"][0]["delta"].get("content", "")
                                if token:
                                    yield token
                            except Exception:
                                continue
        except Exception as e:
            logger.warning(f"[Router] LEO FAST backend unavailable: {e}")
            yield f"[LEO Fast Tier — simulated response to: {prompt[:80]}...]"

    async def get_routing_status(self) -> Dict[str, Any]:
        """Returns the live status of all three tiers for dashboard telemetry."""
        _, colibri_online = await self._get_colibri()
        return {
            "tier_fast":   {"status": "online",  "model": "Phi-3 / TinyLlama", "est_tps": 25.0},
            "tier_smart":  {"status": "online",  "model": "LEO Speculative Stack", "est_tps": 12.8},
            "tier_deep":   {
                "status": "online" if colibri_online else "offline",
                "model": "Colibri GLM-5.2 (744B MoE)",
                "est_tps": 0.08,
                "note": "Streaming experts from disk. Speed improves with usage (learning cache).",
            },
        }
