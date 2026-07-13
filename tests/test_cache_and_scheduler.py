"""
tests/test_cache_and_scheduler.py
Verifies functional CPU memory pooling, work-stealing scheduler mapping, and object allocator leak diagnostics.
"""

import os
import time
import numpy as np
import pytest
from core_ai.cache_manager import MemoryPool, WeightPrefetcher, CacheLocalityProfiler
from core_ai.task_scheduler import WorkStealingScheduler
from core_ai.memory_manager import MemoryManager

def test_memory_pool_allocation():
    pool = MemoryPool(size_bytes=1024)
    # 1024 bytes = 256 float32 elements
    # Alloc block size = 256 / 1024 = 0.25 (rounds to 1 block minimum)
    
    alloc_id1, arr1 = pool.allocate(10)
    assert len(arr1) == 10
    assert arr1.dtype == np.float32
    
    # Try allocate remaining space
    alloc_id2, arr2 = pool.allocate(240)
    assert len(arr2) == 240
    
    # Exceed allocation limit
    with pytest.raises(MemoryError):
        pool.allocate(50)
        
    # Free space and try again
    pool.free(alloc_id1)
    alloc_id3, arr3 = pool.allocate(10)
    assert len(arr3) == 10

def test_weight_prefetcher():
    prefetcher = WeightPrefetcher()
    prefetcher.request_prefetch("layer1.weight", (100, 100))
    
    # Wait briefly for background prefetch thread execution
    time.sleep(0.1)
    w = prefetcher.get_prefetched_weight("layer1.weight")
    assert w is not None
    assert w.shape == (100, 100)

def test_cache_locality_profiler():
    metrics = CacheLocalityProfiler.profile_cache_misses(size=10000)
    assert "estimated_cache_miss_penalty_multiplier" in metrics
    assert metrics["ns_per_op_contiguous"] > 0

def test_work_stealing_scheduler():
    scheduler = WorkStealingScheduler(num_threads=2)
    
    # Submit multiple compute tasks
    def workload(x):
        return x * x
        
    results = scheduler.map(workload, [1, 2, 3, 4, 5])
    assert results == [1, 4, 9, 16, 25]
    
    scheduler.shutdown()

def test_memory_manager_diagnostics():
    mgr = MemoryManager()
    
    # Normal allocation from preallocated blocks pool
    lease_id1, arr1 = mgr.allocate(100)
    assert len(arr1) == 100
    
    # Check diagnostics
    diag = mgr.get_memory_diagnostics()
    assert diag["pool_hits"] == 1
    assert diag["active_blocks_pool"] == 1
    
    # Recycle
    mgr.recycle(lease_id1)
    
    # Fallback allocate (exceeds preallocated bucket size limits)
    lease_id2, arr2 = mgr.allocate(50_000_000)
    diag2 = mgr.get_memory_diagnostics()
    assert diag2["pool_misses"] == 1


def test_safety_governor():
    from core_ai.governor import LEOSafetyGovernor
    import tempfile
    
    gov = LEOSafetyGovernor(max_concurrent_requests=2, min_available_ram_gb=0.1)
    
    # Test slot acquisition and concurrency limits
    assert gov.acquire_slot() is True
    assert gov.acquire_slot() is True
    assert gov.acquire_slot() is False # Queue backpressure triggered
    
    gov.release_slot()
    assert gov.acquire_slot() is True
    
    # Test safety checks
    safety = gov.check_system_safety()
    assert "status" in safety
    assert "available_ram_gb" in safety

    # Test cache cleaning
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a test cache file
        cache_file = os.path.join(tmp_dir, "cache_entry.json")
        with open(cache_file, "w") as f:
            f.write("{}" * 1000)
            
        gov_small_cache = LEOSafetyGovernor(max_cache_dir_size_mb=0.0001) # very small limit
        gov_small_cache.enforce_cache_limits(tmp_dir)
        # Should delete the file since it exceeds limit
        assert not os.path.exists(cache_file)
