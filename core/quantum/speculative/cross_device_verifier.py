"""
LEO Cross-Device Logit Verifier
Handles logit sync and verification across CPU and iGPU.
"""
import torch

class CrossDeviceVerifier:
    """
    Validates candidate token probabilities across heterogeneous silicon boundaries.
    """
    
    def __init__(self, tolerance: float = 1e-5):
        self.tolerance = tolerance
        
    def verify_logits_match(self, device_a_logits: torch.Tensor, device_b_logits: torch.Tensor) -> bool:
        """Determines if logits align within floating-point tolerance limits"""
        diff = torch.abs(device_a_logits.cpu() - device_b_logits.cpu())
        max_diff = torch.max(diff).item()
        return max_diff < self.tolerance

    def align_distributions(self, target_probs: torch.Tensor, draft_probs: torch.Tensor) -> torch.Tensor:
        """Adjusts target probability distribution on rejection for correct sampling"""
        # Calculate scaling factor to adjust probability distributions
        diff = target_probs - draft_probs
        adjusted = torch.clamp(diff, min=0.0)
        sum_val = torch.sum(adjusted, dim=-1, keepdim=True)
        return adjusted / torch.maximum(sum_val, torch.tensor(1e-9))
