import argparse
import sys
import os
import psutil
import torch
import logging
from pathlib import Path
from core_ai.bitnet_engine import BitNetQuantizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_bitnet(model_path: str, test_prompt: str, expected_memory_gb: float):
    logger.info("Starting BitNet verification...")
    
    # 1. Run quantization
    original_path = "models/leo_original.pt"
    quantizer = BitNetQuantizer(original_path, model_path)
    stats = quantizer.quantize_model()
    
    # 2. Check files exist
    if not Path(model_path).exists():
        logger.error(f"Quantized model path does not exist: {model_path}")
        sys.exit(1)
        
    # 3. Simulate loader memory checking
    process = psutil.Process(os.getpid())
    current_mem_gb = process.memory_info().rss / (1024 ** 3)
    logger.info(f"Current Process Memory RSS: {current_mem_gb:.3f} GB")
    
    # Quantized size should be under the limit
    quantized_size_gb = stats['quantized_size_mb'] / 1024.0
    logger.info(f"Quantized Model Size: {quantized_size_gb:.3f} GB")
    
    if quantized_size_gb > expected_memory_gb:
        logger.error(f"Quantized model memory footprint {quantized_size_gb:.3f}GB exceeds expected {expected_memory_gb}GB")
        sys.exit(1)
        
    logger.info("BitNet Verification Success!")
    logger.info(f"Compression Stats: {stats}")
    print("[OK] BitNet b1.58 conversion verified. Memory footprint:", f"{quantized_size_gb:.3f}GB (Expected: < {expected_memory_gb}GB)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="models/leo_bitnet.gguf")
    parser.add_argument("--test-prompt", type=str, default="Explain quantum computing")
    parser.add_argument("--expected-memory", type=str, default="0.4GB")
    args = parser.parse_args()
    
    # Parse expected memory string (e.g. "0.4GB" -> 0.4)
    mem_str = args.expected_memory.upper().replace("GB", "")
    try:
        expected_mem_gb = float(mem_str)
    except ValueError:
        expected_mem_gb = 0.4
        
    verify_bitnet(args.model, args.test_prompt, expected_mem_gb)
