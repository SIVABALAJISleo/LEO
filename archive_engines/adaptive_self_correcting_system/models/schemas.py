from pydantic import BaseModel, Field
from typing import Any
from enum import Enum
from datetime import datetime

class CascadeLayer(str, Enum):
    CACHE = "CACHE"
    RAG = "RAG"
    TINY = "TINY"
    MEDIUM = "MEDIUM"
    HEAVY = "HEAVY"

class CascadeStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FALLBACK = "FALLBACK"
    DEGRADED = "DEGRADED"

class CascadeResponse(BaseModel):
    answer: Any
    layer_handled: CascadeLayer
    confidence: float = Field(..., ge=0, le=1.0)
    latency_ms: float
    status: CascadeStatus
    compute_cost_score: float # 0 (cache) to 1.0 (heavy)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
