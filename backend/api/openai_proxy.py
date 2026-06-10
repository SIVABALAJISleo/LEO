"""
backend/api/openai_proxy.py
LEO: STAGE 17 — ENTERPRISE OVERLAY MODE

Provides full OpenAI API compatibility. Existing enterprise apps can just point 
their base_url to this server, seamlessly dropping cloud inference for local procedural execution.
"""

import time
import uuid
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

from backend.api.universal_adapter import api_runtime

# --- OpenAI Request Schemas ---

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 1.0
    stream: Optional[bool] = False

class EmbeddingRequest(BaseModel):
    input: Union[str, List[str]]
    model: str

# --- Implementation ---

async def handle_chat_completion(req: ChatCompletionRequest) -> Dict[str, Any]:
    """
    Acts as a drop-in replacement for OpenAI chat completions.
    Extracts the user prompt, runs it through the Universal Adapter (Stages 1-16),
    and formats the result back as a standard OpenAI JSON object.
    """
    # Extract the last user message as the core query
    query = req.messages[-1].content
    
    # Execute through the 17-Stage OS Pipeline
    result = await api_runtime.generate(query)
    
    answer_text = result.get("answer", "Error: No response generated.")
    trust_meta = result.get("human_trust_metadata", {})
    
    # Map back to OpenAI schema
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "leo-distributed-os",
        "system_fingerprint": f"prov_{trust_meta.get('provenance', 'unknown')}",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": answer_text
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": len(query.split()),
            "completion_tokens": len(answer_text.split()),
            "total_tokens": len(query.split()) + len(answer_text.split())
        },
        # Custom Extension: Inject Stage 15 Human Trust Layer directly into the payload
        "x_leo_trust": trust_meta
    }

def handle_embeddings(req: EmbeddingRequest) -> Dict[str, Any]:
    """
    Drop-in replacement for OpenAI embeddings.
    """
    texts = [req.input] if isinstance(req.input, str) else req.input
    data = []
    
    for idx, text in enumerate(texts):
        res = api_runtime.embed(text)
        data.append({
            "object": "embedding",
            "embedding": res.get("vector", []),
            "index": idx
        })
        
    return {
        "object": "list",
        "data": data,
        "model": "leo-semantic-os",
        "usage": {
            "prompt_tokens": 0,
            "total_tokens": 0
        }
    }
