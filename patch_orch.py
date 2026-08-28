import re

with open(r"c:\Users\sivab\OneDrive\Documents\HYPER\remix-of-remix-of-remix-of-nvidia-inspired-design-main\backend\core\orchestrator.py", "r", encoding="utf-8") as f:
    code = f.read()

new_process_core = """    async def _process_core(self, query: str, request_id: str, tenant_id: str, workspace_id: str, start_time: float):
        import time
        from backend.analytics.metrics import global_metrics
        from backend.shadow.shadow_store import global_shadow_store
        from backend.shadow.shadow_worker import global_shadow_worker
        from backend.rag.embedding_model import search as rag_search
        from backend.intelligence.delta_engine import global_delta_engine_v2
        from backend.compression.fragments import global_fragment_compressor
        from backend.micro_models.router import global_micro_router
        from backend.models.llm_loader import generate_response

        logger.info(f"request_start: id={request_id} query={query} tenant={tenant_id}")
        global_metrics.track_query()
        user_id = request_id.split("_")[1] if "_" in request_id else "default"
        session_id = user_id

        # -------------------------------------------------------------
        # STRICT OPTIMIZATION PIPELINE
        # -------------------------------------------------------------

        # 1. SHADOW STORE (Precomputed predictions)
        shadow_hit = global_shadow_store.lookup(query, session_id, tenant_id=tenant_id, workspace_id=workspace_id)
        if shadow_hit:
            global_metrics.track_hit("shadow")
            logger.info("pipeline_hit: shadow_store")
            return self._wrap_response(shadow_hit["answer"], "SHADOW_STORE", start_time, shadow_hit["confidence"])

        # 2. DELTA ENGINE (Semantic caching & partial reuse)
        delta = global_delta_engine_v2.find_delta(query)
        if delta:
            if delta["mode"] == "FULL_MATCH":
                global_metrics.track_hit("cache")
                logger.info("pipeline_hit: exact_cache")
                return self._wrap_response(delta["answer"], "CACHE_EXACT", start_time, 1.0)
            elif delta["mode"] == "PARTIAL_MATCH":
                global_metrics.track_hit("delta")
                logger.info("pipeline_hit: delta_match")
                return self._wrap_response(delta["answer"], "DELTA_COMPOSED", start_time, 0.95)

        # 3. MICRO MODELS (Specialized fast bypass for math/code/summary)
        specialty = global_micro_router.route(query)
        if specialty:
            global_metrics.track_hit("micro")
            logger.info(f"pipeline_hit: micro_model ({specialty})")
            answer = await global_micro_router.execute(query, specialty)
            global_delta_engine_v2.register_answer(query, answer)
            return self._wrap_response(answer, f"MICRO_MODEL_{specialty.upper()}", start_time, 0.95)

        # 4. MEMORY / FRAGMENT ASSEMBLY (Dynamic Composition)
        fragments = global_fragment_compressor.fragmentize_and_store(query) # In a real implementation we look up fragments
        # Actually, let's assemble using RAG fragments if we can.
        
        # 5. FULL RAG + LLM GENERATION (Last Resort)
        global_metrics.track_model_call()
        logger.info("pipeline_miss: executing full RAG + LLM computation")
        
        # Retrieve context
        rag_results = rag_search(query, k=3)
        context_str = "\\n".join([r["content"] for r in rag_results])
        if rag_results:
            global_metrics.track_hit("rag")
            
        system_prompt = (
            "You are a helpful AI assistant. Answer the user's question clearly.\\n"
            f"Use the following context if relevant:\\n{context_str}"
        )
        
        # Generates response
        import asyncio
        loop = asyncio.get_event_loop()
        answer = await loop.run_in_executor(
            None, generate_response, query, 512, 0.7, system_prompt
        )

        # Post-computation: Store for future optimization
        global_delta_engine_v2.register_answer(query, answer)
        global_fragment_compressor.fragmentize_and_store(answer)
        
        # Trigger shadow worker for next turns
        asyncio.create_task(global_shadow_worker.precompute_next_turns(query, session_id, tenant_id, workspace_id))

        return self._wrap_response(answer, "FULL_COMPUTE", start_time, 0.9)"""

# Regex replacement: find async def _process_core to async def process_stream
pattern = r"    async def _process_core\(.*?    async def process_stream\("
new_content = re.sub(pattern, new_process_core + "\n\n    async def process_stream(", code, flags=re.DOTALL)

with open(r"c:\Users\sivab\OneDrive\Documents\HYPER\remix-of-remix-of-remix-of-nvidia-inspired-design-main\backend\core\orchestrator.py", "w", encoding="utf-8") as f:
    f.write(new_content)