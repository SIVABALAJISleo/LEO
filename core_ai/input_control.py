from pydantic import BaseModel, ValidationError, Field
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class QuerySchema(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    session_id: str
    metadata: Dict[str, Any] = {}

class InputController:
    """
    LAYER 1: INPUT CONTROL
    - Rejects ambiguous or invalid inputs early.
    - Does NOT rely on free-form interpretation.
    """
    def validate(self, raw_input: Dict[str, Any]) -> Tuple[bool, Any]:
        try:
            validated = QuerySchema(**raw_input)
            return True, validated
        except ValidationError as e:
            logger.warning(f"Input validation failed: {e}")
            return False, {"error": "Invalid input format", "details": e.errors()}
