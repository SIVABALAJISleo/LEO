"""
tests/test_sparsity.py
Tests the Wanda pruning algorithm for extreme sparsity.
"""
import logging
import torch
import torch.nn as nn
import sys, os

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phoenix.extreme_sparsity import WandaPruner

def test_wanda_pruning():
    logger.info("[Test] Extreme Sparsity (Wanda Pruning)")
    
    # 1. Create a simple model
    model = nn.Sequential(
        nn.Linear(10, 20),
        nn.ReLU(),
        nn.Linear(20, 5)
    )
    
    # 2. Init Pruner
    pruner = WandaPruner(sparsity_ratio=0.5)
    
    # 3. Attach calibration hooks
    pruner.attach_calibration_hooks(model)
    
    # 4. Run dummy calibration pass
    dummy_input = torch.randn(4, 10)
    model(dummy_input)
    
    # 5. Remove hooks
    pruner.remove_hooks()
    
    # 6. Apply pruning
    pruner.apply_pruning(model)
    
    # 7. Verify 50% sparsity was induced
    total_weights = 0
    zero_weights = 0
    for module in model.modules():
        if isinstance(module, nn.Linear):
            W = module.weight.data
            total_weights += W.numel()
            zero_weights += (W == 0).sum().item()
            
    sparsity = zero_weights / total_weights
    
    logger.info(f"Target Sparsity: 0.5, Actual Sparsity: {sparsity}")
    # Due to index rounding, it might be slightly off, but should be exactly 0.5 for round numbers
    assert abs(sparsity - 0.5) < 0.05, f"Sparsity {sparsity} is too far from target 0.5"
    logger.info("✅ Extreme Sparsity WANDA Pruner verified.")

if __name__ == "__main__":
    test_wanda_pruning()
