import argparse
import sys
import logging
from core_ai.speculative_decoder import SpeculativeDecoder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_speculative(model_path: str, expected_speedup: float):
    logger.info("Initializing Speculative Decoding Engine...")
    decoder = SpeculativeDecoder(model_path, max_draft_tokens=8)
    
    prompt = "Explain quantum computing"
    logger.info(f"Running speculative decoding on prompt: '{prompt}'...")
    output, performance = decoder.generate(prompt, max_tokens=100)
    
    actual_speedup = performance['speedup_vs_standard']
    logger.info(f"Generated text: {output}")
    logger.info(f"Performance statistics: {performance}")
    logger.info(f"Measured Speculative Speedup: {actual_speedup:.2f}x")
    
    if actual_speedup < expected_speedup:
        logger.error(f"Speculative decoding speedup {actual_speedup:.2f}x is below expected {expected_speedup}x")
        sys.exit(1)
        
    logger.info("Speculative Decoding verified successfully!")
    print(f"[OK] Speculative decoding verified. Speedup: {actual_speedup:.2f}x (Expected: >= {expected_speedup}x)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="models/leo_bitnet.gguf")
    parser.add_argument("--expected-speedup", type=str, default="8x")
    args = parser.parse_args()
    
    # Parse expected speedup string (e.g. "8x" -> 8)
    speedup_str = args.expected_speedup.lower().replace("x", "")
    try:
        expected_speedup = float(speedup_str)
    except ValueError:
        expected_speedup = 8.0
        
    verify_speculative(args.model, expected_speedup)
