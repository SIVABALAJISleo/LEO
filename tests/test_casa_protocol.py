"""
tests/test_casa_protocol.py
===========================
Contract-Aware Sieve Architecture (CASA) Integration Test Suite
Comprehensive Verification & Hostile Falsification Protocol.

Targets:
  - Phase 1: Arithmetic Dematerialization (T-MAC 1.58-bit LUT manifold, 0% FP32 MACs).
  - Phase 2: Spatio-Temporal Sieve (E-core spectral delta culling, >=85% reduction).
  - Phase 3: Zero-Copy Unified Memory (Intel Level Zero zeMemAllocShared, 0.0 ms latency).
  - Phase 4: Complexity Inversion (SSM O(N) sequence time & O(1) memory, SimHash LSH).
  - Entropy Trap & Hostile Falsification Protocol (Correlated low-entropy vs Maximum-entropy noise).
"""

import pytest
import os
import numpy as np
from typing import Dict, Any

from hyper.casa.tmac_lut_engine import TMacLUTEngine
from hyper.casa.spatio_temporal_sieve import SpatioTemporalSieve
from hyper.casa.zero_copy_usm import ZeroCopyUSMManager
from hyper.casa.complexity_inversion import ComplexityInverter, StateSpaceModelEngine, SimHashLSHIndex
from hyper.casa.casa_orchestrator import CASAOrchestrator
from hyper.contracts.contract_types import UniversalContract, ContractClass


class TestPhase1ArithmeticDematerialization:
    """Tests for Phase 1: T-MAC 1.58-bit Lookup Table (LUT) Manifold."""

    def test_zero_fp32_mac_utilization(self):
        dim = 128
        engine = TMacLUTEngine(group_size=2, hidden_dim=dim)
        rng = np.random.RandomState(42)
        
        # 1.58-bit ternary weights in {-1, 0, +1}
        W_ternary = rng.choice([-1, 0, 1], size=(dim, dim)).astype(np.int8)
        x = rng.randn(dim).astype(np.float32)
        
        y_lut, profile = engine.forward(x, W_ternary)
        
        # Acceptance Criteria: 0% FP32 MAC utilization
        assert profile["fp32_mac_utilization_pct"] == 0.0
        assert profile["fp32_mac_count"] == 0
        assert profile["lut_reads"] > 0
        assert profile["int_additions"] > 0
        assert profile["l3_cache_manifold"] is True

    def test_mathematical_exactness(self):
        dim = 64
        engine = TMacLUTEngine(group_size=2, hidden_dim=dim)
        rng = np.random.RandomState(123)
        
        W_ternary = rng.choice([-1, 0, 1], size=(dim, dim)).astype(np.int8)
        x = rng.randn(dim).astype(np.float32)
        
        y_lut, _ = engine.forward(x, W_ternary)
        y_exact = W_ternary.astype(np.float32) @ x
        
        # Exact mathematical parity within float32 numerical precision
        max_diff = float(np.max(np.abs(y_lut - y_exact)))
        assert max_diff < 1e-4, f"T-MAC numerical drift {max_diff} exceeded tolerance!"


class TestPhase2SpatioTemporalSieve:
    """Tests for Phase 2: Spatio-Temporal Sieve (The Delta Algorithm)."""

    def test_severed_graph_on_redundant_state(self):
        dim = 64
        sieve = SpatioTemporalSieve(tolerance_tau=0.05, input_dim=dim, output_dim=dim)
        
        x0 = np.ones(dim, dtype=np.float32) * 0.5
        def forward_fn(x):
            return x * 2.0
            
        # Step 0: Initial full graph execution
        y0, telem0 = sieve.execute_sieve(x0, forward_fn)
        assert telem0["action"] == "FULL_GRAPH_EXECUTION"
        assert telem0["graph_severed"] is False
        
        # Step 1: Input with tiny delta < tau (redundant state)
        x1 = x0 + np.ones(dim, dtype=np.float32) * 0.001
        y1, telem1 = sieve.execute_sieve(x1, forward_fn)
        
        # Acceptance Criteria: Execution graph severed, returns cached state
        assert telem1["action"] == "SEVERED_GRAPH_BYPASS"
        assert telem1["graph_severed"] is True
        assert telem1["compute_saved_pct"] == 100.0
        assert np.allclose(y1, y0)

    def test_correlated_sequential_data_cull_rate(self):
        dim = 64
        sieve = SpatioTemporalSieve(tolerance_tau=0.08, jacobian_tau=0.25, input_dim=dim, output_dim=dim)
        
        def forward_fn(x):
            return np.tanh(x @ np.eye(dim))
            
        frames = 80
        t = np.linspace(0, 2 * np.pi, frames)
        for i in range(frames):
            # Smoothly correlated trajectory
            x_t = np.sin(t[i] * 0.04) * np.ones(dim, dtype=np.float32) + np.random.normal(0, 0.004, dim).astype(np.float32)
            sieve.execute_sieve(x_t, forward_fn)
            
        stats = sieve.get_cull_efficiency()
        # Acceptance Criteria: >=85% compute drop on correlated data
        assert stats["total_bypassed_percentage"] >= 85.0
        assert stats["target_85_90_pct_achieved"] is True


class TestPhase3ZeroCopyUnifiedMemory:
    """Tests for Phase 3: Zero-Copy Unified Memory (The PCIe Bypass)."""

    def test_zero_copy_pointer_sharing(self):
        mgr = ZeroCopyUSMManager()
        profile = mgr.profile_transfer_latency(shape=(256, 256))
        
        # Acceptance Criteria: Memory transfer latency must profile at 0.0 ms
        assert profile["host_to_device_latency_ms"] == 0.0
        assert profile["device_to_host_latency_ms"] == 0.0
        assert profile["total_pcie_transfer_latency_ms"] == 0.0
        assert profile["pcie_serialization_eliminated"] is True
        assert profile["unified_ram_shared"] is True

    def test_usm_buffer_integrity(self):
        mgr = ZeroCopyUSMManager()
        buf, arr = mgr.create_shared_buffer((128,), dtype=np.float32)
        
        # Write test pattern from CPU
        arr[:] = np.arange(128, dtype=np.float32)
        
        # Verify buffer pointer matches array pointer
        assert arr.__array_interface__["data"][0] == buf.raw_ptr
        assert arr[0] == 0.0
        assert arr[127] == 127.0
        buf.free()


class TestPhase4ComplexityInversion:
    """Tests for Phase 4: Complexity Inversion (SSM & SimHash)."""

    def test_ssm_o1_memory_scaling(self):
        ci = ComplexityInverter(d_model=64, d_state=16)
        lengths = [128, 512, 1024, 2048]
        res = ci.profile_memory_scaling(lengths)
        
        # Acceptance Criteria: Flat constant O(1) state memory regardless of context length
        assert res["quadratic_attention_eliminated"] is True
        memories = [r["state_memory_bytes"] for r in res["scaling_results"]]
        assert len(set(memories)) == 1, "Operational memory must remain strictly O(1) flat!"
        assert memories[0] == 64 * 16 * 4  # 4096 bytes

    def test_simhash_lsh_retrieval(self):
        dim = 64
        index = SimHashLSHIndex(dim=dim, num_bits=64)
        rng = np.random.RandomState(42)
        
        base_vec = rng.randn(dim).astype(np.float32)
        index.add(item_id=101, vec=base_vec)
        
        # Add orthogonal noise vectors
        for i in range(20):
            noise_vec = rng.randn(dim).astype(np.float32)
            index.add(item_id=i, vec=noise_vec)
            
        # Query with slightly perturbed version of base_vec
        query = base_vec + rng.normal(0, 0.01, dim).astype(np.float32)
        matches = index.query_nearest(query, max_hamming_dist=4)
        
        assert len(matches) > 0
        best_id, best_dist = matches[0]
        assert best_id == 101, f"Expected item 101, got {best_id}"
        assert best_dist < 0.2


class TestHostileFalsificationEntropyTrap:
    """Adversarial Verification & Hostile Falsification Protocol."""

    def test_low_entropy_correlated_pass(self):
        orch = CASAOrchestrator(hidden_dim=64, group_size=2, tolerance_tau=0.05)
        res = orch.run_falsification_stream(stream_type="correlated", num_steps=50)
        
        # Acceptance Criteria:
        # Sieve activates (>85%), Power < 20W, 100% Contract Parity at < 30ms latency
        assert res["cull_ratio"] >= 0.85, f"Cull ratio {res['cull_ratio']} below 85%"
        assert res["avg_power_watts"] < 20.0, f"Power {res['avg_power_watts']}W exceeded 20W limit!"
        assert res["avg_latency_ms"] < 30.0, f"Latency {res['avg_latency_ms']}ms exceeded 30ms!"
        assert res["fp32_mac_utilization_pct"] == 0.0

    def test_maximum_entropy_noise_trap(self):
        orch = CASAOrchestrator(hidden_dim=64, group_size=2, tolerance_tau=0.05)
        res = orch.run_falsification_stream(stream_type="high_entropy_noise", num_steps=40)
        
        # Acceptance Criteria:
        # Sieve SAFELY DEACTIVATES (cull ratio = 0.0)
        # Routes 100% to dense fallback without crashing or hallucinating static cached states
        assert res["dense_count"] == 40, f"Expected 40 dense fallback runs, got {res['dense_count']}"
        assert res["cull_ratio"] == 0.0, f"Expected 0.0 cull ratio on pure noise, got {res['cull_ratio']}"
        assert res["fp32_mac_utilization_pct"] == 0.0
        assert res["avg_latency_ms"] < 30.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
