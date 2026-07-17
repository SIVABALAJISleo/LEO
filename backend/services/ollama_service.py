"""
backend/services/ollama_service.py
Thin private AI service layer routing prompts to local Ollama API.
Includes prompt sanitization guardrails and SSE streaming.
"""

import json
import logging
import requests
import re

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434"

class OllamaService:
    def __init__(self, default_model: str = "qwen2.5:1.5b"):
        self.default_model = default_model

    def check_health(self) -> dict:
        """Pings local Ollama instance to check connection status."""
        try:
            # Query active tags/models in local Ollama
            response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2.0)
            if response.status_code == 200:
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]
                return {
                    "status": "ONLINE",
                    "url": OLLAMA_URL,
                    "models_available": models
                }
        except Exception as e:
            logger.warning(f"Ollama connection check failed: {e}")
            
        return {
            "status": "OFFLINE",
            "url": OLLAMA_URL,
            "models_available": []
        }

    def sanitize_input(self, text: str) -> str:
        """Basic prompt-injection guardrail sanitizing special tags/instructions."""
        if not text:
            return ""
        # Strip common instruction overrides
        cleaned = re.sub(r"(?i)\b(ignore previous instructions|system directive|overwrite)\b", "[SANITIZED]", text)
        return cleaned.strip()

    def generate_stream(self, prompt: str, system_message: str = None, model: str = None):
        """Streams text generation chunks as Server-Sent Events (SSE)."""
        target_model = model or self.default_model
        sanitized_prompt = self.sanitize_input(prompt)
        
        payload = {
            "model": target_model,
            "prompt": sanitized_prompt,
            "stream": True
        }
        if system_message:
            payload["system"] = system_message

        try:
            # Make a streaming POST query to local Ollama
            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json=payload,
                stream=True,
                timeout=30.0
            )
            
            if response.status_code != 200:
                yield f"data: {json.dumps({'error': f'Ollama error status {response.status_code}'})}\n\n"
                return

            for line in response.iter_lines():
                if line:
                    decoded = line.decode("utf-8")
                    try:
                        data = json.loads(decoded)
                        chunk = data.get("response", "")
                        done = data.get("done", False)
                        
                        yield f"data: {json.dumps({'token': chunk, 'done': done})}\n\n"
                        if done:
                            break
                    except Exception as e:
                        logger.error(f"Error parsing Ollama stream chunk: {e}")
                        
        except Exception as e:
            logger.error(f"Ollama stream request failed: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
