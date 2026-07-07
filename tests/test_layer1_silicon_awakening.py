"""
tests/test_layer1_silicon_awakening.py
Layer 1 — Silicon Awakening: unit & integration tests for hardware detection,
routing, and the universal execution dispatcher.
"""

import pytest
import asyncio
import platform
from unittest.mock import patch, MagicMock
from dataclasses import dataclass

from backend.hardware.detector import (
    HardwareDetector,
    HardwareProfile,
    CPUProfile,
    GPUProfile,
    NPUProfile,
)
from backend.hardware.router import HeterogeneousRouter
from backend.hardware.universal_execution import UniversalExecutionLayer


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def minimal_cpu():
    return CPUProfile(
        cores=4, threads=8,
        architecture="x86_64", processor="Intel Core i5",
        avx2=True, avx512=False, avx512_vnni=False, amx=False, neon=False,
    )


@pytest.fixture
def amx_cpu():
    return CPUProfile(
        cores=16, threads=32,
        architecture="x86_64", processor="Intel Core Ultra 7",
        avx2=True, avx512=True, avx512_vnni=True, amx=True, neon=False,
    )


@pytest.fixture
def arm_cpu():
    return CPUProfile(
        cores=8, threads=8,
        architecture="arm64", processor="Apple M2",
        avx2=False, avx512=False, avx512_vnni=False, amx=False, neon=True, sme=True,
    )


@pytest.fixture
def vulkan_igpu():
    return GPUProfile(
        vendor="Intel Iris Xe", vram_shared_mb=4096,
        vulkan=True, opencl=True, directml=True,
        devices=["Intel Iris Xe Graphics"],
        igpu_detected=True,
    )


@pytest.fixture
def metal_igpu():
    return GPUProfile(
        vendor="Apple M2 GPU", vram_shared_mb=16384,
        metal=True,
        devices=["Apple M2 GPU"],
        igpu_detected=True,
    )


@pytest.fixture
def directml_npu():
    return NPUProfile(
        vendor="Intel NPU", tops=11, api="DirectML", has_npu=True, type="Intel NPU"
    )


@pytest.fixture
def apple_npu():
    return NPUProfile(
        vendor="Apple", tops=15, api="CoreML", has_npu=True, type="Apple Neural Engine (ANE)"
    )


def _make_profile(cpu, igpu, npu=None):
    return HardwareProfile(
        cpu=cpu,
        igpu=igpu,
        npu=npu if npu else NPUProfile(),
        ram_total_gb=16.0,
        ram_available_gb=8.0,
    )


# ── CPUProfile tests ──────────────────────────────────────────────────────────

class TestCPUProfile:
    def test_minimal_cpu_fields(self, minimal_cpu):
        assert minimal_cpu.cores == 4
        assert minimal_cpu.threads == 8
        assert minimal_cpu.avx2 is True
        assert minimal_cpu.amx is False

    def test_amx_cpu_flags(self, amx_cpu):
        assert amx_cpu.amx is True
        assert amx_cpu.avx512_vnni is True
        assert amx_cpu.avx512 is True

    def test_arm_cpu_flags(self, arm_cpu):
        assert arm_cpu.neon is True
        assert arm_cpu.sme is True
        assert arm_cpu.amx is False


# ── GPUProfile tests ──────────────────────────────────────────────────────────

class TestGPUProfile:
    def test_vulkan_igpu(self, vulkan_igpu):
        assert vulkan_igpu.vulkan is True
        assert vulkan_igpu.igpu_detected is True
        assert vulkan_igpu.vram_shared_mb == 4096

    def test_metal_igpu(self, metal_igpu):
        assert metal_igpu.metal is True
        assert metal_igpu.has_nvidia is False


# ── NPUProfile tests ──────────────────────────────────────────────────────────

class TestNPUProfile:
    def test_intel_npu(self, directml_npu):
        assert directml_npu.has_npu is True
        assert directml_npu.api == "DirectML"
        assert directml_npu.tops > 0

    def test_apple_npu(self, apple_npu):
        assert apple_npu.has_npu is True
        assert apple_npu.api == "CoreML"
        assert apple_npu.tops >= 11


# ── HardwareDetector live tests ───────────────────────────────────────────────

class TestHardwareDetector:
    def test_get_system_profile_returns_hardware_profile(self):
        profile = HardwareDetector.get_system_profile()
        assert isinstance(profile, HardwareProfile)

    def test_cpu_has_cores(self):
        cpu = HardwareDetector.get_cpu_info()
        assert cpu.cores >= 1
        assert cpu.threads >= cpu.cores

    def test_gpu_info_has_vram(self):
        gpu = HardwareDetector.get_gpu_info()
        assert gpu.vram_shared_mb > 0

    def test_npu_info_returns_npu_profile(self):
        npu = HardwareDetector.get_npu_info()
        assert isinstance(npu, NPUProfile)

    def test_profile_backward_compat_get(self):
        profile = HardwareDetector.get_system_profile()
        ram = profile.get("ram")
        assert ram is not None
        assert "total_gb" in ram

    def test_profile_get_unknown_key(self):
        profile = HardwareDetector.get_system_profile()
        assert profile.get("nonexistent_key", "default") == "default"


# ── HeterogeneousRouter tests ─────────────────────────────────────────────────

class TestHeterogeneousRouter:
    def test_score_backends_returns_sorted_list(self, minimal_cpu, vulkan_igpu):
        profile = _make_profile(minimal_cpu, vulkan_igpu)
        router = HeterogeneousRouter(profile)
        ranked = router.score_backends()
        assert len(ranked) >= 1
        # Verify descending order
        scores = [score for _, score in ranked]
        assert scores == sorted(scores, reverse=True)

    def test_vulkan_igpu_outscores_cpu(self, minimal_cpu, vulkan_igpu):
        profile = _make_profile(minimal_cpu, vulkan_igpu)
        router = HeterogeneousRouter(profile)
        ranked = dict(router.score_backends())
        assert ranked.get("vulkan", 0) > ranked.get("cpu_generic", 1)

    def test_amx_cpu_outscores_generic_cpu(self, amx_cpu):
        gpu = GPUProfile()  # no iGPU
        profile = _make_profile(amx_cpu, gpu)
        router = HeterogeneousRouter(profile)
        ranked = dict(router.score_backends())
        assert ranked.get("cpu_amx", 0) > ranked.get("cpu_generic", 0)

    def test_build_device_plan_has_cpu_remainder(self, minimal_cpu, vulkan_igpu, directml_npu):
        profile = _make_profile(minimal_cpu, vulkan_igpu, directml_npu)
        router = HeterogeneousRouter(profile)
        plan = router.build_device_plan(total_layers=32)
        assert "cpu" in plan
        assert plan["cpu"]["layers"] == -1  # remainder

    def test_build_device_plan_with_npu(self, minimal_cpu, vulkan_igpu, directml_npu):
        profile = _make_profile(minimal_cpu, vulkan_igpu, directml_npu)
        router = HeterogeneousRouter(profile)
        plan = router.build_device_plan(total_layers=32)
        assert "npu" in plan
        assert plan["npu"]["layers"] > 0

    def test_build_device_plan_with_igpu(self, minimal_cpu, vulkan_igpu):
        profile = _make_profile(minimal_cpu, vulkan_igpu)
        router = HeterogeneousRouter(profile)
        plan = router.build_device_plan(total_layers=32)
        assert "igpu" in plan
        assert plan["igpu"]["layers"] > 0

    def test_select_backend_symbolic_always_cpu(self, minimal_cpu, vulkan_igpu):
        profile = _make_profile(minimal_cpu, vulkan_igpu)
        router = HeterogeneousRouter(profile)
        decision = router.select_backend("symbolic")
        assert decision["target"] == "CPU"

    def test_select_backend_retrieval_always_cpu(self, minimal_cpu, vulkan_igpu):
        profile = _make_profile(minimal_cpu, vulkan_igpu)
        router = HeterogeneousRouter(profile)
        decision = router.select_backend("retrieval")
        assert decision["target"] == "CPU"

    def test_select_backend_embeddings_uses_igpu(self, minimal_cpu, vulkan_igpu):
        profile = _make_profile(minimal_cpu, vulkan_igpu)
        router = HeterogeneousRouter(profile)
        decision = router.select_backend("embeddings")
        assert decision["target"] == "iGPU"

    def test_select_backend_inference_has_device_plan(self, minimal_cpu, vulkan_igpu):
        profile = _make_profile(minimal_cpu, vulkan_igpu)
        router = HeterogeneousRouter(profile)
        decision = router.select_backend("inference", complexity_score=0.5)
        assert "device_plan" in decision
        assert "cpu" in decision["device_plan"]

    def test_select_backend_cloud_fallback_high_complexity(self, minimal_cpu):
        # Low RAM, very complex query → cloud fallback
        gpu = GPUProfile()
        profile = HardwareProfile(
            cpu=minimal_cpu, igpu=gpu,
            ram_total_gb=4.0, ram_available_gb=2.0,
        )
        router = HeterogeneousRouter(profile)
        decision = router.select_backend("inference", complexity_score=0.95)
        assert decision["target"] == "Cloud-API"

    def test_select_quantization_low_ram(self, minimal_cpu):
        gpu = GPUProfile()
        profile = HardwareProfile(
            cpu=minimal_cpu, igpu=gpu,
            ram_total_gb=4.0, ram_available_gb=2.0,
        )
        router = HeterogeneousRouter(profile)
        quant = router.select_quantization()
        assert quant == "ternary"

    def test_select_quantization_high_ram(self, minimal_cpu):
        gpu = GPUProfile()
        profile = HardwareProfile(
            cpu=minimal_cpu, igpu=gpu,
            ram_total_gb=32.0, ram_available_gb=24.0,
        )
        router = HeterogeneousRouter(profile)
        quant = router.select_quantization()
        assert quant == "FP16"


# ── UniversalExecutionLayer tests ─────────────────────────────────────────────

class TestUniversalExecutionLayer:
    def test_init_creates_layer(self):
        layer = UniversalExecutionLayer()
        assert layer.status == "ACTIVE"

    def test_get_fallback_chain_non_empty(self):
        layer = UniversalExecutionLayer()
        chain = layer.get_fallback_chain()
        assert len(chain) >= 1
        assert "cpu_generic" in chain

    def test_execute_payload_returns_success(self):
        layer = UniversalExecutionLayer()
        result = layer.execute_payload("test-model", {"prompt": "hello"})
        assert result["status"] == "success"
        assert "backend_used" in result

    def test_execute_payload_oom_fallback(self):
        """Forcing OOM on cuda should fall back to next backend."""
        layer = UniversalExecutionLayer()
        result = layer.execute_payload("test-model", {"force_oom": True})
        assert result["status"] == "success"
        assert result["backend_used"] != "cuda"

    def test_get_hardware_summary_structure(self):
        layer = UniversalExecutionLayer()
        summary = layer.get_hardware_summary()
        assert "cpu" in summary
        assert "igpu" in summary
        assert "npu" in summary
        assert "ram" in summary
        assert "backend_ranking" in summary

    @pytest.mark.asyncio
    async def test_generate_async_yields_tokens(self):
        """generate_async should yield at least one token."""
        layer = UniversalExecutionLayer()
        tokens = []
        async for token in layer.generate_async("Hello world", "dummy-model"):
            tokens.append(token)
            if len(tokens) >= 3:
                break
        assert len(tokens) >= 1

    def test_boot_banner_logged(self, caplog):
        """Boot banner must mention 'LEO awakened'."""
        import logging
        with caplog.at_level(logging.INFO, logger="backend.hardware.universal_execution"):
            layer = UniversalExecutionLayer()
        assert any("LEO awakened" in record.message for record in caplog.records)


# ── Benchmark smoke test ──────────────────────────────────────────────────────

class TestLayer1Benchmark:
    """Fast smoke-test to confirm detection completes in reasonable time."""

    def test_detection_fast(self):
        import time
        t0 = time.perf_counter()
        HardwareDetector.get_system_profile()
        elapsed = time.perf_counter() - t0
        # Detection should complete within 15 seconds on any platform
        assert elapsed < 15.0, f"Hardware detection too slow: {elapsed:.1f}s"

    def test_routing_fast(self):
        import time
        profile = HardwareDetector.get_system_profile()
        router = HeterogeneousRouter(profile)
        t0 = time.perf_counter()
        for _ in range(100):
            router.select_backend("inference", complexity_score=0.5)
        elapsed = time.perf_counter() - t0
        # 100 routing decisions should be microseconds
        assert elapsed < 0.5, f"Routing too slow: {elapsed:.3f}s"
