"""
hyper_v3/memory/residency.py
Tracks memory buffer residency across CPU, iGPU, and Shared host memory.
"""

from typing import Dict, Any, Optional


class MemoryResidencyTracker:
    """Tracks location of tensor buffers to eliminate unnecessary device transfers."""

    def __init__(self):
        self.residency: Dict[str, str] = {}  # tensor_name -> 'CPU', 'iGPU', 'SHARED'

    def register_buffer(self, tensor_name: str, device: str = "CPU"):
        self.residency[tensor_name] = device

    def get_location(self, tensor_name: str) -> str:
        return self.residency.get(tensor_name, "CPU")

    def update_location(self, tensor_name: str, device: str):
        self.residency[tensor_name] = device

    def is_transfer_needed(self, tensor_name: str, target_device: str) -> bool:
        curr = self.get_location(tensor_name)
        if curr == "SHARED":
            return False
        return curr != target_device
