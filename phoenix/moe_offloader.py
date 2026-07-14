"""
phoenix/moe_offloader.py
MoE Expert Offloading Engine.
Active experts (Top-2) reside in iGPU/RAM.
Inactive experts are offloaded to CPU RAM with async prefetching.
Simulates 64B total params with only ~2B active at any token.
"""

import torch
import torch.nn as nn
import threading
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class Expert(nn.Module):
    """A single MoE expert: 2-layer FFN sub-network."""
    def __init__(self, hidden_dim: int, ffn_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(hidden_dim, ffn_dim),
            nn.SiLU(),
            nn.Linear(ffn_dim, hidden_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class MoEOffloadingLayer(nn.Module):
    """
    Mixture-of-Experts layer with CPU offloading.
    - Router selects Top-2 experts per token
    - Active experts are moved to compute device on demand
    - Idle experts stay in CPU RAM (zero iGPU VRAM used)
    - Background thread prefetches predicted next experts
    """

    def __init__(self, num_experts: int, hidden_dim: int, ffn_dim: int,
                 top_k: int = 2, compute_device: str = "cpu"):
        super().__init__()
        self.num_experts    = num_experts
        self.top_k          = top_k
        self.compute_device = torch.device(compute_device)

        # Router: decides which experts to activate
        self.router = nn.Linear(hidden_dim, num_experts, bias=False)

        # All experts always stored on CPU
        self.experts = nn.ModuleList([
            Expert(hidden_dim, ffn_dim) for _ in range(num_experts)
        ])

        # Track which experts are currently loaded to compute device
        self._loaded_experts: Dict[int, Expert] = {}
        self._load_lock = threading.Lock()

        logger.info(f"MoEOffloader: {num_experts} experts × {hidden_dim}→{ffn_dim}. "
                    f"Top-{top_k} active per token. Compute: {compute_device}")

    def _load_expert(self, expert_id: int) -> Expert:
        """Move an expert from CPU to compute device."""
        with self._load_lock:
            if expert_id not in self._loaded_experts:
                expert = self.experts[expert_id].to(self.compute_device)
                self._loaded_experts[expert_id] = expert
            return self._loaded_experts[expert_id]

    def _evict_expert(self, expert_id: int):
        """Return an expert to CPU RAM."""
        with self._load_lock:
            if expert_id in self._loaded_experts:
                self.experts[expert_id] = self._loaded_experts.pop(expert_id).cpu()

    def _prefetch_experts_async(self, expert_ids: List[int]):
        """Background thread: pre-load predicted next experts."""
        def _load():
            for eid in expert_ids:
                self._load_expert(eid)
        t = threading.Thread(target=_load, daemon=True)
        t.start()

    def forward(self, x: torch.Tensor,
                prefetch_hint: Optional[List[int]] = None) -> torch.Tensor:
        """
        x: (batch, seq_len, hidden_dim)
        Returns: (batch, seq_len, hidden_dim)
        """
        B, S, H = x.shape
        x_flat = x.reshape(-1, H)                           # (B*S, H)

        # Router logits + Top-K selection
        gate_logits = self.router(x_flat)                   # (B*S, num_experts)
        weights, indices = torch.topk(gate_logits, self.top_k, dim=-1)
        weights = torch.softmax(weights, dim=-1)             # (B*S, top_k)

        output = torch.zeros_like(x_flat)

        # Gather unique expert IDs needed for this batch
        needed_experts = indices.unique().tolist()
        for eid in needed_experts:
            self._load_expert(eid)

        # Dispatch tokens to experts
        for k in range(self.top_k):
            expert_ids_k = indices[:, k]                    # (B*S,)
            w_k          = weights[:, k].unsqueeze(-1)      # (B*S, 1)

            for eid in needed_experts:
                mask = (expert_ids_k == eid)
                if not mask.any():
                    continue
                expert = self._loaded_experts[eid]
                expert_out = expert(x_flat[mask])
                output[mask] += w_k[mask] * expert_out

        # Async prefetch next experts if hint provided
        if prefetch_hint:
            self._prefetch_experts_async(prefetch_hint)

        # Evict experts not needed (save iGPU memory)
        for eid in list(self._loaded_experts.keys()):
            if eid not in needed_experts:
                self._evict_expert(eid)

        return output.reshape(B, S, H)

    def get_memory_stats(self) -> Dict[str, int]:
        return {
            "active_experts_in_memory": len(self._loaded_experts),
            "total_experts": self.num_experts,
            "experts_on_cpu": self.num_experts - len(self._loaded_experts),
        }
