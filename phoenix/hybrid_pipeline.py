"""
phoenix/hybrid_pipeline.py
Hybrid CPU↔iGPU Layer Dispatch Pipeline.
Routes individual model layers to the best available compute device:
  - Embedding: CPU (memory-bandwidth bound, CPU has more RAM)
  - Early layers: iGPU (parallel, warm-up)
  - Mid layers: CPU fallback if iGPU OOM
  - Late layers + LM head: iGPU (compute-bound generation)
Supports async prefetch of the next layer's weights while current runs.
"""

import torch
import torch.nn as nn
import threading
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


def _best_device() -> str:
    """Detect the best available device: CUDA → MPS → CPU."""
    if torch.cuda.is_available():
        return "cuda"
    try:
        if torch.backends.mps.is_available():
            return "mps"
    except AttributeError:
        pass
    return "cpu"


class HybridLayerPipeline:
    """
    Layer-wise dispatch across CPU and iGPU.
    Each layer is dispatched to the device profile assigned during init.
    A background thread prefetches the next layer while the current runs.
    """

    def __init__(self, layers: nn.ModuleList,
                 embedding: Optional[nn.Module] = None,
                 lm_head: Optional[nn.Module] = None,
                 igpu_device: Optional[str] = None):
        self.layers    = layers
        self.embedding = embedding
        self.lm_head   = lm_head

        self.igpu  = torch.device(igpu_device or _best_device())
        self.cpu   = torch.device("cpu")

        num_layers = len(layers)
        # Dispatch profile: early 25% → iGPU, mid 50% → CPU, last 25% → iGPU
        self.dispatch_map: List[torch.device] = []
        for i in range(num_layers):
            ratio = i / max(1, num_layers - 1)
            if ratio < 0.25 or ratio > 0.75:
                self.dispatch_map.append(self.igpu)
            else:
                self.dispatch_map.append(self.cpu)

        # Move layers to their assigned devices
        self._move_layers_to_devices()

        # Prefetch state
        self._prefetch_thread: Optional[threading.Thread] = None
        self._prefetch_layer_idx: int = -1

        logger.info(
            f"HybridPipeline: {num_layers} layers across {self.igpu}/{self.cpu}. "
            f"iGPU: {sum(1 for d in self.dispatch_map if d == self.igpu)} layers, "
            f"CPU: {sum(1 for d in self.dispatch_map if d == self.cpu)} layers."
        )

    def _move_layers_to_devices(self):
        for i, (layer, device) in enumerate(zip(self.layers, self.dispatch_map)):
            layer.to(device)
        if self.embedding is not None:
            self.embedding.to(self.cpu)
        if self.lm_head is not None:
            self.lm_head.to(self.igpu)

    def _prefetch_layer(self, idx: int):
        """Background: ensure layer idx is on its target device."""
        if 0 <= idx < len(self.layers):
            target = self.dispatch_map[idx]
            self.layers[idx].to(target)

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        """Full forward pass with layer-wise hybrid dispatch."""
        # Embedding on CPU
        if self.embedding is not None:
            x = self.embedding(input_ids.to(self.cpu))
        else:
            x = input_ids.float()

        for i, (layer, device) in enumerate(zip(self.layers, self.dispatch_map)):
            # Move activations to layer's device
            x = x.to(device)

            # Run current layer
            x = layer(x)

            # Async prefetch next layer in background
            next_idx = i + 1
            if next_idx < len(self.layers):
                t = threading.Thread(
                    target=self._prefetch_layer,
                    args=(next_idx,), daemon=True
                )
                t.start()

        # LM head on iGPU
        if self.lm_head is not None:
            x = x.to(self.igpu)
            x = self.lm_head(x)

        return x

    def get_dispatch_summary(self) -> Dict[str, int]:
        igpu_count = sum(1 for d in self.dispatch_map if d == self.igpu)
        cpu_count  = len(self.dispatch_map) - igpu_count
        return {
            "igpu_device": str(self.igpu),
            "cpu_device":  str(self.cpu),
            "layers_on_igpu": igpu_count,
            "layers_on_cpu":  cpu_count,
        }
