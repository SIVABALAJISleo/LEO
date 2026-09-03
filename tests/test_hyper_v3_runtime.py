"""
tests/test_hyper_v3_runtime.py
Unit tests for Device Manager, CPU/iGPU/Hybrid backends, Scheduler, Cache hierarchy, and Buffer pools.
"""

import pytest
import numpy as np
from hyper_v3.runtime.device_manager import DeviceManager
from hyper_v3.runtime.cpu_backend import CPUBackend
from hyper_v3.runtime.igpu_backend import IntelIGPUBackend
from hyper_v3.runtime.hybrid_backend import HybridBackend
from hyper_v3.runtime.scheduler import HeterogeneousScheduler
from hyper_v3.ir.operation import DeviceType
from hyper_v3.memory.cache import CacheHierarchy
from hyper_v3.memory.pools import BufferPool
from hyper_v3.memory.residency import MemoryResidencyTracker


def test_device_manager_and_backends():
    dev_mgr = DeviceManager()
    prof = dev_mgr.get_hardware_profile()
    assert "cpu" in prof
    assert prof["cpu"]["physical_cores"] > 0

    cpu = CPUBackend()
    a = np.ones((8, 8), dtype=np.float32)
    b = np.ones((8, 8), dtype=np.float32)
    c, t_us = cpu.execute_matmul(a, b)
    assert c.shape == (8, 8)
    assert t_us > 0


def test_scheduler_and_hybrid():
    scheduler = HeterogeneousScheduler()
    a = np.ones((16, 16), dtype=np.float32)
    b = np.ones((16, 16), dtype=np.float32)
    c, t_us = scheduler.dispatch_matmul(a, b, DeviceType.CPU)
    assert c.shape == (16, 16)

    hybrid = HybridBackend()
    c_hyb, _ = hybrid.execute_matmul_split(a, b, cpu_ratio=0.5)
    assert c_hyb.shape == (16, 16)


def test_cache_hierarchy_and_pools():
    cache = CacheHierarchy(l1_cap=2, l2_cap=2, l3_cap=2)
    cache.put_l1("k1", "v1")
    cache.put_l1("k2", "v2")
    cache.put_l1("k3", "v3")  # Causes k1 to evict to L2
    assert cache.lookup("k1") == "v1"

    pool = BufferPool()
    buf = pool.acquire((10, 10))
    assert buf.shape == (10, 10)
    pool.release(buf)

    res = MemoryResidencyTracker()
    res.register_buffer("tensor_a", "CPU")
    assert res.is_transfer_needed("tensor_a", "iGPU") is True
