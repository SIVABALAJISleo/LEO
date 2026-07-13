"""
core_ai/hardware_tuner.py
Decide and tune the CPU thread count, batch sizing, context sizing, and power modes
specifically optimized for Intel Core i5-12450H (8 cores: 4P+4E, 12 threads) and iGPU.
"""

import os
import time
import json
import logging
import psutil
import platform
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

# Config files paths
TUNED_CONFIG_PATH = "models/tuned_config.json"

DEFAULT_TUNED_PARAMS = {
    "performance": {
        "threads": 8,           # Matching physical core count
        "batch_size": 32,
        "context_size": 2048,
        "use_igpu": False
    },
    "power_saving": {
        "threads": 4,           # Run on subset to avoid thermal scaling limits
        "batch_size": 8,
        "context_size": 1024,
        "use_igpu": False
    }
}


class LEOHardwareTuner:
    """Tuning harness that runs parameter sweep and selects best settings."""
    
    @staticmethod
    def detect_fingerprint() -> str:
        cpu = platform.processor()
        logical_cores = psutil.cpu_count(logical=True)
        return f"{platform.system()}_{cpu}_{logical_cores}cores"

    def get_optimized_settings(self, mode: str = "performance") -> Dict[str, Any]:
        """Load tuned parameters or fall back to defaults optimized for Intel Core i5-12450H."""
        if os.path.exists(TUNED_CONFIG_PATH):
            try:
                with open(TUNED_CONFIG_PATH, "r") as f:
                    data = json.load(f)
                    fingerprint = self.detect_fingerprint()
                    if data.get("fingerprint") == fingerprint:
                        return data.get("modes", {}).get(mode, DEFAULT_TUNED_PARAMS[mode])
            except Exception:
                pass
        return DEFAULT_TUNED_PARAMS.get(mode, DEFAULT_TUNED_PARAMS["performance"])

    def run_parameter_sweep(self, model_path: str) -> Dict[str, Any]:
        """Runs a physical/theoretical parameter sweep to find optimal inference params."""
        fingerprint = self.detect_fingerprint()
        logger.info(f"[Tuner] Starting parameter sweep for fingerprint: {fingerprint}")
        
        # Default fallback values for i5-12450H
        best_threads = 8
        best_batch = 32
        best_tps = 0.0
        
        # If real model exists and llama_cpp is installed, execute a mini physical sweep
        if os.path.exists(model_path):
            try:
                from llama_cpp import Llama
                # Sweep thread range
                for t in [4, 6, 8, 12]:
                    t0 = time.perf_counter()
                    llm = Llama(model_path=model_path, n_ctx=512, n_threads=t, verbose=False)
                    # Run quick completion
                    start_gen = time.perf_counter()
                    res = llm("Hello, count from 1 to 5.", max_tokens=10)
                    elapsed = time.perf_counter() - start_gen
                    tps = 10.0 / max(0.001, elapsed)
                    logger.info(f"[Tuner Sweep] Thread {t} generated at {tps:.2f} tokens/sec.")
                    if tps > best_tps:
                        best_tps = tps
                        best_threads = t
            except Exception as e:
                logger.warning(f"[Tuner Sweep] Physical parameter sweep failed (falling back to static heuristics): {e}")

        # Construct final settings map
        tuning_report = {
            "fingerprint": fingerprint,
            "sweep_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "modes": {
                "performance": {
                    "threads": best_threads,
                    "batch_size": best_batch,
                    "context_size": 2048,
                    "use_igpu": False
                },
                "power_saving": {
                    "threads": 4,
                    "batch_size": 8,
                    "context_size": 1024,
                    "use_igpu": False
                }
            }
        }

        # Save configuration
        os.makedirs(os.path.dirname(TUNED_CONFIG_PATH) or ".", exist_ok=True)
        with open(TUNED_CONFIG_PATH, "w") as f:
            json.dump(tuning_report, f, indent=2)

        return tuning_report
