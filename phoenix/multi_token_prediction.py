"""
phoenix/multi_token_prediction.py
Lookahead Decoding & Tree Verification.
Works in tandem with Medusa heads to verify multi-token predictions.
"""

import torch
import torch.nn as nn
from typing import List, Tuple

class LookaheadDecoder:
    """
    Verifies multiple draft tokens simultaneously using tree-based attention,
    rather than verifying them sequentially in an auto-regressive loop.
    """
    def __init__(self, target_model: nn.Module):
        self.target = target_model

    @torch.no_grad()
    def verify_draft(self, input_ids: torch.Tensor, draft_tokens: torch.Tensor) -> Tuple[torch.Tensor, int]:
        """
        input_ids: (batch, seq) - the established context
        draft_tokens: (batch, K) - the K tokens drafted by Medusa/Draft model
        
        Evaluates the draft tokens against the target model in a single forward pass.
        Returns accepted tokens and the count of accepted tokens.
        """
        batch, seq = input_ids.shape
        K = draft_tokens.shape[1]
        
        # Concatenate context and draft tokens
        combined = torch.cat([input_ids, draft_tokens], dim=1)
        
        # Forward pass on target model
        logits = self.target(combined) # (batch, seq+K, vocab)
        
        # We only care about the logits predicting the draft tokens
        # Target predicting token at pos (seq + i) given context up to (seq + i - 1)
        target_logits = logits[:, seq-1 : seq+K-1, :] # (batch, K, vocab)
        target_preds = target_logits.argmax(dim=-1) # (batch, K)
        
        accepted = []
        for i in range(K):
            if target_preds[0, i] == draft_tokens[0, i]:
                accepted.append(draft_tokens[0, i].item())
            else:
                # Disagreement. Accept the target's prediction as the correction and halt.
                accepted.append(target_preds[0, i].item())
                break
                
        return torch.tensor([accepted], device=input_ids.device), len(accepted)
