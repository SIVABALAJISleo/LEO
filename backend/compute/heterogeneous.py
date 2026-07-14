import logging
import os
import time
from typing import Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class HeterogeneousComputeEngine:
    """
    Subsystem 2: Heterogeneous Compute Engine.
    Executes neural network models (ONNX/OpenVINO format) prioritizing the iGPU,
    falling back to CPU or DirectML dynamically based on availability.
    """
    def __init__(self):
        self.providers = []
        self._detect_hardware()
        
        # In-memory dictionary for loaded sessions to act as an execution cache.
        self.active_sessions: Dict[str, Any] = {}
        
    def _detect_hardware(self):
        """Attempts to load ONNX Runtime and OpenVINO dynamically to detect iGPU capabilities."""
        try:
            import onnxruntime as ort
            available_providers = ort.get_available_providers()
            logger.info(f"ONNX Runtime available providers: {available_providers}")
            
            # Prioritize OpenVINO and DirectML (Windows iGPU) before CPU
            if 'OpenVINOExecutionProvider' in available_providers:
                self.providers.append('OpenVINOExecutionProvider')
            if 'DmlExecutionProvider' in available_providers:
                self.providers.append('DmlExecutionProvider')
                
            self.providers.append('CPUExecutionProvider')
            
        except ImportError:
            logger.warning("ONNX Runtime not installed. Heterogeneous Compute Engine will use CPU simulators.")
            self.providers = ['CPUExecutionProvider']

    def load_model(self, model_id: str, model_path: str) -> bool:
        """Loads a model into the execution cache."""
        if not os.path.exists(model_path):
            logger.error(f"Model path not found: {model_path}")
            return False
            
        try:
            import onnxruntime as ort
            sess_options = ort.SessionOptions()
            # Optimize graph dynamically
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            
            session = ort.InferenceSession(model_path, sess_options, providers=self.providers)
            self.active_sessions[model_id] = session
            logger.info(f"Successfully loaded {model_id} into Heterogeneous Compute Engine using {session.get_providers()}")
            return True
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            return False

    def execute_inference(self, model_id: str, input_dict: Dict[str, np.ndarray]) -> Optional[np.ndarray]:
        """Runs the model dynamically routing the workload to the best available processor."""
        if model_id not in self.active_sessions:
            logger.error(f"Model {model_id} is not loaded.")
            return None
            
        session = self.active_sessions[model_id]
        
        t0 = time.perf_counter()
        try:
            outputs = session.run(None, input_dict)
            latency = time.perf_counter() - t0
            logger.debug(f"Executed {model_id} via ONNX Runtime in {latency*1000:.2f}ms")
            return outputs
        except Exception as e:
            logger.error(f"Inference failure for {model_id}: {e}")
            return None

    def flush_cache(self):
        """Unloads all models from memory to free RAM/VRAM."""
        self.active_sessions.clear()
        logger.info("Heterogeneous compute cache flushed.")
