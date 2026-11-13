"""
tests/test_gpu_unlock_equivalence.py
====================================
Validation suite for GPU-Unlock reverse-engineered formulations and laptop
silicon equivalence engine on Intel Core i5-12450H + Intel UHD Graphics.
"""

import sys
import numpy as np
import pytest

from backend.canonical.gpu_unlock_equivalence_engine import (
    GU_FEAT_PLM_OFFSET,
    GU_FEAT_SS0_OFFSET,
    GU_FEAT_SS1_OFFSET,
    GU_TU102_FEAT_SS0_OFFSET,
    GU_TU102_FEAT_SS1_OFFSET,
    GU_SS0_UNLOCK,
    GU_SS1_UNLOCK,
    NV_SUPPORTED_RECIPES,
    probe_gpu_hardware_topology,
    LocalSiliconCudaEmulator,
    execute_gpu_unlock_equivalence_pipeline,
    GpuUnlockDiagnosticResult,
    GpuUnlockEquivalenceResult,
)
from backend.canonical.functional_replacement_engine import FunctionalReplacementEngine


def test_nv_recipe_database_integrity():
    """Validates reverse-engineered register addresses and V67 gadget offsets."""
    assert GU_FEAT_PLM_OFFSET == 0x00823804
    assert GU_FEAT_SS0_OFFSET == 0x0082381C
    assert GU_FEAT_SS1_OFFSET == 0x00823820
    assert GU_TU102_FEAT_SS0_OFFSET == 0x00409664
    assert GU_TU102_FEAT_SS1_OFFSET == 0x0040966C
    assert GU_SS0_UNLOCK == 0x88888888
    assert GU_SS1_UNLOCK == 0x00000008

    assert "GA102" in NV_SUPPORTED_RECIPES
    assert "AD102" in NV_SUPPORTED_RECIPES
    assert "TU102" in NV_SUPPORTED_RECIPES

    ga102 = NV_SUPPORTED_RECIPES["GA102"]
    assert ga102["gadget_write_entry"] == 0x1110
    assert ga102["unlock_ss0"] == 0x88888888

    ad102 = NV_SUPPORTED_RECIPES["AD102"]
    assert ad102["gadget_write_entry"] == 0x257E
    assert ad102["unlock_ss0"] == 0x88888888

    tu102 = NV_SUPPORTED_RECIPES["TU102"]
    assert tu102["gadget_write_entry"] == 0x10B9
    assert tu102["unlock_ss0"] == 0x88888888


def test_probe_gpu_hardware_topology():
    """Validates hardware topology probe and adaptive strategy selection."""
    diag = probe_gpu_hardware_topology()
    assert isinstance(diag, GpuUnlockDiagnosticResult)
    assert diag.status == "PASS"
    assert isinstance(diag.discrete_nvidia_present, bool)
    assert isinstance(diag.detected_device_name, str)
    assert len(diag.detected_device_name) > 0

    if not diag.discrete_nvidia_present:
        assert diag.intel_equivalence_active is True
        assert "INTEL" in diag.throttle_bypass_strategy


def test_local_silicon_cuda_emulator():
    """Validates CUDA Driver C-ABI and Tensor Core MMA emulation on local silicon."""
    emu = LocalSiliconCudaEmulator()

    # cuInit
    assert emu.cuInit(0) == 0

    # cuMemAlloc & Free
    rc_alloc, dptr = emu.cuMemAlloc_v2(512)
    assert rc_alloc == 0
    assert dptr > 0

    # cuMemcpy HtoD & DtoH
    src = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    assert emu.cuMemcpyHtoD_v2(dptr, src, src.nbytes) == 0

    dst = np.zeros_like(src)
    assert emu.cuMemcpyDtoH_v2(dst, dptr, dst.nbytes) == 0
    np.testing.assert_array_equal(dst, src)

    assert emu.cuMemFree_v2(dptr) == 0

    # cublasGemmEx emulated
    m, k = 16, 32
    A = np.random.uniform(-1.0, 1.0, size=(m, k)).astype(np.float32)
    B = np.random.uniform(-1.0, 1.0, size=(k, 1)).astype(np.float32)
    C_out = emu.cublasGemmEx_emulated(0, 0, m, 1, k, B.ravel(), A)
    assert C_out.shape[0] == m


def test_execute_gpu_unlock_equivalence_pipeline():
    """Validates end-to-end execution of the GPU-unlock equivalence pipeline."""
    res = execute_gpu_unlock_equivalence_pipeline()
    assert isinstance(res, GpuUnlockEquivalenceResult)
    assert res.status == "PASS"
    assert res.usm_page_aligned_4096 is True
    assert res.usm_cacheline_aligned_64 is True
    assert res.avx_vnni_tensor_active is True
    assert res.avx_vnni_exact_match is True
    assert res.avx_vnni_cosine_similarity >= 0.999
    assert res.cuda_driver_interception_verified is True
    assert res.full_external_gpu_replacement is True


def test_functional_replacement_engine_dispatch():
    """Validates FunctionalReplacementEngine dispatch methods for GPU unlock equivalence."""
    engine = FunctionalReplacementEngine()

    diag = engine.probe_gpu_topology()
    assert isinstance(diag, GpuUnlockDiagnosticResult)
    assert diag.status == "PASS"

    res = engine.execute_gpu_unlock_equivalence()
    assert isinstance(res, GpuUnlockEquivalenceResult)
    assert res.status == "PASS"
    assert res.full_external_gpu_replacement is True

