"""
backend/routers/ollama_chat.py
FastAPI router for local Ollama AI endpoints.
Supports Server-Sent Events (SSE) streaming.
"""

from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
from backend.services.ollama_service import OllamaService

router = APIRouter(prefix="/api/v1/ollama", tags=["Local AI (Ollama)"])
service = OllamaService()

class ChatRequest(BaseModel):
    prompt: str = Field(..., description="Prompt string to process")
    system_message: Optional[str] = Field("You are a helpful local assistant powered by LEO AI.", description="Optional system instruction overrides")
    model: Optional[str] = Field(None, description="Local model name")

@router.get("/health")
async def get_ollama_health():
    """Returns connectivity health diagnostics for the local Ollama instance."""
    return service.check_health()

@router.post("/chat")
async def run_ollama_chat(body: ChatRequest):
    """Streams a completion response token-by-token using Server-Sent Events (SSE)."""
    return StreamingResponse(
        service.generate_stream(
            prompt=body.prompt,
            system_message=body.system_message,
            model=body.model
        ),
        media_type="text/event-stream"
    )
