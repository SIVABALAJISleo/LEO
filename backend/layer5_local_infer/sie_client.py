"""
backend/layer5_local_infer/sie_client.py
Client connector for the Superlinked Inference Engine (SIE).
Enables querying local or cluster self-hosted agent models via OpenAI compatible endpoints.
"""
import os
import httpx
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class SieClient:
    """
    Client for interacting with the Superlinked Inference Engine (SIE).
    """
    def __init__(self, api_base: Optional[str] = None):
        # Default to localhost port 8000 (standard SIE port)
        self.api_base = api_base or os.getenv("VITE_SIE_API_BASE_URL", "http://localhost:8000/v1")
        self.client = httpx.Client(timeout=10.0)

    def is_healthy(self) -> bool:
        """Checks if the SIE backend server is online."""
        try:
            # Check models endpoint to verify connection
            res = self.client.get(f"{self.api_base}/models")
            return res.status_code == 200
        except Exception:
            return False

    def get_embeddings(self, text: str, model: str = "stella") -> Optional[List[float]]:
        """Extracts embeddings using the SIE vector model API."""
        try:
            res = self.client.post(
                f"{self.api_base}/embeddings",
                json={"input": text, "model": model}
            )
            if res.status_code == 200:
                data = res.json()
                return data["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"SIE Embedding extraction failed: {e}")
        return None

    def get_chat_completion(self, prompt: str, system_prompt: str = "", model: str = "qwen3") -> Optional[str]:
        """Requests completions from SIE served language models."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            res = self.client.post(
                f"{self.api_base}/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": 150
                }
            )
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"SIE Chat completion failed: {e}")
        return None
