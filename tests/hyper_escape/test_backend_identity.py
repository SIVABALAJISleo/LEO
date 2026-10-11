"""
tests/hyper_escape/test_backend_identity.py
Validates Genuine Backend Capability Discovery (Feature F / Section 8.1).
Ensures zero fabricated GPU devices, honest reporting of available hardware,
and verification that CPU AVX2 is always recognized as reliable fallback.
"""
import pytest
from hyper_universal.backends.registry import BackendCapabilityRegistry


def test_backend_registry_discovery():
    registry = BackendCapabilityRegistry()
    backends = registry.get_available_backends()

    # CPU AVX2 must ALWAYS be available on Intel Core i5
    backend_names = [b.backend_name for b in backends]
    assert "CPU_AVX2" in backend_names

    cpu_backend = registry.get_backend("CPU_AVX2")
    assert cpu_backend is not None
    assert cpu_backend.is_available is True
    assert "float32" in cpu_backend.supported_dtypes
    assert cpu_backend.device_type == "CPU"


def test_no_fabricated_cuda_devices():
    registry = BackendCapabilityRegistry()
    cuda_backend = registry.get_backend("NVIDIA_CUDA")
    # On Lenovo IdeaPad Slim 3 (i5-12450H/i5-13420H), there is NO dedicated NVIDIA GPU!
    assert cuda_backend is None or cuda_backend.is_available is False


def test_backend_device_details():
    registry = BackendCapabilityRegistry()
    for backend in registry.get_available_backends():
        # Every available backend must have valid attributes
        assert backend.backend_name is not None
        assert backend.device_type in ["CPU", "GPU", "HYBRID"]
        assert backend.max_memory_mb > 0
        assert len(backend.supported_dtypes) > 0
