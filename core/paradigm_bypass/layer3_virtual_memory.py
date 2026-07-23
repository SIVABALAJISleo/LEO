import numpy as np
import os
import json

class HyperdimensionalCompressor:
    def __init__(self, dim=10000):
        self.dim = dim
        self.codebook = {}

    def compress(self, data) -> np.ndarray:
        # Encode data into binary hypervectors (mocked via hashing and random state)
        if isinstance(data, np.ndarray) and np.issubdtype(data.dtype, np.number):
            seed_val = int(np.sum(np.abs(data)) * 1000)
        else:
            seed_val = abs(hash(str(data)))
            
        np.random.seed(seed_val % (2**32))
        return np.random.randint(0, 2, self.dim, dtype=np.uint8)

    def bundle(self, vecs: list) -> np.ndarray:
        if not vecs: return np.zeros(self.dim, dtype=np.uint8)
        sum_vec = np.sum(vecs, axis=0)
        return (sum_vec > (len(vecs) / 2)).astype(np.uint8)

    def decompress(self, hd_vec: np.ndarray) -> np.ndarray:
        # Decode HD back to approximate FP32 (Mock representation)
        return (hd_vec.astype(np.float32) - 0.5) * 2.0

class InfiniteMemoryArchitecture:
    def __init__(self, disk_path=".hyper_cache/virtual_vram", cache_size_gb=2):
        self.disk_path = disk_path
        self.cache_size_gb = cache_size_gb
        self.compressor = HyperdimensionalCompressor()
        
        # RAM Cache
        self.ram_cache = {}
        self.access_tracker = {}
        
        if not os.path.exists(disk_path):
            os.makedirs(disk_path, exist_ok=True)

    def _get_disk_file(self, key):
        return os.path.join(self.disk_path, f"{hash(str(key))}.hd")

    def store(self, key, data: np.ndarray):
        hd_data = self.compressor.compress(data)
        
        # Cache in RAM
        key_str = str(key)
        self.ram_cache[key_str] = hd_data
        self.access_tracker[key_str] = 1
        
        # Write to SSD
        np.save(self._get_disk_file(key_str), hd_data)
        
        # Very simple eviction
        if len(self.ram_cache) > 10000:
            least_used = min(self.access_tracker, key=lambda k: self.access_tracker[k])
            del self.ram_cache[least_used]
            del self.access_tracker[least_used]

    def retrieve(self, key) -> np.ndarray | None:
        key_str = str(key)
        # 1. Check RAM cache
        if key_str in self.ram_cache:
            self.access_tracker[key_str] += 1
            return self.compressor.decompress(self.ram_cache[key_str])
            
        # 2. Check SSD
        disk_file = self._get_disk_file(key_str)
        if os.path.exists(disk_file + ".npy"):
            hd_data = np.load(disk_file + ".npy")
            self.ram_cache[key_str] = hd_data
            self.access_tracker[key_str] = 1
            return self.compressor.decompress(hd_data)
            
        return None
