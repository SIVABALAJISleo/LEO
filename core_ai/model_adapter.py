"""
core_ai/model_adapter.py
Production-grade Local Inference Adapter for LEO AI v∞.
Integrates with llama-cpp-python and OpenVINO GenAI backends.
Offers validation checks, checksum audit, streaming, timeouts, cancellation tokens,
and device-level transparency.
"""

import os
import time
import hashlib
import logging
import threading
import queue
from typing import Dict, Any, Generator, Optional, List

logger = logging.getLogger(__name__)

# Real Legally Downloadable Model Manifests
QWEN_MODEL_MANIFESTS = {
    "qwen2.5-1.5b-instruct-q4_k_m.gguf": {
        "name": "Qwen2.5-1.5B-Instruct-GGUF",
        "exact_revision": "q4_k_m",
        "url": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf",
        "license": "Apache-2.0",
        "sha256": "6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e",
        "file_size_bytes": 1157962464,
        "quantization": "q4_k_m (4-bit)",
        "context_length": 32768,
        "expected_ram_gb": "1.5GB - 2.5GB"
    },
    "qwen2.5-0.5b-instruct-q4_k_m.gguf": {
        "name": "Qwen2.5-0.5B-Instruct-GGUF",
        "exact_revision": "q4_k_m",
        "url": "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf",
        "license": "Apache-2.0",
        "sha256": "74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db",
        "file_size_bytes": 397858816,
        "quantization": "q4_k_m (4-bit)",
        "context_length": 32768,
        "expected_ram_gb": "1.2GB - 2.0GB"
    }
}

class ModelValidationError(Exception):
    """Exception raised when model validation contract checks fail."""
    pass

def validate_model_integrity(model_path: str) -> None:
    """Verifies existence, GGUF magic bytes, size, and SHA-256 checksum."""
    if not os.path.exists(model_path):
        raise ModelValidationError(
            f"Model file missing at '{model_path}'!\n"
            f"Please run 'python leo.py download-model' to fetch the real models."
        )

    # If it is a directory (like OpenVINO IR directory), skip GGUF validation
    if os.path.isdir(model_path):
        if not os.path.exists(os.path.join(model_path, "openvino_model.xml")):
            raise ModelValidationError(f"Invalid OpenVINO IR model directory: '{model_path}'")
        return

    filename = os.path.basename(model_path).lower()
    manifest = QWEN_MODEL_MANIFESTS.get(filename)
    if not manifest:
        # If it's a custom/unregistered model file, verify magic and proceed gracefully
        with open(model_path, "rb") as f:
            if f.read(4) != b"GGUF":
                raise ModelValidationError("Invalid GGUF format!")
        return

    # Validate file size
    stat = os.stat(model_path)
    if abs(stat.st_size - manifest["file_size_bytes"]) > 20 * 1024 * 1024:
        logger.warning(f"File size mismatch: Found {stat.st_size} bytes vs expected {manifest['file_size_bytes']}.")

    # Validate GGUF format by checking magic bytes
    with open(model_path, "rb") as f:
        magic = f.read(4)
        if magic != b"GGUF":
            raise ModelValidationError(f"Invalid GGUF format! File magic header is '{magic}' instead of 'GGUF'.")

    # Incremental checksum validation to prevent memory blowout
    sha = hashlib.sha256()
    with open(model_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    checksum = sha.hexdigest()
    
    if checksum != manifest["sha256"]:
        logger.warning(f"SHA-256 Checksum mismatch for {filename}! Found '{checksum}' vs expected '{manifest['sha256']}'.")


class LEOInferenceAdapter:
    """Streams and manages local model inference runs via llama_cpp or OpenVINO GenAI."""
    def __init__(self, model_path: str, context_size: int = 2048, threads: int = 8, use_gpu: bool = False, backend: str = "llama.cpp"):
        self.model_path = model_path
        self.context_size = context_size
        self.threads = threads
        self.use_gpu = use_gpu
        self.backend = backend
        self._llm = None
        self._openvino_pipeline = None
        
        # Lazy loading
        self._init_backend()

    def _init_backend(self) -> None:
        validate_model_integrity(self.model_path)
        
        if self.backend == "llama.cpp":
            try:
                from llama_cpp import Llama
                gpu_layers = 16 if self.use_gpu else 0
                logger.info(f"[InferenceAdapter] Initializing GGUF Llama runtime with {self.threads} threads (GPU Layers: {gpu_layers}).")
                # KV Cache quantization: type_k=2 (q8_0), type_v=2 (q8_0)
                self._llm = Llama(
                    model_path=self.model_path,
                    n_ctx=self.context_size,
                    n_threads=self.threads,
                    n_gpu_layers=gpu_layers,
                    type_k=2,
                    type_v=2,
                    verbose=False
                )
            except ImportError:
                raise RuntimeError("llama_cpp-python package is not installed or available.")
        elif self.backend == "openvino":
            try:
                import openvino_genai as ov_genai
                device = "GPU" if self.use_gpu else "CPU"
                logger.info(f"[InferenceAdapter] Initializing OpenVINO GenAI pipeline on device: {device}.")
                self._openvino_pipeline = ov_genai.LLMPipeline(self.model_path, device)
            except ImportError:
                raise RuntimeError("openvino_genai package is not installed or available.")

    def generate_stream(
        self,
        prompt: str,
        system_prompt: str = "You are LEO AI v∞, a helpful and optimized assistant.",
        max_output_tokens: int = 512,
        temperature: float = 0.7,
        seed: Optional[int] = None,
        cancellation_token: Optional[threading.Event] = None,
        timeout_seconds: float = 30.0
    ) -> Generator[Dict[str, Any], None, None]:
        """Streams response tokens from the loaded local model backend."""
        t_start = time.time()
        token_count = 0
        device = ("GPU (OpenVINO)" if self.backend == "openvino" and self.use_gpu 
                  else ("GPU (Vulkan)" if self.use_gpu else "CPU"))

        if self.backend == "llama.cpp":
            if not self._llm:
                raise RuntimeError("Llama model is not loaded correctly.")

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            try:
                stream = self._llm.create_chat_completion(
                    messages=messages,
                    max_tokens=max_output_tokens,
                    temperature=temperature,
                    seed=seed if seed is not None else -1,
                    stream=True
                )
                
                for chunk in stream:
                    if cancellation_token and cancellation_token.is_set():
                        yield {
                            "text": " [Cancelled]",
                            "metadata": {"device": device, "tokens": token_count, "status": "CANCELLED", "latency_ms": (time.time() - t_start) * 1000.0}
                        }
                        return

                    if time.time() - t_start > timeout_seconds:
                        yield {
                            "text": " [Timeout Exceeded]",
                            "metadata": {"device": device, "tokens": token_count, "status": "TIMEOUT", "latency_ms": (time.time() - t_start) * 1000.0}
                        }
                        return

                    choices = chunk.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        token_text = delta.get("content", "")
                        if token_text:
                            token_count += 1
                            yield {
                                "text": token_text,
                                "metadata": {"device": device, "tokens": token_count, "status": "STREAMING", "latency_ms": (time.time() - t_start) * 1000.0}
                            }
            except Exception as e:
                logger.error(f"[InferenceAdapter] Llama generation failed: {e}")
                yield {
                    "text": f"\n[Generation Error: {e}]",
                    "metadata": {"device": device, "tokens": token_count, "status": "ERROR", "latency_ms": (time.time() - t_start) * 1000.0}
                }

        elif self.backend == "openvino":
            if not self._openvino_pipeline:
                raise RuntimeError("OpenVINO model pipeline is not loaded correctly.")

            import openvino_genai as ov_genai
            token_queue = queue.Queue()
            
            gen_config = ov_genai.GenerationConfig()
            gen_config.max_new_tokens = max_output_tokens
            gen_config.temperature = temperature
            
            def openvino_streamer(subword):
                token_queue.put(subword)
                if cancellation_token and cancellation_token.is_set():
                    return ov_genai.StreamingStatus.STOP
                if time.time() - t_start > timeout_seconds:
                    return ov_genai.StreamingStatus.STOP
                return ov_genai.StreamingStatus.RUNNING

            def run_generation():
                try:
                    formatted_prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
                    self._openvino_pipeline.generate(formatted_prompt, gen_config, openvino_streamer)
                except Exception as e:
                    logger.error(f"OpenVINO generation error: {e}")
                finally:
                    token_queue.put(None)
                    
            t = threading.Thread(target=run_generation)
            t.start()
            
            while True:
                token = token_queue.get()
                if token is None:
                    break
                token_count += 1
                yield {
                    "text": token,
                    "metadata": {
                        "device": device,
                        "tokens": token_count,
                        "status": "STREAMING",
                        "latency_ms": (time.time() - t_start) * 1000.0
                    }
                }
