from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class LeoPerceivedResponse(BaseModel):
    what_i_know: str
    what_is_uncertain: Optional[str] = None
    best_possible_answer: str
    next_steps: List[str] = Field(default_factory=list)
    confidence_score: float
    perceived_status: str = "SUCCESS" # Always success/useful
    framing: Optional[str] = None

class QueryRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = "default"

