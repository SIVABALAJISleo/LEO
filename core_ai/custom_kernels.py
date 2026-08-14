# core_ai/custom_kernels.py
# THE REAL PHOTOSYNTHESIS: Let C++ do the math, Python just orchestrates.
from llama_cpp import Llama
import os

class RealNativeEngine:
    _instance = None

    def __init__(self):
        if RealNativeEngine._instance is None:
            print("[LEO] Initializing Real C++ Engine (llama.cpp)...")
            # Default to the BitNet model path
            model_path = os.environ.get("LEO_MODEL_PATH", "models/bitnet-b1.58-2b.gguf")
            
            # Fallback to pre-existing Qwen model if the BitNet model is not downloaded
            if not os.path.exists(model_path):
                fallback_path = "models/qwen2.5-0.5b-instruct-q4_k_m.gguf"
                if os.path.exists(fallback_path):
                    print(f"[LEO] Warning: '{model_path}' not found. Falling back to existing Qwen model at '{fallback_path}'.")
                    model_path = fallback_path
            
            print(f"[LEO] Loading model from: {model_path}")
            self.llm = Llama(
                model_path=model_path,
                n_ctx=2048,
                n_threads=8,          # Use all i5 physical/performance cores
                n_gpu_layers=0,       # CPU only for stability on laptop
                use_mlock=True        # Lock memory to prevent swapping
            )
            RealNativeEngine._instance = self
        else:
            self.llm = RealNativeEngine._instance.llm

    def generate(self, prompt, max_tokens=128):
        # This runs real AVX2 C++ assembly, not slow Python Numba loops
        response = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=0.7,
            stop=["</s>"]
        )
        return response["choices"][0]["text"]

# Remove the fake Numba ternary matmul completely. 
# llama.cpp handles BitNet quantization natively in C++.
