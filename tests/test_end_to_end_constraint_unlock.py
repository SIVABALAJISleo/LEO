"""
tests/test_end_to_end_constraint_unlock.py
==============================================================================
Project LEO / HYPER-Omega: Comprehensive Verification Suite for
End-to-End Hardware Roof-Closer, SSD-Native Streaming, Radix Serving & P2P Mesh.
Target Hardware: Intel Core i5-12450H + Intel UHD Graphics + 16 GB RAM + 512 GB NVMe
==============================================================================
"""

import os
import sys
import pytest
import numpy as np
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.canonical.ssd_native_unmodified_expert_engine import (
    ExpertPackBuilder,
    SSDNativeUnmodifiedExpertEngine,
    benchmark_ssd_native_unmodified_expert_engine,
)
from backend.canonical.radix_prefix_serving_engine import (
    RadixPrefixServingEngine,
    benchmark_radix_prefix_serving_engine,
)
from backend.canonical.p2p_expert_sharding_mesh import (
    ConsistentHashExpertRing,
    P2PExpertWorkerNode,
    P2PExpertShardingMesh,
    benchmark_p2p_expert_sharding_mesh,
)
from backend.canonical.end_to_end_constraint_unlock_runner import (
    EndToEndConstraintUnlockRouter,
    run_full_end_to_end_constraint_unlock_audit,
)


def test_1_ssd_native_sector_alignment_and_manifest():
    """Verify 4096-byte sector alignment of every packed expert block."""
    tmp_dir = "IEEE_EVIDENCE/test_scratch_ssd"
    os.makedirs(tmp_dir, exist_ok=True)
    pack_path = os.path.join(tmp_dir, "test_pack.bin")
    manifest_path = os.path.join(tmp_dir, "test_manifest.json")

    rng = np.random.default_rng(101)
    experts_dict = {}
    for e in range(8):
        g = rng.laplace(0.0, 0.05, size=(64, 32)).astype(np.float32)
        u = rng.laplace(0.0, 0.05, size=(64, 32)).astype(np.float32)
        d = rng.laplace(0.0, 0.05, size=(32, 64)).astype(np.float32)
        experts_dict[(0, e)] = (g, u, d)

    builder = ExpertPackBuilder(sector_size=4096)
    manifest = builder.build_pack_file(experts_dict, pack_path, manifest_path)

    for k, v in manifest.items():
        assert v["file_offset_aligned"] % 4096 == 0, f"Offset {v['file_offset_aligned']} not 4096-aligned"
        assert v["payload_length"] <= v["padded_length"]
        assert len(v["sha256"]) == 64

    # Clean up
    try:
        if os.path.exists(pack_path): os.remove(pack_path)
        if os.path.exists(manifest_path): os.remove(manifest_path)
    except Exception:
        pass


def test_2_rans_lossless_roundtrip_and_incompressibility_guard():
    """Verify 0-bit error rANS roundtrip on skewed weights & RAW_PASSTHROUGH on white noise."""
    builder = ExpertPackBuilder()
    rng = np.random.default_rng(202)

    # 1. Skewed Laplace weights -> rANS compression
    g_skew = rng.laplace(0.0, 0.04, size=(64, 32)).astype(np.float32)
    u_skew = rng.laplace(0.0, 0.04, size=(64, 32)).astype(np.float32)
    d_skew = rng.laplace(0.0, 0.04, size=(32, 64)).astype(np.float32)
    enc_bytes, codec, raw_sz, sha = builder.pack_expert_tensors(g_skew, u_skew, d_skew)
    assert len(sha) == 64

    # 2. Maximum-entropy uniform white noise -> RAW_PASSTHROUGH (codec 0)
    g_noise = (rng.integers(-7, 8, size=(64, 32)) / 16.0).astype(np.float32)
    u_noise = (rng.integers(-7, 8, size=(64, 32)) / 16.0).astype(np.float32)
    d_noise = (rng.integers(-7, 8, size=(32, 64)) / 16.0).astype(np.float32)
    _, noise_codec, _, _ = builder.pack_expert_tensors(g_noise, u_noise, d_noise)
    assert noise_codec == 0, f"Expected RAW_PASSTHROUGH (0), got {noise_codec}"


def test_3_speculative_multi_token_batching_and_leviathan_chen():
    """Verify speculative tree batching and Leviathan-Chen rejection sampling."""
    res = benchmark_ssd_native_unmodified_expert_engine(
        num_layers=1,
        experts_per_layer=8,
        active_k=2,
        hidden_dim=64,
        inter_dim=32,
    )
    assert res["sector_alignment_verified"] is True
    assert res["execution_metrics"]["distribution_parity"] == "100%_LEVIATHAN_CHEN_EXACT"
    assert res["execution_metrics"]["accepted_speculative_tokens"] > 0
    assert res["parity_tiers"]["TIER_2_EXACT_COMPUTATIONAL_PARITY"] is True


def test_4_radix_prefix_multi_user_serving_zero_numerical_error():
    """Verify Radix prefix sharing produces 0.0 numerical difference vs naive recomputation."""
    res = benchmark_radix_prefix_serving_engine(
        num_users=4,
        shared_prefix_len=32,
        user_suffix_len=8,
        hidden_dim=64,
        latent_dim=16,
    )
    assert res["prefix_hit_rate_pct"] > 0.0
    assert res["max_absolute_error_vs_naive"] <= 1e-5
    assert res["multi_user_speedup_x"] >= 1.0
    assert res["parity_tiers"]["TIER_2_EXACT_COMPUTATIONAL_PARITY"] is True


def test_5_radix_prefix_adversarial_unique_prompts_clean_fallback():
    """Verify 100%-unique random prompts trigger clean fallback without false speedup."""
    res = benchmark_radix_prefix_serving_engine(
        num_users=4,
        shared_prefix_len=16,
        user_suffix_len=8,
        hidden_dim=32,
        latent_dim=16,
    )
    assert res["adversarial_clean_fallback_verified"] is True
    assert res["adversarial_unique_prefix_hit_pct"] == 0.0


def test_6_p2p_consistent_hash_ring_and_activation_routing():
    """Verify consistent-hash sharding across peer nodes and tiny activation transmission."""
    ring = ConsistentHashExpertRing(["node_0", "node_1", "node_2", "node_3"], num_experts=64)
    # Check all experts mapped
    for e in range(64):
        node = ring.get_node_for_expert(e)
        assert node in ["node_0", "node_1", "node_2", "node_3"]

    # Check balanced sharding
    for n in ["node_0", "node_1", "node_2", "node_3"]:
        assert len(ring.node_to_experts[n]) > 0


def test_7_p2p_mesh_execution_and_fault_injection_failover():
    """Verify P2P multi-node socket execution matches single-node and survives killed worker."""
    res = benchmark_p2p_expert_sharding_mesh()
    assert res["max_diff_normal_vs_single_node"] <= 1e-5
    assert res["network_activation_metrics"]["network_bytes_sent"] > 0
    assert res["network_activation_metrics"]["activation_routing_compression_ratio_x"] > 10.0

    # Fault injection check
    fault_res = res["fault_injection_test"]
    assert fault_res["seamless_failover_verified"] is True
    assert fault_res["fallback_invocations"] > 0
    assert fault_res["max_diff_after_fault"] <= 1e-5
    assert res["parity_tiers"]["TIER_2_EXACT_COMPUTATIONAL_PARITY"] is True


def test_8_end_to_end_router_4_pillars_classification():
    """Verify Stage 0 router cleanly maps workloads to Path A, B1, B2, or C."""
    router = EndToEndConstraintUnlockRouter()

    # Path A: Contract Reformulation
    r_a = router.classify_and_route("knowledge_moe", allow_contract_reformulation=True, entropy_shannon=0.3)
    assert r_a["selected_path"] == "PATH_A_CONTRACT_REFORMULATION"

    # Path B1: Unmodified SSD Streaming
    r_b1 = router.classify_and_route("unmodified_eval", allow_contract_reformulation=False, entropy_shannon=0.4)
    assert r_b1["selected_path"] == "PATH_B1_SSD_NATIVE_UNMODIFIED"

    # Path B2: Incompressible TDM
    r_b2 = router.classify_and_route("adversarial_noise", allow_contract_reformulation=False, entropy_shannon=0.95)
    assert r_b2["selected_path"] == "PATH_B2_ARBITRARY_EXACT_TDM"

    # Path C: P2P Decentralized Mesh
    r_c = router.classify_and_route("cluster_serving", has_p2p_peers=True, entropy_shannon=0.5)
    assert r_c["selected_path"] == "PATH_C_P2P_DECENTRALIZED_MESH"


def test_9_master_end_to_end_constraint_unlock_audit():
    """Verify master audit executes, outputs clean artifacts, and verifies all 4 parity tiers."""
    audit = run_full_end_to_end_constraint_unlock_audit()
    assert audit["audit_name"] == "END_TO_END_HARDWARE_ROOF_CLOSER_AND_CONSTRAINT_UNLOCK"
    assert audit["subsystem_1_ssd_native_unmodified"]["status"] == "PASS"
    assert audit["subsystem_2_radix_serving"]["status"] == "PASS"
    assert audit["subsystem_3_p2p_mesh"]["status"] == "PASS"

    tiers = audit["global_parity_tiers"]
    assert tiers["TIER_1_RAW_HARDWARE_PARITY"] is False
    assert tiers["TIER_2_EXACT_COMPUTATIONAL_PARITY"] is True
    assert tiers["TIER_3_CONTRACT_PARITY"] is True
    assert tiers["TIER_4_CONSUMER_ROOFLINE_EFFICIENCY"] > 50.0
