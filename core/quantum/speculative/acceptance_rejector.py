"""
LEO Speculative Token Acceptance Rejector
Implements decision policies (greedy, stochastic/nucleus) for token verification.
"""
import torch

class AcceptanceRejector:
    """
    Evaluates proposed tokens and decides whether to accept or reject them.
    """
    
    def __init__(self, mode: str = 'stochastic'):
        self.mode = mode
        
    def should_accept(
        self,
        draft_token: int,
        target_probs: torch.Tensor,
        draft_probs: torch.Tensor
    ) -> bool:
        """
        Acceptance rule using target and draft token probabilities.
        """
        if self.mode == 'greedy':
            return draft_token == torch.argmax(target_probs).item()
            
        # Stochastic criterion: min(1, P(x) / Q(x))
        p_val = target_probs[0, draft_token].item()
        q_val = draft_probs[0, draft_token].item()
        
        if q_val <= 0.0:
            return False
            
        ratio = p_val / q_val
        if ratio >= 1.0:
            return True
            
        # Sample uniformly to decide
        rand_val = torch.rand(1).item()
        return rand_val < ratio
