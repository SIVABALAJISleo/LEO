import asyncio
import numpy as np
import logging
from orchestration.intelligence.adaptive_downgrade import AdaptiveDowngradeEngine
from orchestration.intelligence.fallback_graph import FallbackGraph
from engine_hv.advanced.progressive_compute import ProgressiveCompute
from engine_hv.advanced.perceptual_metric import PerceptualValidationMetric

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
logger = logging.getLogger("AdvancedIntegration")

async def high_fidelity_compute(params):
    """A simulated heavy GPU-class task."""
    logger.info("Running heavy compute...")
    await asyncio.sleep(1.0)
    return np.ones((128, 128)) * 255

async def approximated_compute(params):
    """A fast CPU-native approximation."""
    logger.info("Running fast approximation...")
    return np.ones((128, 128)) * 200

async def main():
    # 1. Strategy Detection
    downgrade_engine = AdaptiveDowngradeEngine()
    strategy = downgrade_engine.get_quality_strategy(task_priority="normal")
    
    # 2. Fallback Setup
    graph = FallbackGraph()
    graph.register_task("primary_rendering", high_fidelity_compute, fallbacks=["approx_rendering"])
    graph.register_task("approx_rendering", approximated_compute)
    
    # 3. Execution with Progressive Refinement
    logger.info("--- Execution Start ---")
    
    mock_params = {"data": "input_buffer"}

    # Check if we should downgrade immediately based on strategy
    if strategy["tier"] in ["perceptual", "cached", "template"]:
        logger.warning(f"Strategy suggests {strategy['tier']}. Skipping primary.")
        result = await graph.execute("approx_rendering", mock_params)
    else:
        # Try primary with fallbacks
        result = await graph.execute("primary_rendering", mock_params)

    # 4. Perceptual Stopping during Progressive Refinement (Simulated)
    # We compare the current result against a "Goal" if we had one.
    goal = np.ones((128, 128)) * 255
    pvm = PerceptualValidationMetric()
    is_good_enough, psnr = pvm.is_equivalent(goal, result["result"])
    
    print(f"\nFinal Final Status: {result['path']} ({result['status']})")
    print(f"Good Enough? {is_good_enough} (PSNR: {psnr:.2f})\n")

if __name__ == "__main__":
    asyncio.run(main())
