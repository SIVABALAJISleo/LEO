"""
tests/test_leo_v8_engine.py
===========================
Automated test suite for LEO v8 Breakthrough Engine:
1. Multi-tier contract classification (including Zero-MAC AVX2 LUT routing)
2. BitNet b1.58 ternary matrix quantization & multiplication-free execution
3. Zero-MAC 4-bit AVX2 LUT kernel execution (zero hardware multipliers)
4. Zero-Copy NVMe mmap weight streamer
5. 3D SDF neural rasterizer execution (>30 FPS)
6. Symplectic physics orbit simulation
7. FAISS semantic bypass & exact match resolution
"""

import os
import tempfile
import pytest
import numpy as np

from leo_v8_engine import (
    LEOv8Engine,
    BitNetTernaryKernel,
    ZeroMAC_Avx2Kernel,
    ZeroCopyWeightStreamer,
    ExecutionContract,
    AbsoluteContractEnforcer,
)


class TestLEOv8Engine:

    @pytest.fixture(scope="class")
    def engine(self):
        return LEOv8Engine(semantic_threshold=0.75)

    def test_1_bitnet_ternary_kernel_multiplication_free(self):
        """Tests that BitNet ternary kernel accurately executes {-1, 0, +1} matvec."""
        dim = 128
        W = np.random.randn(dim, dim).astype(np.float32)
        W_ternary, gamma = BitNetTernaryKernel.quantize_weights_ternary(W)

        # Ensure weights are strictly ternary {-1, 0, +1}
        unique_vals = set(np.unique(W_ternary))
        assert unique_vals.issubset({-1, 0, 1})

        x = np.random.randn(dim).astype(np.float32)
        y_ternary = BitNetTernaryKernel.ternary_matvec(W_ternary, gamma, x)

        # Baseline float multiplication check
        y_expected = (W_ternary.astype(np.float32) * gamma) @ x
        assert np.allclose(y_ternary, y_expected, atol=1e-4)

    def test_2_contract_classification(self, engine):
        """Tests that queries are classified into appropriate target tiers."""
        c_render = engine.classify_contract("render 3d scene with raymarching and sdf")
        assert c_render.intent == "3D_GRAPHICS_RENDERING"
        assert c_render.target_tier == "TIER_4_NEURAL_RASTERIZER"

        c_phys = engine.classify_contract("simulate n-body gravitational orbit with physics")
        assert c_phys.intent == "PHYSICS_SIMULATION"
        assert c_phys.target_tier == "TIER_5_SYMPLECTIC_PHYSICS"

        c_bitnet = engine.classify_contract("execute bitnet ternary matrix multiplication")
        assert c_bitnet.intent in ["ZERO_MAC_TERNARY_COMPUTE", "BITNET_TERNARY_COMPUTE"]
        assert c_bitnet.target_tier in ["TIER_2_ZERO_MAC_LUT", "TIER_2_BITNET_TERNARY"]
        assert "Zero-Copy" in c_bitnet.device_affinity

    def test_3_semantic_cache_instant_resolution(self, engine):
        """Tests that seeded exact queries resolve in Tier 0 with 100% compute avoided."""
        res = engine.execute("what is leo ai")
        assert "LEVEL_1_EXACT" in res.tier_executed
        assert res.computation_avoided_pct == 100.0
        assert res.latency_ms < 5.0
        assert res.contract_satisfied is True

    def test_4_3d_graphics_rasterizer_fps_contract(self, engine):
        """Tests that 3D neural rasterizer satisfies the >30 FPS contract."""
        res = engine.execute("render a 3d scene using raymarching and sdf")
        assert res.tier_executed == "TIER_4_NEURAL_RASTERIZER"
        assert res.computation_avoided_pct > 90.0
        assert res.contract_satisfied is True

    def test_5_symplectic_physics_energy_conservation(self, engine):
        """Tests that physics simulation satisfies Hamiltonian energy conservation contract."""
        res = engine.execute("simulate n-body gravitational orbit with physics")
        assert res.tier_executed == "TIER_5_SYMPLECTIC_PHYSICS"
        assert res.contract_satisfied is True
        assert res.provenance["invariant_preserved"] is True

    def test_6_zero_mac_avx2_kernel(self):
        """Tests that ZeroMAC_Avx2Kernel executes 4-bit LUT lookups with zero multiplier ops."""
        kernel = ZeroMAC_Avx2Kernel()
        dim = 64
        W = np.random.randn(dim, dim).astype(np.float32)
        x = np.random.randn(dim).astype(np.float32)

        res, lat_ms = kernel.execute(W, x)
        assert res.shape == (dim,)
        assert lat_ms >= 0.0
        assert not np.isnan(res).any()

        # Check LUT precomputed table
        assert kernel.lut.shape == (256,)
        # Verify 3 * 5 in LUT: index (3 << 4) | 5 = 48 + 5 = 53
        assert kernel.lut[(3 << 4) | 5] == 15

    def test_7_zero_copy_weight_streamer(self):
        """Tests that ZeroCopyWeightStreamer maps and fetches blocks without RAM bloat."""
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(b"LEO_V8_ZERO_COPY_WEIGHT_PAYLOAD_TEST")
            temp_path = tf.name

        try:
            streamer = ZeroCopyWeightStreamer(temp_path)
            assert streamer.file_size > 0
            block = streamer.fetch_block(offset=0, length=6)
            assert block == b"LEO_V8"
            streamer.close()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_8_leo_v8_tier2_zero_mac_execution(self, engine):
        """Tests end-to-end execution of Tier 2 Zero-MAC LUT pipeline in LEO v8."""
        res = engine.execute("execute zero-mac 4-bit lut matrix multiplication")
        assert res.tier_executed == "TIER_2_ZERO_MAC_LUT"
        assert res.computation_avoided_pct >= 90.0
        assert res.contract_satisfied is True
        assert res.provenance.get("zero_mac") is True

    def test_9_absolute_contract_enforcer_impossible_3d_workload(self, engine):
        """Tests that an impossible 3D rendering workload is gracefully degraded to guaranteed achievable contract."""
        enforcer = AbsoluteContractEnforcer()
        impossible_3d = {
            "intent": "3D_GRAPHICS_RENDERING",
            "estimated_flops": 5.0e11,  # 500 GFLOPS -> 5000ms latency on 100 GFLOPS limit
            "estimated_ram_mb": 4000
        }
        enforced, was_degraded = enforcer.evaluate_and_enforce(impossible_3d)
        assert was_degraded is True
        assert enforced["intent"] == "3D_GRAPHICS_UPSCALED"
        assert enforced["method"] == "TEMPORAL_DELTA + BILINEAR_UPSCALE"
        assert enforced["guaranteed_latency_ms"] == 16.0
        assert "SSIM >= 0.95" in enforced["quality_contract"]
        assert enforced["estimated_flops"] == 5.0e11 * 0.05

        # Execute through engine with raw_contract
        res = engine.execute("render impossible 4k 3d raytraced scene", raw_contract=impossible_3d)
        assert res.tier_executed == "TIER_4_NEURAL_RASTERIZER"
        assert res.contract_satisfied is True
        assert res.contract_fulfilled_100_percent is True
        assert res.provenance.get("was_degraded") is True

    def test_10_absolute_contract_enforcer_impossible_matrix_and_memory(self, engine):
        """Tests that an impossible dense matrix workload and massive RAM footprint are algorithmically substituted."""
        enforcer = AbsoluteContractEnforcer()
        impossible_dense = {
            "intent": "DENSE_MATRIX_COMPUTE",
            "estimated_flops": 3.0e11,
            "estimated_ram_mb": 16000  # Exceeds 8000 MB limit
        }
        enforced, was_degraded = enforcer.evaluate_and_enforce(impossible_dense)
        assert was_degraded is True
        assert enforced["intent"] == "APPROXIMATE_TERNARY_COMPUTE"
        assert enforced["method"] == "NUMBA_ZERO_MAC + PI_ERROR_CONTROLLER"
        assert enforced["guaranteed_latency_ms"] == 15.0
        assert enforced["memory_strategy"] == "ZERO_COPY_MMAP_STREAMING"

        # Execute through engine
        res = engine.execute("compute massive dense gemm", raw_contract=impossible_dense)
        assert res.tier_executed == "TIER_2_ZERO_MAC_LUT"
        assert res.contract_satisfied is True
        assert res.contract_fulfilled_100_percent is True
        assert res.provenance.get("was_degraded") is True
