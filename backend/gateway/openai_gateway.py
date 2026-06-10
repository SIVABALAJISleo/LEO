"""
backend/gateway/openai_gateway.py
OpenAI-Compatible API Gateway router (Tier 9).
Provides standard chat completion and embedding endpoints to serve as a drop-in replacement
for standard OpenAI client SDKs, intercepting and cascades routing through the LEO 12-Layer cascade.
"""
import time
import uuid
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from backend.core.leo_orchestrator import global_leo_orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["OpenAI API Gateway"])

# ── OpenAI Schema Specifications ────────────────────────────────────────── #

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "leo-zni-turbo"
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False
    max_tokens: Optional[int] = 2048

class EmbeddingRequest(BaseModel):
    input: Any  # Can be string or list of strings
    model: str = "leo-text-embedding"

# ── Gateway endpoints ────────────────────────────────────────────────────── #

@router.post("/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    """
    OpenAI-Compatible /v1/chat/completions Drop-In Replacement.
    Intercepts standard client SDK queries and pipes them through LEO's 12-Layer cascade.
    """
    if not req.messages:
        raise HTTPException(status_code=400, detail="Messages list cannot be empty.")
    
    # Intercept the latest query
    query = req.messages[-1].content
    logger.info(f"[GATEWAY] Intercepted chat completion request: model={req.model} query_len={len(query)}")
    
    t0 = time.time()
    
    # Run through the LEO 12-Layer cascade orchestrator
    workflow_result = await global_leo_orchestrator.execute_semantic_workflow(query)
    answer = workflow_result.get("result", "")
    resolved_by = workflow_result.get("resolved_by", "Cascade")
    metrics = workflow_result.get("metrics", {})
    
    # Calculate simulated token metrics
    prompt_tokens = max(len(query) // 4, 1)
    completion_tokens = max(len(answer) // 4, 1)
    total_tokens = prompt_tokens + completion_tokens
    
    # Format according to official OpenAI OpenAPI spec v2
    completion_id = f"chatcmpl-{uuid.uuid4()}"
    response = {
        "id": completion_id,
        "object": "chat.completion",
        "created": int(t0),
        "model": req.model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": answer
                },
                "logprobs": None,
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        },
        "system_fingerprint": f"fp_leo_zni_{resolved_by.replace(' ', '_').lower()}",
        # Custom LEO metadata injected as extensions (fully compatible)
        "x_leo_metadata": {
            "resolved_by": resolved_by,
            "latency_ms": workflow_result.get("latency_ms", 0.0),
            "compute_avoided": workflow_result.get("compute_avoided", True),
            "gpu_watts_saved": workflow_result.get("gpu_watts_saved", 0.0),
            "entropy_tier": workflow_result.get("entropy_tier", "low"),
            "avoidance_rate_pct": metrics.get("avoidance_rate_pct", 95.0),
            "avoided_cloud_spend_usd": metrics.get("avoided_cloud_spend_usd", 0.0)
        }
    }
    
    logger.info(f"[GATEWAY] Served client query via {resolved_by} in {response['x_leo_metadata']['latency_ms']}ms.")
    return response


@router.post("/embeddings")
async def embeddings(req: EmbeddingRequest):
    """
    OpenAI-Compatible /v1/embeddings Drop-In Replacement.
    Uses local fast embedders to resolve embeddings locally.
    """
    t0 = time.time()
    
    # Standardize input to list
    inputs = req.input
    if isinstance(inputs, str):
        inputs = [inputs]
        
    logger.info(f"[GATEWAY] Intercepted embedding request: inputs={len(inputs)}")
    
    # Retrieve LEO embedder dynamically
    from backend.cache.semantic_cache import TrigramEmbedder
    encoder = None
    try:
        from sentence_transformers import SentenceTransformer
        encoder = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        encoder = TrigramEmbedder()
        
    data = []
    total_tokens = 0
    
    for idx, text in enumerate(inputs):
        vec = encoder.encode(text)
        # Convert to list of floats
        embedding_list = [float(x) for x in vec]
        total_tokens += max(len(text) // 4, 1)
        
        data.append({
            "object": "embedding",
            "index": idx,
            "embedding": embedding_list
        })
        
    return {
        "object": "list",
        "data": data,
        "model": req.model,
        "usage": {
            "prompt_tokens": total_tokens,
            "total_tokens": total_tokens
        },
        "x_leo_metadata": {
            "latency_ms": round((time.time() - t0) * 1000, 2),
            "local_only": True
        }
    }
