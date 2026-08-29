"""
tests/test_leo_v8_engine.py
===========================
Automated test suite for LEO v8 Breakthrough Engine:
1. Multi-tier contract classification
2. BitNet b1.58 ternary matrix quantization & multiplication-free execution
3. 3D SDF neural rasterizer execution (>30 FPS)
4. Symplectic physics orbit simulation
5. FAISS semantic bypass & exact match resolution
"""

import pytest
import numpy as np

from leo_v8_engine import LEOv8Engine, BitNetTernaryKernel, ExecutionContract


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
        assert c_bitnet.intent == "BITNET_TERNARY_COMPUTE"
        assert c_bitnet.target_tier == "TIER_2_BITNET_TERNARY"

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
