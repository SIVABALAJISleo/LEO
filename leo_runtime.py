"""
leo_runtime.py
PHOENIX RUNTIME — Unified Entry Point for LEO AI V∞ Research Edition.
Binds all 20 V∞ subsystems + PHOENIX RUNTIME modules into a single engine.
"""

import asyncio
import logging
import time
import os
import sys
from typing import Dict, Any, Optional

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s][%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── V∞ Core subsystems ─────────────────────────────────────────────────────────
from backend.os.orchestrator         import LEOOperatingSystem
from backend.os.resource_manager     import IntelligentResourceManager
from backend.routing.adaptive_router import AdaptiveModelRouter
from backend.caching.semantic_cache  import MultiLevelSemanticCache
from backend.retrieval.hybrid_search import HybridRetrievalEngine
from backend.intelligence.hybrid_intelligence  import HybridIntelligenceEngine
from backend.intelligence.self_verification    import SelfVerificationEngine
from backend.intelligence.prompt_compressor    import IntelligentPromptCompressor
from backend.memory.hierarchical_memory        import HierarchicalMemory
from backend.knowledge.knowledge_graph         import KnowledgeGraph
from backend.optimization.self_optimizer       import ContinuousSelfOptimizer
from backend.optimization.benchmark_framework  import BenchmarkFramework

# ── PHOENIX modules ────────────────────────────────────────────────────────────
from phoenix.context_manager  import HierarchicalContextManager
from phoenix.paged_kv_cache   import PagedKVCacheManager
from phoenix.kv_compression   import StreamingKVCache


class PhoenixRuntime:
    """
    PHOENIX RUNTIME: The unified intelligence engine.
    "Do not ask the hardware to do more. Ask the model to need less."
    """

    VERSION = "PHOENIX-V1.0 / LEO-V∞"

    def __init__(self):
        logger.info("=" * 60)
        logger.info(f"  {self.VERSION} STARTING UP")
        logger.info("=" * 60)

        t0 = time.perf_counter()

        # ── V∞ OS layer ────────────────────────────────────────────────────────
        self.leo_os        = LEOOperatingSystem()
        self.resource_mgr  = self.leo_os.resource_manager
        self.router        = AdaptiveModelRouter()

        # ── Intelligence layer ─────────────────────────────────────────────────
        self.hybrid_intel  = HybridIntelligenceEngine()
        self.verifier      = SelfVerificationEngine(min_confidence=0.15)
        self.compressor    = IntelligentPromptCompressor()

        # ── Memory layer ───────────────────────────────────────────────────────
        self.memory        = HierarchicalMemory(db_path="phoenix_memory.db")
        self.kg            = KnowledgeGraph()
        self.sem_cache     = MultiLevelSemanticCache(max_exact_items=50_000)
        self.retrieval     = HybridRetrievalEngine()

        # ── PHOENIX context ────────────────────────────────────────────────────
        self.ctx_manager   = HierarchicalContextManager(
            l1_max=1024, l2_max=256, l3_max=512, l4_max=2048
        )
        self.kv_cache      = PagedKVCacheManager(
            num_blocks=512, num_heads=8, head_dim=64
        )
        self.streaming_kv  = StreamingKVCache(
            sink_size=4, window_size=256, top_k_heavy=64
        )

        # ── Optimization layer ─────────────────────────────────────────────────
        self.self_optimizer = ContinuousSelfOptimizer(optimization_interval_sec=30.0)
        self.benchmark      = BenchmarkFramework()

        # ── Start background services ──────────────────────────────────────────
        self.self_optimizer.start()

        startup_ms = (time.perf_counter() - t0) * 1000
        logger.info(f"✅ PHOENIX RUNTIME ready in {startup_ms:.0f}ms")
        self._print_capabilities()

    def _print_capabilities(self):
        stats = self.resource_mgr.get_current_stats()
        kv_s  = self.kv_cache.stats()
        logger.info(
            f"  Hardware: CPU {stats['cpu_percent']:.0f}% | "
            f"RAM {stats['ram_percent']:.0f}% ({stats['available_ram_gb']:.1f}GB free)"
        )
        logger.info(
            f"  KV Cache: {kv_s['total_blocks']} blocks × 16 tokens = "
            f"{kv_s['total_blocks'] * 16} token capacity"
        )
        logger.info(
            f"  Context: L1={self.ctx_manager.levels['L1'].max_tokens}tok | "
            f"L2={self.ctx_manager.levels['L2'].max_tokens}tok | "
            f"L3={self.ctx_manager.levels['L3'].max_tokens}tok | "
            f"L4={self.ctx_manager.levels['L4'].max_tokens}tok"
        )

    # ── Main Request Handler ───────────────────────────────────────────────────
    async def process(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Full PHOENIX inference pipeline:
        1. Resource check
        2. Cache check (zero inference if hit)
        3. Symbolic rule engine (zero neural)
        4. Prompt compression + context assembly
        5. Adaptive routing
        6. Model execution (with self-verification)
        7. Profiling + auto-tuning
        """
        t0 = time.perf_counter()

        # ── 1. Record turn in context and memory ───────────────────────────────
        self.ctx_manager.add_turn("user", query)
        self.memory.record_turn("user", query)

        result = {
            "query":      query,
            "session_id": session_id,
            "inference":  "UNKNOWN",
            "answer":     "",
            "latency_ms": 0.0,
        }

        # ── 2. L1/L2 Semantic Cache ────────────────────────────────────────────
        cached = self.sem_cache.check_cache(query)
        if cached:
            result.update({"inference": "CACHE_HIT", "answer": cached})
            self.self_optimizer.record("CACHE_HIT", 0.5, cache_hit=True)
            self._finalize(result, t0)
            return result

        # ── 3. Symbolic / Classical resolver (zero neural) ────────────────────
        symbolic = self.hybrid_intel.solve(query)
        if symbolic:
            result.update({"inference": "SYMBOLIC", "answer": symbolic})
            self.sem_cache.add_to_cache(query, symbolic)
            self.self_optimizer.record("RULE_ENGINE", 1.0)
            self._finalize(result, t0)
            return result

        # ── 4. Adaptive Router ────────────────────────────────────────────────
        route = self.router.route_query(query)

        # ── 5. Prompt Compression ─────────────────────────────────────────────
        recent_ctx = self.memory.get_recent_context(limit=5)
        ctx_texts  = [f"{r['role']}: {r['content']}" for r in recent_ctx]
        compressed_ctx = self.compressor.compress_context(ctx_texts, max_tokens=300)

        # ── 6. Full context prompt assembly ───────────────────────────────────
        full_prompt = self.ctx_manager.build_prompt()
        logger.debug(f"Prompt assembled: {len(full_prompt.split())} words")

        # ── 7. Execution via LEO OS (routed model call) ───────────────────────
        leo_response = await self.leo_os.execute_request(query)
        answer       = leo_response.get("answer", "")

        # ── 8. Self-verification ──────────────────────────────────────────────
        verification = self.verifier.verify(answer, ctx_texts or [query])
        if not verification["verification_passed"] and verification["confidence_score"] < 0.05:
            answer = self.verifier.add_caveat(answer, verification["confidence_score"])

        # ── 9. Cache the result ───────────────────────────────────────────────
        self.sem_cache.add_to_cache(query, answer)
        self.memory.record_turn("assistant", answer)
        self.ctx_manager.add_turn("assistant", answer)

        result.update({
            "inference":    route,
            "answer":       answer,
            "confidence":   verification["confidence_score"],
            "verification": verification["verification_passed"],
        })

        # ── 10. Profile ───────────────────────────────────────────────────────
        self.self_optimizer.record(route, (time.perf_counter() - t0) * 1000)
        self._finalize(result, t0)
        return result

    def _finalize(self, result: Dict, t0: float):
        result["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        logger.info(
            f"[PHOENIX] '{result['query'][:50]}' → {result['inference']} "
            f"in {result['latency_ms']}ms"
        )

    def get_runtime_stats(self) -> Dict[str, Any]:
        """Unified telemetry from all subsystems."""
        return {
            "optimizer":  self.self_optimizer.get_live_stats(),
            "kv_cache":   self.kv_cache.stats(),
            "resources":  self.resource_mgr.get_current_stats(),
            "context":    self.ctx_manager.get_stats(),
        }

    def shutdown(self):
        logger.info("PHOENIX RUNTIME shutting down...")
        self.self_optimizer.stop()
        self.leo_os.shutdown()
        logger.info("Shutdown complete.")


# ── Web Server & CLI Entry Point ───────────────────────────────────────────────
from aiohttp import web
import json

async def handle_index(request):
    try:
        with open(os.path.join(os.path.dirname(__file__), 'chat_ui', 'index.html'), 'r', encoding='utf-8') as f:
            html = f.read()
        return web.Response(text=html, content_type='text/html')
    except Exception as e:
        return web.Response(text=f"Error loading UI: {e}", status=500)

async def handle_chat(request):
    runtime = request.app['runtime']
    try:
        data = await request.json()
        query = data.get("query", "")
        if not query:
            return web.json_response({"error": "Empty query"}, status=400)
            
        response = await runtime.process(query)
        return web.json_response(response)
    except Exception as e:
        logger.error(f"Chat API Error: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def start_web_server(runtime):
    app = web.Application()
    app['runtime'] = runtime
    app.router.add_get('/', handle_index)
    app.router.add_post('/api/chat', handle_chat)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8767)
    await site.start()
    logger.info("Chat UI Server running at: http://localhost:8767")
    return runner

async def main():
    runtime = PhoenixRuntime()
    print("\n🔥 PHOENIX RUNTIME active.")
    
    # Start web server in the background
    await start_web_server(runtime)
    
    print("   Chat UI  : http://localhost:8767")
    print("   Telemetry: http://localhost:8766")
    print("\nType 'quit' to exit, 'stats' for telemetry.\n")

    session_id = f"session_{int(time.time())}"
    
    # Run CLI in executor so it doesn't block the async web server loop
    loop = asyncio.get_running_loop()
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as pool:
        while True:
            try:
                query = await loop.run_in_executor(pool, input, "You: ")
                query = query.strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not query:
                continue
            if query.lower() == "quit":
                break
            if query.lower() == "stats":
                print(json.dumps(runtime.get_runtime_stats(), indent=2))
                continue

            response = await runtime.process(query, session_id)
            print(f"\n🔥 PHOENIX [{response['inference']} | {response['latency_ms']}ms]: "
                  f"{response['answer']}\n")

    runtime.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown requested.")
