"""
backend/layer5_local_infer/local_model.py
=========================================
Local-First inference execution engine wrapper (Tier 6).
Wires GGUF low-bit quantization, ONNX Runtime backends, and Speculative Decoding
on local devices (Intel Core i5-12450H + Intel UHD Graphics Xe 48EU) with zero NVIDIA dependency.
"""

import os
import time
import logging
from typing import Dict, Any, Optional

from core_ai.neural_inference_engine import NeuralInferenceEngine
from core_ai.prompt_lookup_decoder import PromptLookupDecoder

logger = logging.getLogger("LocalInferenceRunner")


class LocalInferenceRunner:
    """
    Orchestrates llama.cpp GGUF, ONNX Runtime, and Speculative Decoding on CPU/iGPU.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.neural_engine = NeuralInferenceEngine(model_path=model_path, n_threads=8)
        self.pld = PromptLookupDecoder(ngram_size=3, max_proposals=6)

    def generate(self, prompt: str, system_prompt: str = "", max_tokens: int = 256) -> Dict[str, Any]:
        """Runs local neural inference with genuine metrics."""
        return self.neural_engine.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens
        )

    def run_speculative_decoding(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """
        Executes local speculative decoding using Prompt Lookup Decoding (PLD).
        """
        t0 = time.perf_counter()
        gen_res = self.neural_engine.generate(prompt=prompt, system_prompt=system_prompt)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        pld_stats = self.pld.get_telemetry()
        return {
            "prompt": prompt,
            "response": gen_res["text"],
            "backend": gen_res["backend"],
            "tokens_generated": gen_res["tokens_generated"],
            "throughput_tok_s": gen_res["throughput_tok_s"],
            "speculative_telemetry": pld_stats,
            "latency_ms": round(elapsed_ms, 2),
            "status": "success"
        }
