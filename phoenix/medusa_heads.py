"""
phoenix/medusa_heads.py
Multi-Token Prediction via Medusa heads.
Adds N dedicated prediction heads to an existing model so it predicts
tokens t+1, t+2, t+3, t+4 in a single forward pass — 3-5x throughput gain.
"""

import torch
import torch.nn as nn
from typing import List, Tuple


class MedusaHead(nn.Module):
    """Single prediction head for token at offset +k."""
    def __init__(self, hidden_dim: int, vocab_size: int, num_layers: int = 1):
        super().__init__()
        layers = []
        for _ in range(num_layers):
            layers.extend([nn.Linear(hidden_dim, hidden_dim), nn.SiLU()])
        layers.append(nn.Linear(hidden_dim, vocab_size))
        self.net = nn.Sequential(*layers)

    def forward(self, hidden: torch.Tensor) -> torch.Tensor:
        return self.net(hidden)


class MedusaDecoder(nn.Module):
    """
    Attaches K Medusa heads to a base model hidden state.
    During inference: predict K future tokens in ONE forward pass.
    During verification: compare against base model's AR output.
    """
    def __init__(self, hidden_dim: int, vocab_size: int,
                 num_heads: int = 4, head_layers: int = 1):
        super().__init__()
        self.num_heads = num_heads
        self.heads = nn.ModuleList([
            MedusaHead(hidden_dim, vocab_size, head_layers)
            for _ in range(num_heads)
        ])

    def forward(self, hidden: torch.Tensor) -> List[torch.Tensor]:
        """
        Returns list of logit tensors, one per head (offset +1, +2, ..., +K).
        hidden: (batch, seq_len, hidden_dim)
        Returns: [logits_+1, logits_+2, ..., logits_+K]  each (batch, seq_len, vocab)
        """
        return [head(hidden) for head in self.heads]

    def generate_draft(self, hidden: torch.Tensor, top_k: int = 1) -> List[torch.Tensor]:
        """
        Greedily samples draft tokens from each head.
        Returns: list of token-id tensors, one per future offset.
        """
        all_logits = self.forward(hidden)
        draft_tokens = []
        for logits in all_logits:
            # Take the last position's prediction
            next_logits = logits[:, -1, :]          # (batch, vocab)
            if top_k == 1:
                token = next_logits.argmax(dim=-1)   # (batch,)
            else:
                topk_vals, topk_ids = torch.topk(next_logits, top_k, dim=-1)
                probs = torch.softmax(topk_vals, dim=-1)
                idx = torch.multinomial(probs, 1).squeeze(-1)
                token = topk_ids[torch.arange(topk_ids.size(0)), idx]
            draft_tokens.append(token)
        return draft_tokens

    @torch.no_grad()
    def verify_and_accept(self, draft_tokens: List[torch.Tensor],
                          base_tokens: List[int]) -> Tuple[List[int], int]:
        """
        Sequential acceptance: accept draft tokens that match the base model.
        Returns (accepted_token_ids, num_accepted).
        """
        accepted = []
        for draft_tok, base_tok in zip(draft_tokens, base_tokens):
            dt = int(draft_tok.squeeze())
            if dt == base_tok:
                accepted.append(dt)
            else:
                accepted.append(base_tok)   # Correction
                break
        return accepted, len(accepted)

    def auxiliary_loss(self, all_logits: List[torch.Tensor],
                       target_ids: torch.Tensor, offset: int = 1) -> torch.Tensor:
        """
        Training loss: head k predicts token at position i+k.
        target_ids: (batch, seq_len) — original token IDs.
        """
        loss = torch.tensor(0.0, requires_grad=True)
        criterion = nn.CrossEntropyLoss()
        for k, logits in enumerate(all_logits, start=offset):
            if k >= target_ids.size(1):
                break
            # Logits from position 0..T-k, targets from position k..T
            pred = logits[:, :-k, :].reshape(-1, logits.size(-1))
            tgt  = target_ids[:, k:].reshape(-1)
            loss = loss + criterion(pred, tgt)
        return loss / len(all_logits)
