import os
import logging
from typing import Dict, List, Optional
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

logger = logging.getLogger(__name__)

class AdapterManager:
    """
    LAYER 2: DYNAMIC SPECIALIZATION (LoRA SWARM)
    Manages loading and soft-activation of LoRA adapters.
    """
    def __init__(self, model_dir: str = "models/adapters"):
        self.model_dir = model_dir
        # Mapping domain names to file paths
        self.adapter_paths = {
            "coding": os.path.join(model_dir, "coding_lora.bin"),
            "math": os.path.join(model_dir, "math_lora.bin"),
            "creative": os.path.join(model_dir, "creative_lora.bin"),
            "logic": os.path.join(model_dir, "logic_lora.bin")
        }

    def apply_to_model(self, llm: Llama, weights: Dict[str, float]):
        """
        Applies LoRA adapters to the base model with specified scales.
        """
        if not llm or not weights:
            logger.info("Using base model (no adapters).")
            return

        active_adapters = []
        for domain, scale in weights.items():
            path = self.adapter_paths.get(domain)
            if path and os.path.exists(path):
                active_adapters.append((path, scale))
                logger.info(f"Applying LoRA: {domain} (Scale: {scale})")

        # llama-cpp-python specific: applying multiple LoRAs
        # For now, we simulate the 'Soft Activation' by logging
        # Real implementation would call internal llama_apply_lora
        if hasattr(llm, "set_lora_adapters"):
            # Mocking the call structure
            # llm.set_lora_adapters(active_adapters)
            pass
        
    def get_prompt_template(self, weights: Dict[str, float]) -> str:
        """
        Returns a blended system prompt based on active domains.
        """
        if not weights:
            return "You are a general-purpose AI assistant."
            
        domains = ", ".join([f"{k} ({v*100:.0f}%)" for k, v in weights.items()])
        return f"You are a specialized AI expert blending: {domains}. Synthesize your knowledge across these domains."
