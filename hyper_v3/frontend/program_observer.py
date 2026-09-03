"""
hyper_v3/frontend/program_observer.py
Observes incoming workloads, tensors, and execution streams to capture runtime characteristics.
"""

from typing import Dict, Any, List, Optional
import numpy as np


class ProgramObserver:
    """Monitors workloads to extract operational characteristics, input shapes, and sparsity profiles."""

    @staticmethod
    def inspect_tensor(tensor: np.ndarray) -> Dict[str, Any]:
        """Inspects statistical and structural properties of an operand."""
        if not isinstance(tensor, np.ndarray):
            return {"type": type(tensor).__name__}
        
        flat = tensor.ravel()
        size = flat.size
        if size == 0:
            return {"shape": tensor.shape, "dtype": str(tensor.dtype), "size": 0}
            
        non_zeros = np.count_nonzero(flat)
        sparsity_ratio = 1.0 - (non_zeros / size)
        mean_val = float(np.mean(flat))
        std_val = float(np.std(flat))
        min_val = float(np.min(flat))
        max_val = float(np.max(flat))

        # Check for NaN / Inf
        has_nan = bool(np.isnan(flat).any())
        has_inf = bool(np.isinf(flat).any())

        return {
            "shape": list(tensor.shape),
            "dtype": str(tensor.dtype),
            "size": size,
            "memory_bytes": tensor.nbytes,
            "sparsity_ratio": sparsity_ratio,
            "mean": mean_val,
            "std": std_val,
            "min": min_val,
            "max": max_val,
            "has_nan": has_nan,
            "has_inf": has_inf
        }

    @staticmethod
    def profile_workload(workload_name: str, sample_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Profiles a workload's inputs and memory footprint."""
        tensor_profiles = {}
        total_memory_bytes = 0
        for name, inp in sample_inputs.items():
            if isinstance(inp, np.ndarray):
                prof = ProgramObserver.inspect_tensor(inp)
                tensor_profiles[name] = prof
                total_memory_bytes += prof.get("memory_bytes", 0)
        return {
            "workload_name": workload_name,
            "input_count": len(sample_inputs),
            "tensors": tensor_profiles,
            "total_input_memory_bytes": total_memory_bytes
        }
