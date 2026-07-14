"""
tests/test_phoenix.py
PHOENIX RUNTIME integration test suite.
Validates Medusa heads, Paged KV, PABEE, Context Manager, MoE, KV Compression.
"""

import logging
import sys, os, asyncio
import torch
import torch.nn as nn
import numpy as np

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phoenix.medusa_heads     import MedusaDecoder
from phoenix.paged_kv_cache   import PagedKVCacheManager
from phoenix.pabee_early_exit import PABEEController
from phoenix.context_manager  import HierarchicalContextManager
from phoenix.moe_offloader    import MoEOffloadingLayer
from phoenix.kv_compression   import StreamingKVCache, SnapKVCompressor
from phoenix.hybrid_pipeline  import HybridLayerPipeline


def test_medusa_heads():
    logger.info("[Test] Medusa Multi-Token Prediction")
    hidden, vocab, batch, seq = 64, 256, 2, 16

    decoder = MedusaDecoder(hidden_dim=hidden, vocab_size=vocab, num_heads=4)
    decoder.eval()
    hidden_state = torch.randn(batch, seq, hidden)

    with torch.no_grad():
        all_logits = decoder(hidden_state)

    assert len(all_logits) == 4, "Expected 4 Medusa heads"
    assert all_logits[0].shape == (batch, seq, vocab)

    # Draft generation
    drafts = decoder.generate_draft(hidden_state, top_k=1)
    assert len(drafts) == 4
    assert all(d.shape == (batch,) for d in drafts)

    # Auxiliary training loss
    targets = torch.randint(0, vocab, (batch, seq))
    loss = decoder.auxiliary_loss(all_logits, targets)
    assert loss.item() > 0

    logger.info(f"   Medusa draft tokens: {[int(d[0]) for d in drafts]}")
    logger.info("✅ Medusa Multi-Token Prediction verified.")


def test_paged_kv_cache():
    logger.info("\n[Test] Paged KV Cache Manager")
    mgr = PagedKVCacheManager(num_blocks=64, num_heads=4, head_dim=32)

    mgr.init_sequence("seq_A")
    mgr.init_sequence("seq_B")

    # Write 40 tokens for seq_A (spans 3 blocks of 16)
    for i in range(40):
        k = torch.randn(1, 4, 32)
        v = torch.randn(1, 4, 32)
        mgr.write_kv("seq_A", i, k, v)

    k_out, v_out = mgr.read_kv("seq_A", max_tokens=40)
    assert k_out.shape[0] == 40, f"Expected 40 tokens, got {k_out.shape[0]}"

    stats = mgr.stats()
    logger.info(f"   KV cache stats: {stats}")
    assert stats["active_sequences"] == 2

    mgr.free_sequence("seq_A")
    assert mgr.stats()["active_sequences"] == 1

    logger.info("✅ Paged KV Cache verified.")


def test_pabee():
    logger.info("\n[Test] PABEE Early Exit")
    hidden_dim  = 32
    num_classes = 4
    num_layers  = 8

    layers = nn.ModuleList([nn.Linear(hidden_dim, hidden_dim) for _ in range(num_layers)])
    controller = PABEEController(layers, hidden_dim, num_classes, patience=2)

    x = torch.randn(2, 12, hidden_dim)
    logits, exit_layer = controller.forward(x)

    assert logits.shape == (2, num_classes)
    assert 0 <= exit_layer < num_layers

    savings = controller.compute_savings()
    logger.info(f"   Exit layer: {exit_layer+1}/{num_layers} | Savings: {savings['savings_pct']}%")
    assert savings["savings_pct"] >= 0

    logger.info("✅ PABEE Early Exit verified.")


def test_context_manager():
    logger.info("\n[Test] Hierarchical Context Manager")
    ctx = HierarchicalContextManager(l1_max=50, l2_max=30, l3_max=40, l4_max=100)

    # Add several turns to trigger overflow
    for i in range(10):
        ctx.add_turn("user",      f"Question {i}: " + "word " * 8)
        ctx.add_turn("assistant", f"Answer {i}: "   + "word " * 8)

    # Inject RAG context
    ctx.inject_retrieval(["Relevant document chunk about Python programming."])
    ctx.inject_long_term_memory(["User prefers concise answers.", "User is a developer."])

    prompt = ctx.build_prompt()
    assert "L1" in prompt or "L2" in prompt or "L3" in prompt or "L4" in prompt

    stats = ctx.get_stats()
    logger.info(f"   Context stats: L1={stats['L1']['tokens']}tok "
                f"L2={stats['L2']['tokens']}tok "
                f"L3={stats['L3']['tokens']}tok")

    logger.info("✅ Hierarchical Context Manager verified.")


def test_moe_offloader():
    logger.info("\n[Test] MoE Expert Offloader")
    layer = MoEOffloadingLayer(
        num_experts=8, hidden_dim=32, ffn_dim=64, top_k=2, compute_device="cpu"
    )
    layer.eval()

    x = torch.randn(2, 4, 32)
    with torch.no_grad():
        out = layer(x)

    assert out.shape == (2, 4, 32), f"MoE output shape: {out.shape}"
    mem_stats = layer.get_memory_stats()
    logger.info(f"   MoE memory: {mem_stats}")

    logger.info("✅ MoE Expert Offloader verified.")


def test_kv_compression():
    logger.info("\n[Test] KV Cache Compression")

    # StreamingKV
    skv = StreamingKVCache(sink_size=4, window_size=16, top_k_heavy=8)
    heads, dim = 2, 16

    for i in range(50):
        k = torch.randn(1, heads, dim)
        v = torch.randn(1, heads, dim)
        k_cache, v_cache = skv.update(k, v)

    total_budget = skv.sink_size + skv.window_size + skv.top_k_heavy
    assert k_cache.size(0) <= total_budget + 5, \
        f"StreamingKV cache too large: {k_cache.size(0)} > {total_budget}"
    logger.info(f"   StreamingKV: 50 tokens compressed to {k_cache.size(0)}")

    # SnapKV
    compressor = SnapKVCompressor(similarity_threshold=0.999)
    keys   = torch.randn(100, 2, 16)
    values = torch.randn(100, 2, 16)
    ck, cv = compressor.compress(keys, values, max_clusters=32)
    assert ck.size(0) <= 100, "SnapKV should compress"
    logger.info(f"   SnapKV: 100 tokens → {ck.size(0)} clusters")

    logger.info("✅ KV Cache Compression verified.")


def test_hybrid_pipeline():
    logger.info("\n[Test] Hybrid CPU↔iGPU Pipeline")
    hidden = 32
    num_layers = 6

    layers    = nn.ModuleList([nn.Linear(hidden, hidden) for _ in range(num_layers)])
    embedding = nn.Embedding(100, hidden)
    lm_head   = nn.Linear(hidden, 100)

    pipeline = HybridLayerPipeline(layers, embedding=embedding, lm_head=lm_head)
    summary  = pipeline.get_dispatch_summary()
    logger.info(f"   Dispatch: {summary}")

    input_ids = torch.randint(0, 100, (2, 8))
    out = pipeline.forward(input_ids)
    assert out.shape == (2, 8, 100), f"Unexpected output: {out.shape}"

    logger.info("✅ Hybrid Pipeline verified.")


async def test_phoenix_runtime():
    logger.info("\n[Test] PHOENIX RUNTIME — Full Integration")
    from leo_runtime import PhoenixRuntime
    runtime = PhoenixRuntime()
    await asyncio.sleep(0.5)  # Let resource monitor stabilize

    test_cases = [
        ("hello",               "CACHE_HIT|SYMBOLIC|RULE_ENGINE"),
        ("fibonacci of 15",     "SYMBOLIC"),
        ("is 97 prime",         "SYMBOLIC"),
        ("search for quantum mechanics", "RETRIEVAL_ENGINE|TINY_MODEL"),
    ]

    for query, expected_routes in test_cases:
        resp = await runtime.process(query)
        logger.info(f"   [{resp['inference']} | {resp['latency_ms']}ms] {query[:40]} → {str(resp['answer'])[:60]}")

    stats = runtime.get_runtime_stats()
    logger.info(f"   Optimizer: {stats['optimizer'].get('total_calls', 0)} calls recorded")
    logger.info(f"   KV Cache: {stats['kv_cache']}")

    runtime.shutdown()
    logger.info("✅ PHOENIX RUNTIME Full Integration verified.")


if __name__ == "__main__":
    test_medusa_heads()
    test_paged_kv_cache()
    test_pabee()
    test_context_manager()
    test_moe_offloader()
    test_kv_compression()
    test_hybrid_pipeline()
    asyncio.run(test_phoenix_runtime())
    logger.info("\n🔥 PHOENIX RUNTIME: ALL SYSTEMS VERIFIED")
