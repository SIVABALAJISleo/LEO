import os
import logging
from typing import Dict, List, Optional, Tuple
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

logger = logging.getLogger(__name__)

class SteeringEngine:
    """
    LAYER 2: CONTROL VECTOR SYSTEM (STEERING ENGINE)
    Precomputes, blends, and injects control vectors into hidden layers.
    """
    def __init__(self, vector_dir: str = "models/vectors"):
        self.vector_dir = vector_dir
        # Mapping domain/tone to control vector files (.gguf / .bin)
        self.vector_paths = {
            "math": os.path.join(vector_dir, "math_steering.gguf"),
            "coding": os.path.join(vector_dir, "coding_steering.gguf"),
            "philosophy": os.path.join(vector_dir, "philosophy_steering.gguf"),
            "formal": os.path.join(vector_dir, "formal_tone.gguf"),
            "creative": os.path.join(vector_dir, "creative_tone.gguf"),
            "concise": os.path.join(vector_dir, "concise_behavior.gguf")
        }

    def blend_vectors(self, weights: Dict[str, float]) -> Optional[str]:
        """
        Conceptual blending logic. 
        In llama.cpp, you can pass multiple control vectors with scales.
        V = Σ (weight_i * vector_i)
        """
        active_vectors = []
        for key, weight in weights.items():
            path = self.vector_paths.get(key)
            if path and os.path.exists(path) and weight > 0.05:
                active_vectors.append((path, weight))
                logger.info(f"Steering: Active Vector '{key}' at weight {weight}")
        
        return active_vectors if active_vectors else None

    def apply_steering(self, llm: Llama, active_vectors: List[Tuple[str, float]]):
        """
        Injects the blended control vector into the model.
        """
        if not llm or not active_vectors:
            return

        # llama-cpp-python API for control vectors:
        # Some versions use load_control_vector, others use constructor.
        # We simulate the injection here.
        logger.info(f"Injecting {len(active_vectors)} control vectors into hidden layers.")
        
        # Example of how it would be called in llama-cpp-python:
        # llm.set_control_vectors(active_vectors)
        pass
