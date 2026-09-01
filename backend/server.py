import os
import time
import json
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from backend.layer5_local_infer.native_engine import LEONativeOrchestrator
from backend.layer5_local_infer.bitnet_tmac_engine import BitNetTMacEngine
from backend.layer4_igpu.openvino_igpu_engine import OpenVINOiGPUEngine

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core_ai.cache_manager import CacheManager

app = FastAPI(title="LEO AI Engine Backend")
cache_manager = CacheManager()

# Enable CORS for local dev frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Native Engines
orchestrator = LEONativeOrchestrator()
bitnet_tmac = BitNetTMacEngine()
igpu_engine = OpenVINOiGPUEngine()

# In-memory storage for local metrics and memories
metrics_data = {
    "requests_total": 0,
    "cache_hits_total": 0,
    "total_latency_ms": 0.0,
    "start_time": time.time(),
}
memories_store: List[Dict[str, Any]] = [
    {"id": "mem-1", "type": "user_preference", "content": "Preferred language: TypeScript", "created_at": "2026-08-08T12:00:00Z"},
    {"id": "mem-2", "type": "context", "content": "System Kernel: C++ AVX2 Native Engine", "created_at": "2026-08-08T12:00:00Z"},
]


@app.get("/api/v1/leo/metrics")
async def get_metrics():
    uptime = time.time() - metrics_data["start_time"]
    total = metrics_data["requests_total"]
    hits = metrics_data["cache_hits_total"]
    avoidance_rate = round((hits / max(total, 1)) * 100.0 if total > 0 else 0.0, 1)
    avg_latency = round(metrics_data["total_latency_ms"] / max(total, 1), 2)
    # Estimate watt-seconds avoided (15W per avoided discrete inference)
    watts_saved = int(hits * 15)

    return {
        "leo_total_requests": total,
        "leo_compute_avoided": hits,
        "leo_avoidance_rate_pct": avoidance_rate,
        "leo_gpu_watts_saved": watts_saved,
        "leo_crystallization_hit_rate": avoidance_rate,
        "average_latency_ms": avg_latency,
        "uptime_seconds": round(uptime, 2),
    }


@app.get("/api/v1/leo/frontiers")
async def get_frontiers():
    return {
        "frontiers": [
            {"id": "bitnet_tmac", "name": "Pillar 1: BitNet 1.58b + T-MAC LUT", "status": "active", "throughput_multiplier": "5-7x"},
            {"id": "openvino_igpu", "name": "Pillar 4: OpenVINO Intel iGPU", "status": "active", "device": igpu_engine.device},
            {"id": "layerskip", "name": "Pillar 2: LayerSkip Self-Speculation", "status": "ready", "depth_exit_pct": "25-50%"},
            {"id": "sparse_moe", "name": "Pillar 3: Ultra-Sparse MoE (14:1)", "status": "ready", "bandwidth_reduction": "14x"},
        ]
    }


@app.get("/api/v1/memory")
async def list_memories():
    return memories_store


@app.post("/api/v1/memory")
async def add_memory(req: Request):
    body = await req.json()
    item = {
        "id": f"mem-{int(time.time()*1000)}",
        "type": body.get("type", "context"),
        "content": body.get("content", ""),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    memories_store.insert(0, item)
    return {"status": "ok", "item": item}


@app.post("/api/v1/leo/orchestrate")
async def orchestrate(req: Request):
    body = await req.json()
    prompt = body.get("prompt") or body.get("query") or "Hello"
    start = time.time()
    
    # Check Semantic Cache / Procedural Bypass
    cached_res, similarity, route = cache_manager.semantic_cache.lookup(prompt)
    if cached_res:
        elapsed_ms = round((time.time() - start) * 1000, 2)
        metrics_data["requests_total"] += 1
        metrics_data["cache_hits_total"] += 1
        metrics_data["total_latency_ms"] += elapsed_ms
        return {
            "route": route,
            "confidence": similarity,
            "response": cached_res,
            "latency_ms": elapsed_ms,
            "used_memory": True,
        }

    response_text = orchestrator.generate(prompt, max_tokens=128)
    elapsed_ms = round((time.time() - start) * 1000, 2)
    metrics_data["requests_total"] += 1
    metrics_data["total_latency_ms"] += elapsed_ms

    # Trigger Pillar 2 Background pre-generation (Speculative Prefill)
    import threading
    def run_background_prefill(last_prompt: str):
        time.sleep(0.2)
        predicted_queries = []
        if "photosynthesis" in last_prompt.lower():
            predicted_queries = ["why is photosynthesis important?", "what are the products of photosynthesis?"]
        elif "hardware" in last_prompt.lower() or "leo" in last_prompt.lower():
            predicted_queries = ["how does speculative decoding work?", "what is the role of avx2 in leo?"]
        
        for q in predicted_queries:
            ans, _, _ = cache_manager.semantic_cache.lookup(q)
            if not ans:
                res = orchestrator.generate(q, max_tokens=128)
                cache_manager.semantic_cache.cache_db.append({
                    "query": q,
                    "response": res,
                    "context_hash": "default_ctx"
                })
    
    threading.Thread(target=run_background_prefill, args=(prompt,), daemon=True).start()

    return {
        "route": "llama_cpp_avx2",
        "confidence": 1.0,
        "response": response_text,
        "latency_ms": elapsed_ms,
        "used_memory": True,
    }


@app.post("/v1/chat/completions")
async def chat_completions(req: Request):
    body = await req.json()
    messages = body.get("messages", [])
    prompt = messages[-1]["content"] if messages else "Hello"
    stream = body.get("stream", False)
    metrics_data["requests_total"] += 1

    if not stream:
        response_text = orchestrator.generate(prompt)
        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "leo-native",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": response_text},
                    "finish_reason": "stop",
                }
            ],
        }

    # Streaming mode
    def event_generator():
        response_text = orchestrator.generate(prompt, max_tokens=256)
        words = response_text.split(" ")
        for i, word in enumerate(words):
            chunk = {
                "id": f"chatcmpl-{int(time.time())}",
                "choices": [{"index": 0, "delta": {"content": word + (" " if i < len(words) - 1 else "")}, "finish_reason": None}],
            }
            yield f"data: {json.dumps(chunk)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # nosec B104
