"""
tests/hyper_mirror/test_capability_mirror.py
Comprehensive test suite for Universal GPU Capability Mirror and Substitution Search.
"""
import pytest
import numpy as np

from hyper_universal.capability_mirror.registry import (
    CapabilityRecord,
    CapabilityCertificationStatus,
    EquivalenceDimension,
    UniversalCapabilityRegistry,
)
from hyper_universal.capability_mirror.search import (
    CapabilitySubstitutionSearch,
    SubstitutionCandidate,
)
from hyper_universal.capability_mirror.matrix import (
    CapabilityMatrixGenerator,
)


class TestUniversalCapabilityMirror:

    @pytest.fixture(autouse=True)
    def setup_registry(self):
        self.registry = UniversalCapabilityRegistry()
        self.search = CapabilitySubstitutionSearch(registry=self.registry)

    def test_all_21_capabilities_registered(self):
        """Verifies all 21 reference GPU capabilities exist in the registry."""
        caps = self.registry.list_capabilities()
        assert len(caps) >= 21, f"Expected at least 21 capabilities, found {len(caps)}"

        expected_ids = [
            "CAP_GENERAL_ARITHMETIC",
            "CAP_INTEGER_OPERATIONS",
            "CAP_FLOATING_POINT_TRANSCENDENTAL",
            "CAP_MATRIX_TENSOR_GEMM",
            "CAP_PARALLEL_REDUCTIONS",
            "CAP_ATOMIC_OPERATIONS",
            "CAP_MEMORY_ALLOCATION",
            "CAP_DATA_MOVEMENT",
            "CAP_TEXTURE_SAMPLING",
            "CAP_RASTERIZATION",
            "CAP_SHADER_EXECUTION",
            "CAP_RAY_INTERSECTION",
            "CAP_COORDINATE_TRANSFORMS",
            "CAP_VIDEO_PROCESSING",
            "CAP_ML_INFERENCE",
            "CAP_QUANTIZED_COMPUTATION",
            "CAP_COMPRESSION_DECOMPRESSION",
            "CAP_SYNCHRONIZATION",
            "CAP_ASYNC_EXECUTION",
            "CAP_SPECIALIZED_TENSOR_ATTENTION",
            "CAP_GRAPHICS_COMPUTE_API",
        ]
        for cap_id in expected_ids:
            rec = self.registry.get(cap_id)
            assert rec is not None, f"Missing capability: {cap_id}"
            assert rec.hardware_function
            assert rec.observable_behavior
            assert rec.reference_implementation is not None
            assert rec.cpu_alternative is not None
            assert rec.expected_computational_complexity

    def test_physical_hardware_equivalence_strictly_false(self):
        """Verifies physical hardware equivalence is never falsely claimed as True."""
        candidates = self.search.search_substitution("CAP_MATRIX_TENSOR_GEMM")
        assert len(candidates) > 0
        for c in candidates:
            # Physical dedicated GPU is absent on the target machine
            assert c.equivalence_ratings[EquivalenceDimension.PHYSICAL_HARDWARE.value] is False
            assert c.requires_physical_hardware is False

    def test_dimensions_not_merged_into_single_score(self):
        """Verifies 6 dimensions are distinct and separate."""
        candidates = self.search.search_substitution("CAP_GENERAL_ARITHMETIC")
        cand = candidates[0]
        ratings = cand.equivalence_ratings
        assert len(ratings) == 6
        assert EquivalenceDimension.PHYSICAL_HARDWARE.value in ratings
        assert EquivalenceDimension.INSTRUCTION_OR_API_EMULATION.value in ratings
        assert EquivalenceDimension.FUNCTIONAL_EQUIVALENCE.value in ratings
        assert EquivalenceDimension.MATHEMATICAL_EQUIVALENCE.value in ratings
        assert EquivalenceDimension.APPLICATION_CONTRACT.value in ratings
        assert EquivalenceDimension.PERFORMANCE_EQUIVALENCE.value in ratings

    def test_gemm_substitution_verification(self):
        """Verifies matrix multiplication reference vs candidate verification."""
        a = np.random.randn(32, 32).astype(np.float32)
        b = np.random.randn(32, 32).astype(np.float32)
        candidates = self.search.search_substitution("CAP_MATRIX_TENSOR_GEMM", sample_args=(a, b))
        assert len(candidates) >= 1
        cpu_cand = candidates[0]
        assert cpu_cand.is_correctness_verified is True
        assert cpu_cand.verification_error_relative <= 1e-4

    def test_transcendental_substitution(self):
        """Verifies floating-point transcendental functions substitution."""
        x = np.linspace(-1.0, 1.0, 256, dtype=np.float32)
        candidates = self.search.search_substitution("CAP_FLOATING_POINT_TRANSCENDENTAL", sample_args=(x,))
        assert len(candidates) >= 1
        for c in candidates:
            assert c.is_correctness_verified is True

    def test_quantized_computation_substitution(self):
        """Verifies INT8 quantization substitution."""
        x = np.random.randn(64, 64).astype(np.float32)
        candidates = self.search.search_substitution("CAP_QUANTIZED_COMPUTATION", sample_args=(x,))
        assert len(candidates) >= 1
        q_cand = candidates[0]
        assert q_cand.is_correctness_verified is True
        assert q_cand.certification_status in [
            CapabilityCertificationStatus.EXACT_VERIFIED,
            CapabilityCertificationStatus.CONTRACT_VERIFIED,
            CapabilityCertificationStatus.APPROXIMATE_VERIFIED,
        ]

    def test_compression_decompression_substitution(self):
        """Verifies lossless compression mirror."""
        data = b"HYPER-GODMODE UNIVERSAL MIRROR TEST SEQUENCE"
        candidates = self.search.search_substitution("CAP_COMPRESSION_DECOMPRESSION", sample_args=(data,))
        assert len(candidates) >= 1
        c = candidates[0]
        assert c.is_correctness_verified is True

    def test_capability_matrix_generation(self):
        """Verifies capability matrix report generation across all 21 capabilities."""
        gen = CapabilityMatrixGenerator()
        report = gen.evaluate_all()
        assert report["total_capabilities_evaluated"] >= 21
        assert report["total_candidate_pathways"] >= 21
        assert report["verified_substitutions_count"] >= 21

        md = gen.generate_markdown_report()
        assert "# UNIVERSAL GPU CAPABILITY MIRROR MATRIX" in md
        assert "CAP_GENERAL_ARITHMETIC" in md
        assert "CAP_SPECIALIZED_TENSOR_ATTENTION" in md

    def test_capability_mirror_api_endpoints(self):
        """Verifies FastAPI endpoints for capabilities and capability matrix."""
        from fastapi.testclient import TestClient
        from backend.main import app

        client = TestClient(app)
        # 1. List capabilities
        resp = client.get("/api/v1/escape_omega/capabilities")
        assert resp.status_code == 200
        caps = resp.json()
        assert len(caps) >= 21
        cap_ids = [c["capability_id"] for c in caps]
        assert "CAP_GENERAL_ARITHMETIC" in cap_ids
        assert "CAP_MATRIX_TENSOR_GEMM" in cap_ids

        # 2. Get specific capability
        resp_detail = client.get("/api/v1/escape_omega/capabilities/CAP_MATRIX_TENSOR_GEMM")
        assert resp_detail.status_code == 200
        detail = resp_detail.json()
        assert detail["capability"]["capability_id"] == "CAP_MATRIX_TENSOR_GEMM"
        assert len(detail["available_substitutions"]) >= 1

        # 3. 404 on nonexistent capability
        resp_404 = client.get("/api/v1/escape_omega/capabilities/NON_EXISTENT_CAPABILITY_XYZ")
        assert resp_404.status_code == 404

