import argparse
import sys
import numpy as np
import logging
from core_ai.heterogeneous_orchestrator import HeterogeneousOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_heterogeneous(model_path: str, expected_speedup: float):
    logger.info("Initializing Heterogeneous Execution Orchestrator...")
    orchestrator = HeterogeneousOrchestrator()
    
    logger.info(f"Compiling model for {model_path}...")
    compiled_model = orchestrator.compile_heterogeneous_model(model_path)
    
    # Generate dummy input (e.g. random array)
    test_input = {"input": np.random.randn(1, 1024).astype(np.float32)}
    
    logger.info("Running benchmarks...")
    metrics = orchestrator.benchmark_heterogeneous(compiled_model, test_input)
    
    cpu_tps = metrics['cpu_only']['tokens_per_second']
    hetero_tps = metrics['heterogeneous']['tokens_per_second']
    actual_speedup = hetero_tps / cpu_tps
    
    logger.info(f"Performance Metrics: {metrics}")
    logger.info(f"Measured Heterogeneous Speedup: {actual_speedup:.2f}x")
    
    if actual_speedup < expected_speedup:
        logger.error(f"Heterogeneous speedup {actual_speedup:.2f}x is below expected {expected_speedup}x")
        sys.exit(1)
        
    logger.info("Heterogeneous Execution Orchestration verified successfully!")
    print(f"[OK] Heterogeneous execution verified. Speedup: {actual_speedup:.2f}x (Expected: >= {expected_speedup}x)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="models/leo_bitnet.xml")
    parser.add_argument("--expected-speedup", type=str, default="2.5x")
    args = parser.parse_args()
    
    # Parse expected speedup string (e.g. "2.5x" -> 2.5)
    speedup_str = args.expected_speedup.lower().replace("x", "")
    try:
        expected_speedup = float(speedup_str)
    except ValueError:
        expected_speedup = 2.5
        
    verify_heterogeneous(args.model, expected_speedup)
