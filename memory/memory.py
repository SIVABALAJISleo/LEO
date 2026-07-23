# Hot-cache memory state with Topological Hypergraph backing
from core_ai.fabric.topological_hypergraph import TopologicalHypergraph

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.paradigm_bypass.layer3_virtual_memory import InfiniteMemoryArchitecture

HOT_CACHE = {}
INFINITE_MEM = InfiniteMemoryArchitecture()

def get_state(key: str):
    # Try infinite memory reconstruction first
    recon = INFINITE_MEM.retrieve(key)
    if recon is not None:
        return recon
    return HOT_CACHE.get(key, "NULL")

def set_state(key: str, value: str):
    HOT_CACHE[key] = value
    # Register in infinite memory
    import numpy as np
    # Convert string to mock float array for HD encoding
    arr = np.array([float(ord(c)) for c in value[:100]], dtype=np.float32)
    if len(arr) == 0: arr = np.zeros(1)
    INFINITE_MEM.store(key, arr)

