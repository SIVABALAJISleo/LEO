"""
Unified Memory Router for CPU/iGPU/SSD memory management
"""
import torch
import numpy as np
import psutil
from typing import Dict, Any, Optional

class UnifiedMemoryRouter:
    """
    Manages memory allocation across CPU RAM, iGPU shared memory, and SSD
    for optimal utilization of available memory resources.
    """
    
    def __init__(self):
        self.cpu_memory_pool = {}
        self.igpu_memory_pool = {}
        self.ssd_cache = {}
        self.memory_pressure = 0.0
        self.swap_threshold = 0.85  # Start swapping at 85% memory usage
        
    def allocate_tensor(
        self,
        shape: tuple,
        dtype: torch.dtype = torch.float32,
        preferred_device: str = 'auto'
    ) -> torch.Tensor:
        """
        Allocate tensor on optimal memory device based on availability
        """
        if preferred_device == 'auto':
            device = self._select_optimal_device(shape, dtype)
        else:
            device = preferred_device
            
        if device == 'cpu':
            return self._allocate_cpu(shape, dtype)
        elif device == 'igpu':
            return self._allocate_igpu(shape, dtype)
        elif device == 'ssd':
            return self._allocate_ssd_backed(shape, dtype)
        else:
            return self._allocate_cpu(shape, dtype)
    
    def _select_optimal_device(self, shape: tuple, dtype: torch.dtype) -> str:
        """Select optimal memory device based on current memory state"""
        element_size = torch.tensor([], dtype=dtype).element_size()
        required_bytes = int(np.prod(shape)) * element_size
        cpu_available = psutil.virtual_memory().available
        
        if cpu_available > required_bytes * 2:
            return 'cpu'
        elif self._igpu_memory_available() > required_bytes:
            return 'igpu'
        else:
            return 'ssd'

    def _igpu_memory_available(self) -> int:
        """Simulated iGPU memory available (shared system RAM)"""
        # Since Intel UHD uses shared RAM, we return a fraction of remaining free memory
        return int(psutil.virtual_memory().available * 0.4)

    def _allocate_cpu(self, shape: tuple, dtype: torch.dtype) -> torch.Tensor:
        return torch.zeros(shape, dtype=dtype, device='cpu')

    def _allocate_igpu(self, shape: tuple, dtype: torch.dtype) -> torch.Tensor:
        # iGPU memory maps to CPU memory with specialized cache policies in Intel architectures
        # In PyTorch, we represent it as a standard CPU or CUDA tensor if available
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        return torch.zeros(shape, dtype=dtype, device=device)

    def _allocate_ssd_backed(self, shape: tuple, dtype: torch.dtype) -> torch.Tensor:
        # SSD backed returns a CPU tensor, but simulates paging to SSD
        # In a real environment, this might use memory mapping (mmap)
        return torch.zeros(shape, dtype=dtype, device='cpu')
