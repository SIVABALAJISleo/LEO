import httpx
import structlog
from typing import Optional

logger = structlog.get_logger()

class RemoteInference:
    """
    SaaS Scale Interface:
    Connects to high-performance model servers (vLLM, TGI, or OpenAI-compatible).
    """
    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url
        logger.info("loading_remote_model_server", url=endpoint_url)

    def generate(self, prompt: str, max_tokens: int = 512):
        """
        Sends request to remote model server.
        Matches the interface of LocalInference for seamless substitution.
        """
        try:
            # Synchronous wrapper for use in run_in_executor
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.endpoint_url.rstrip('/')}/v1/completions",
                    json={
                        "model": "default",
                        "prompt": prompt,
                        "max_tokens": max_tokens
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data['choices'][0]['text']
        except Exception as e:
            logger.error("remote_inference_failed", error=str(e))
            return f"Error: Remote inference failed: {e}"
