"""
tests/hyper_escape/test_universal_adapters.py
Unit test suite for Universal Adapter Framework & Provisional Contract Inference.
"""
import pytest
import numpy as np

from hyper_universal.adapters.adapter_registry import (
    AdapterRegistry,
    DenseLinearAlgebraAdapter,
    SparseLinearAlgebraAdapter,
    SpectralFFTAdapter,
    AIInferenceAdapter,
    ImageProcessingAdapter,
    CompressionAdapter,
    CryptographyAdapter,
    PhysicsSimulationAdapter,
    SortingAndAlgorithmsAdapter,
    ProvisionalContractInferenceEngine,
)
from hyper_universal.contracts.contract_engine import ExactnessRequirement


class TestUniversalAdapters:

    @pytest.fixture(autouse=True)
    def setup_registry(self):
        self.registry = AdapterRegistry()

    def test_all_9_workload_families_registered(self):
        families = self.registry.list_supported_families()
        assert len(families) == 9
        expected = [
            "DENSE_LINEAR_ALGEBRA",
            "SPARSE_LINEAR_ALGEBRA",
            "SPECTRAL_FFT",
            "AI_INFERENCE",
            "IMAGE_PROCESSING",
            "COMPRESSION",
            "CRYPTOGRAPHY",
            "PHYSICS_SIMULATION",
            "SORTING_AND_ALGORITHMS",
        ]
        for f in expected:
            assert f in families
            adapter = self.registry.get_adapter(f)
            assert adapter is not None
            decl = adapter.get_declaration()
            assert len(decl["supported_operations"]) > 0
            assert len(decl["accepted_formats"]) > 0
            assert "unsupported_constructs" in decl
            assert "output_semantics" in decl
            assert "verification_method" in decl
            assert len(decl["backend_compatibility"]) > 0
            assert "resource_requirements" in decl

    def test_dense_linear_algebra_adapter(self):
        adapter = DenseLinearAlgebraAdapter()
        contract = adapter.create_contract("gemm_test")
        assert contract.exactness == ExactnessRequirement.NUMERICALLY_EQUIVALENT

        A = np.ones((8, 8), dtype=np.float32)
        B = np.ones((8, 8), dtype=np.float32) * 2.0
        ir = adapter.build_ir("gemm_test", (A, B))
        assert len(ir.nodes) >= 3
        assert ir.nodes["matmul_out"].estimated_flops == 2 * 8 * 8 * 8

        ref_out = adapter.execute_reference((A, B))
        assert ref_out.shape == (8, 8)
        assert ref_out[0, 0] == 16.0

    def test_sparse_linear_algebra_adapter(self):
        adapter = SparseLinearAlgebraAdapter()
        contract = adapter.create_contract("spmv_test")
        assert contract.family == "SPARSE_LINEAR_ALGEBRA"

        A = np.eye(8, dtype=np.float32)
        x = np.ones(8, dtype=np.float32)
        ir = adapter.build_ir("spmv_test", (A, x))
        assert len(ir.nodes) >= 3

        ref_out = adapter.execute_reference((A, x))
        assert np.array_equal(ref_out, x)

    def test_spectral_fft_adapter(self):
        adapter = SpectralFFTAdapter()
        contract = adapter.create_contract("fft_test")
        assert contract.tolerances.min_snr_db == 60.0

        sig = np.sin(np.linspace(0, 2 * np.pi, 64))
        ir = adapter.build_ir("fft_test", sig)
        assert "fft_out" in ir.nodes

        ref_out = adapter.execute_reference(sig)
        assert len(ref_out) == 33

    def test_ai_inference_adapter(self):
        adapter = AIInferenceAdapter()
        contract = adapter.create_contract("attn_test")
        assert contract.family == "AI_INFERENCE"

        q = np.ones((4, 8), dtype=np.float32)
        k = np.ones((4, 8), dtype=np.float32)
        v = np.ones((4, 8), dtype=np.float32) * 2.0
        ir = adapter.build_ir("attn_test", (q, k, v))
        assert "attn_out" in ir.nodes

        ref_out = adapter.execute_reference((q, k, v))
        assert ref_out.shape == (4, 8)

    def test_image_processing_adapter(self):
        adapter = ImageProcessingAdapter()
        contract = adapter.create_contract("blur_test")
        assert contract.tolerances.min_ssim == 0.98

        img = np.ones((16, 16), dtype=np.float32)
        ir = adapter.build_ir("blur_test", img)
        assert "filter_out" in ir.nodes

        ref_out = adapter.execute_reference(img)
        assert ref_out.shape == (16, 16)

    def test_compression_adapter(self):
        adapter = CompressionAdapter()
        contract = adapter.create_contract("comp_test")
        assert contract.exactness == ExactnessRequirement.BITWISE_EXACT

        data = b"Testing universal compression adapter pipeline"
        ir = adapter.build_ir("comp_test", data)
        assert "compressed" in ir.nodes

        ref_out = adapter.execute_reference(data)
        assert isinstance(ref_out, bytes)

    def test_cryptography_adapter(self):
        adapter = CryptographyAdapter()
        contract = adapter.create_contract("sha256_test")
        assert contract.exactness == ExactnessRequirement.BITWISE_EXACT

        data = b"Antigravity HYPER-GODMODE cryptographic token"
        ir = adapter.build_ir("sha256_test", data)
        assert "digest_out" in ir.nodes

        ref_out = adapter.execute_reference(data)
        assert len(ref_out) == 64

    def test_physics_simulation_adapter(self):
        adapter = PhysicsSimulationAdapter()
        contract = adapter.create_contract("nbody_test")
        assert contract.family == "PHYSICS_SIMULATION"

        pos = np.random.randn(8, 3).astype(np.float32)
        vel = np.zeros((8, 3), dtype=np.float32)
        ir = adapter.build_ir("nbody_test", (pos, vel, 0.01))
        assert "step_out" in ir.nodes

        new_pos, new_vel = adapter.execute_reference((pos, vel, 0.01))
        assert new_pos.shape == (8, 3)
        assert new_vel.shape == (8, 3)

    def test_sorting_and_algorithms_adapter(self):
        adapter = SortingAndAlgorithmsAdapter()
        contract = adapter.create_contract("sort_test")
        assert contract.exactness == ExactnessRequirement.BITWISE_EXACT

        arr = np.array([5, 2, 8, 1, 9, 3], dtype=np.int32)
        ir = adapter.build_ir("sort_test", arr)
        assert "sorted" in ir.nodes

        ref_out = adapter.execute_reference(arr)
        assert np.array_equal(ref_out, [1, 2, 3, 5, 8, 9])

    def test_provisional_contract_inference_engine(self):
        # 1. Test integer sorting inference
        arr = np.array([10, 4, 1, 9], dtype=np.int32)
        contract_sort = ProvisionalContractInferenceEngine.infer_provisional_contract(
            "inferred_sort", lambda x: np.sort(x), arr
        )
        assert contract_sort.exactness == ExactnessRequirement.EXACT_INTEGER_SYMBOLIC
        assert contract_sort.tolerances.max_relative_error == 0.0

        # 2. Test floating point inference
        mat = np.ones((4, 4), dtype=np.float32)
        contract_mat = ProvisionalContractInferenceEngine.infer_provisional_contract(
            "inferred_mat", lambda x: x * 2.5, mat
        )
        assert contract_mat.exactness == ExactnessRequirement.NUMERICALLY_EQUIVALENT
        assert contract_mat.tolerances.max_relative_error == 1e-4

        # 3. Test bytes inference
        data = b"token"
        contract_bytes = ProvisionalContractInferenceEngine.infer_provisional_contract(
            "inferred_bytes", lambda x: x + b"_hash", data
        )
        assert contract_bytes.exactness == ExactnessRequirement.BITWISE_EXACT
        assert contract_bytes.tolerances.max_relative_error == 0.0

    def test_adapters_api_endpoints(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from backend.routers.hyper_escape_router import router

        test_app = FastAPI()
        test_app.include_router(router)
        client = TestClient(test_app)
        # 1. Test /adapters endpoint
        resp = client.get("/api/v1/escape_omega/adapters")
        assert resp.status_code == 200
        decls = resp.json()
        assert len(decls) == 9
        families = [d["family"] for d in decls]
        assert "DENSE_LINEAR_ALGEBRA" in families
        assert "PHYSICS_SIMULATION" in families
        assert "AI_INFERENCE" in families

        # 2. Test /contracts/infer endpoint
        resp_infer = client.post(
            "/api/v1/escape_omega/contracts/infer",
            json={
                "workload_id": "test_infer_api",
                "sample_data": [1.0, 2.0, 3.0, 4.0],
                "output_dtype": "float32",
            },
        )
        assert resp_infer.status_code == 200
        infer_json = resp_infer.json()
        assert infer_json["is_provisional"] is True
        assert infer_json["inferred_contract"]["workload_id"] == "test_infer_api"
        assert infer_json["inferred_contract"]["exactness"] == "NUMERICALLY_EQUIVALENT"

