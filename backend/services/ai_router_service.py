"""
backend/services/ai_router_service.py
Hardware-aware AI query router.
Routes between lightweight local Ollama and massive Colibri MoE models based on system specifications.
"""

import shutil
import psutil
import requests
import json
import logging
from backend.services.ollama_service import OllamaService

logger = logging.getLogger(__name__)

COLIBRI_API_URL = "http://localhost:8000"

class AIRouterService:
    def __init__(self):
        self.ollama = OllamaService()

    def check_capabilities(self) -> dict:
        """Evaluates hardware capacity limits for executing Colibri MoE models."""
        # 1. Probe total system RAM
        mem = psutil.virtual_memory()
        total_ram_gb = mem.total / (1024 ** 3)
        ram_capable = total_ram_gb >= 24.0 # 24GB reporting buffer for 32GB systems
        
        # 2. Probe disk space bounds
        try:
            disk = shutil.disk_usage("/")
            free_disk_gb = disk.free / (1024 ** 3)
        except Exception:
            free_disk_gb = 0.0
            
        disk_capable = free_disk_gb >= 150.0

        # 3. Assess Ollama & Colibri daemon connectivity
        ollama_health = self.ollama.check_health()
        ollama_online = ollama_health["status"] == "ONLINE"
        
        colibri_online = False
        try:
            response = requests.get(f"{COLIBRI_API_URL}/v1/models", timeout=1.5)
            if response.status_code == 200:
                colibri_online = True
        except Exception:
            pass

        is_capable = ram_capable and disk_capable

        return {
            "ram_total_gb": round(total_ram_gb, 1),
            "ram_capable": ram_capable,
            "disk_free_gb": round(free_disk_gb, 1),
            "disk_capable": disk_capable,
            "colibri_capable": is_capable,
            "colibri_online": colibri_online,
            "ollama_online": ollama_online,
            "ollama_models": ollama_health["models_available"]
        }

    def generate_stream(self, prompt: str, system_message: str = None, model: str = None, route_mode: str = "auto"):
        """Streams text generation chunks, routing to Colibri or Ollama based on capabilities."""
        caps = self.check_capabilities()
        
        # Determine active model routing path
        use_colibri = False
        if route_mode == "colibri":
            if caps["colibri_capable"] and caps["colibri_online"]:
                use_colibri = True
            else:
                logger.warning("[AI Router] Colibri forced but system incapable or offline. Falling back to local Ollama.")
        elif route_mode == "auto":
            # Direct complex/long queries to Colibri if system is capable & online
            is_complex = len(prompt) > 1000 or any(kw in prompt.lower() for kw in ["analyze", "prove", "math", "complexity", "compile"])
            if is_complex and caps["colibri_capable"] and caps["colibri_online"]:
                use_colibri = True

        if use_colibri:
            logger.info("[AI Router] Routing query to Colibri MoE model engine.")
            yield from self._stream_colibri(prompt, system_message, model)
        else:
            logger.info("[AI Router] Routing query to lightweight local Ollama service.")
            yield from self.ollama.generate_stream(prompt, system_message, model)

    def _stream_colibri(self, prompt: str, system_message: str = None, model: str = None):
        """Streams chat completions from Colibri's local OpenAI API server."""
        payload = {
            "model": model or "glm-5.2",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": True
        }
        if system_message:
            payload["messages"].insert(0, {"role": "system", "content": system_message})

        try:
            response = requests.post(
                f"{COLIBRI_API_URL}/v1/chat/completions",
                json=payload,
                stream=True,
                timeout=45.0
            )
            
            if response.status_code != 200:
                yield f"data: {json.dumps({'error': f'Colibri error status {response.status_code}'})}\n\n"
                return

            for line in response.iter_lines():
                if line:
                    decoded = line.decode("utf-8")
                    if decoded.startswith("data: "):
                        content = decoded[6:].strip()
                        if content == "[DONE]":
                            yield f"data: {json.dumps({'token': '', 'done': True})}\n\n"
                            break
                        try:
                            data = json.loads(content)
                            chunk = data["choices"][0]["delta"].get("content", "")
                            yield f"data: {json.dumps({'token': chunk, 'done': False})}\n\n"
                        except Exception as e:
                            logger.error(f"Error parsing Colibri chunk: {e}")
                            
        except Exception as e:
            logger.error(f"Colibri request failed: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
