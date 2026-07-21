"""
core_ai/colibri_glm_backend.py

Colibri GLM-5.2 (744B MoE) Backend Integration for LEO AI.

Colibri streams experts from disk, activating only ~40B params per token.
It exposes an OpenAI-compatible API at http://localhost:8080/v1.

This backend is the 'Deep Reasoning' tier in LEO's tiered intelligence router.
It is NOT a speed tool (0.05–0.1 tok/s). It is a QUALITY/CAPABILITY tool.

Usage:
    backend = ColibriGLMBackend()
    async for token in backend.stream_completion("Analyze this architecture..."):
        print(token, end="", flush=True)
"""

import asyncio
import json
import logging
import time
from typing import AsyncIterator, Optional

logger = logging.getLogger(__name__)

# httpx is the recommended async HTTP client for streaming
try:
    import httpx
    _HTTPX_AVAILABLE = True
except ImportError:
    _HTTPX_AVAILABLE = False
    logger.warning("[Colibri] httpx not installed. Run: pip install httpx")


class ColibriGLMBackend:
    """
    Async streaming backend for Colibri's GLM-5.2 744B MoE model.

    Colibri Architecture Facts:
    - 744B total parameters, ~40B activated per token (MoE routing)
    - ~11GB of experts change between tokens → disk streaming architecture
    - Speed: 0.05–0.1 tok/s on consumer hardware (quality tier, not speed tier)
    - Learning cache: pins hot experts automatically — gets faster with usage
    - API: OpenAI-compatible REST API at localhost:8080
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        model: str = "glm-5.2",
        timeout_seconds: float = 600.0,  # 10 min: 0.1 tok/s * 512 tokens = ~85 min worst case
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout_seconds
        self._client: Optional["httpx.AsyncClient"] = None

    async def _get_client(self) -> "httpx.AsyncClient":
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(
                    connect=10.0,
                    read=self.timeout,
                    write=30.0,
                    pool=5.0,
                )
            )
        return self._client

    async def is_available(self) -> bool:
        """
        Checks if the Colibri server is running and reachable.
        Call this before routing a task to Colibri.
        """
        if not _HTTPX_AVAILABLE:
            return False
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/v1/models", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False

    async def stream_completion(
        self,
        prompt: str,
        system_prompt: str = "You are an expert AI assistant. Think step by step.",
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """
        Streams tokens from Colibri GLM-5.2 as they are generated.

        This is the primary interface — always use streaming for Colibri
        because at 0.1 tok/s, blocking until full response takes minutes.

        Yields:
            str: Individual token strings as they arrive.
        """
        if not _HTTPX_AVAILABLE:
            yield "[ERROR] httpx not installed. Run: pip install httpx"
            return

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "stream": True,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        logger.info(f"[Colibri] Streaming GLM-5.2 response for prompt ({len(prompt)} chars)...")
        t_start = time.perf_counter()
        token_count = 0

        try:
            client = await self._get_client()
            async with client.stream(
                "POST",
                f"{self.base_url}/v1/chat/completions",
                json=payload,
            ) as response:
                if response.status_code != 200:
                    error_body = await response.aread()
                    yield f"[ERROR] Colibri returned HTTP {response.status_code}: {error_body.decode()}"
                    return

                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    if line.startswith("data: "):
                        chunk_str = line[6:]
                        if chunk_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(chunk_str)
                            delta = chunk["choices"][0]["delta"]
                            token_text = delta.get("content", "")
                            if token_text:
                                token_count += 1
                                yield token_text
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue

        except httpx.ConnectError:
            yield (
                "\n\n[Colibri Offline] GLM-5.2 backend is not running. "
                "Start it with: ./coli serve --model /path/to/glm52_i4\n"
                "LEO will route this request to the local fast model instead."
            )
            return
        except Exception as e:
            logger.error(f"[Colibri] Streaming error: {e}")
            yield f"\n\n[Colibri Error] {type(e).__name__}: {e}"
            return
        finally:
            elapsed = time.perf_counter() - t_start
            actual_tps = token_count / max(elapsed, 0.001)
            logger.info(
                f"[Colibri] Completed: {token_count} tokens in {elapsed:.1f}s "
                f"({actual_tps:.3f} tok/s)"
            )

    async def close(self):
        """Gracefully close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
