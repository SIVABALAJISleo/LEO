import os
import numpy as np
import mmap

class NVMeTensorPool:
    """
    ZeRO-Infinity inspired NVMe tensor offloading for VRAM virtualization.
    Maps massive parameter/optimizer states directly to disk.
    """
    def __init__(self, cache_dir=".hyper_cache/nvme_pool", pool_size_gb=1):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.pool_file = os.path.join(cache_dir, "virtual_vram.dat")
        
        bytes_size = int(pool_size_gb * 1024**3)
        if not os.path.exists(self.pool_file):
            with open(self.pool_file, "wb") as f:
                f.seek(bytes_size - 1)
                f.write(b"\0")
                
        self.f = open(self.pool_file, "r+b")
        self.mmap_obj = mmap.mmap(self.f.fileno(), 0)
        self.allocation_ptr = 0
        
    def allocate_tensor(self, shape, dtype=np.float32):
        """Returns a numpy array backed by NVMe mmap."""
        num_elements = np.prod(shape)
        bytes_needed = num_elements * np.dtype(dtype).itemsize
        
        if self.allocation_ptr + bytes_needed > len(self.mmap_obj):
            raise MemoryError("NVMe Tensor Pool exhausted")
            
        tensor = np.ndarray(shape, dtype=dtype, buffer=self.mmap_obj, offset=self.allocation_ptr)
        self.allocation_ptr += bytes_needed
        return tensor
        
    def close(self):
        self.mmap_obj.close()
        self.f.close()
