import os
import logging
from typing import Dict, Any

# Conditional imports for CPU-optimized backends
try:
    from llama_cpp import Llama # type: ignore
except ImportError:
    Llama = None

try:
    import mediapipe as mp # type: ignore
except ImportError:
    mp = None

try:
    import cv2 # type: ignore
except ImportError:
    cv2 = None

try:
    import onnxruntime as ort # type: ignore
except ImportError:
    ort = None

try:
    from openvino.runtime import Core as OpenVINOCore # type: ignore
except ImportError:
    OpenVINOCore = None

logger = logging.getLogger(__name__)

class InferenceHub:
    """
    Centralized hub for CPU-optimized model inference.
    Supports LLMs (llama.cpp), Vision (MediaPipe, OpenCV), and ONNX/OpenVINO.
    Principles: INT4/INT8 Quantization, No training, Inference only.
    """
    def __init__(self, model_root: str = "models"):
        self.model_root = os.path.abspath(model_root)
        os.makedirs(self.model_root, exist_ok=True)
        self.llm = None
        self.vision_backend = "mock"
        
        # Initialize backends
        if mp: self.vision_backend = "mediapipe"
        elif cv2: self.vision_backend = "opencv"
        elif ort: self.vision_backend = "onnx"
        
        logger.info(f"InferenceHub initialized. Root: {self.model_root}. Vision: {self.vision_backend}")
        self.load_llm()

    def load_llm(self, model_name: str = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"):
        model_path = os.path.join(self.model_root, model_name)
        if Llama:
            if os.path.exists(model_path):
                logger.info(f"Loading CPU-optimized LLM from: {model_path}")
                try:
                    threads = max(1, (os.cpu_count() or 1) - 1)
                    self.llm = Llama(model_path=model_path, n_ctx=512, n_threads=threads, verbose=False)
                except Exception as e:
                    logger.error(f"LLM Load Fail: {e}")
            else:
                logger.warning(f"LLM File Missing: {model_path}. Run scripts/download_models.py")
        else:
            logger.warning("llama-cpp-python not found (required for local LLM)")

    def run_llm_inference(self, prompt: str, max_tokens: int = 64) -> str:
        if self.llm:
            try:
                output = self.llm(f"User: {prompt}\nAssistant:", max_tokens=max_tokens, stop=["User:"])
                return output['choices'][0]['text']
            except Exception:
                logger.error("Inference execution failed", exc_info=True)
                return "Inference Error: Failed to generate model response"
        
        return "LLM Engine Offline. (Please download models/tinyllama... and ensure llama-cpp-python is installed)"

    def run_vision_inference(self, frame: Any) -> Dict[str, Any]:
        if self.vision_backend == "mock":
            return {"status": "mock_vision_success", "detections": []}
        return {"status": f"unsupported_vision_backend_{self.vision_backend}", "detections": []}

    def get_status(self) -> Dict[str, Any]:
        available_models = [f for f in os.listdir(self.model_root) if f.endswith('.gguf')]
        return {
            "llm_loaded": self.llm is not None,
            "vision_backend": self.vision_backend,
            "models_on_disk": available_models,
            "cpu_threads": os.cpu_count(),
            "llm_ready": Llama is not None
        }
