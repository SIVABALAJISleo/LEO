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
from backend.services.ai_router_service import AIRouterService

router = APIRouter(prefix="/api/v1/ollama", tags=["Local AI (Ollama)"])
service = OllamaService()
ai_router = AIRouterService()

class ChatRequest(BaseModel):
    prompt: str = Field(..., description="Prompt string to process")
    system_message: Optional[str] = Field("You are a helpful local assistant powered by LEO AI.", description="Optional system instruction overrides")
    model: Optional[str] = Field(None, description="Local model name")
    route_mode: Optional[str] = Field("auto", description="Model routing path: auto | colibri | ollama")

@router.get("/health")
async def get_ollama_health():
    """Returns connectivity health diagnostics for the local Ollama instance."""
    return service.check_health()

@router.get("/capabilities")
async def get_system_capabilities():
    """Returns local system hardware specifications and Colibri viability parameters."""
    return ai_router.check_capabilities()

@router.post("/chat")
async def run_ollama_chat(body: ChatRequest):
    """Streams a completion response token-by-token using Server-Sent Events (SSE)."""
    return StreamingResponse(
        ai_router.generate_stream(
            prompt=body.prompt,
            system_message=body.system_message,
            model=body.model,
            route_mode=body.route_mode
        ),
        media_type="text/event-stream"
    )

