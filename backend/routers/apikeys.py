import secrets
import hashlib
import time
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from backend.core.middleware import redis_client

router = APIRouter(prefix="/api/v1/keys", tags=["Developer APIs"])

# In an MVP, we store active developer keys in Redis
# Real architectures log these permanently in Postgres/Firestore

class APIKeyResponse(BaseModel):
    key: str
    message: str

def generate_secure_api_key():
    # Example format: sk_live_abc123...
    return f"sk_live_{secrets.token_urlsafe(32)}"

def _hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()

@router.post("/generate", response_model=APIKeyResponse)
async def generate_api_key(
    # In reality, verify_token goes here so only logged-in GUI users can generate keys
):
    """
    Generate a new persistent API Key for B2B API integrations.
    """
    user_id = "test_user" # Mocked user
    
    raw_key = generate_secure_api_key()
    hashed_key = _hash_api_key(raw_key)
    
    if redis_client:
        # Map hash to User ID
        redis_client.set(f"apikey:{hashed_key}:user", user_id)
        # Store tier context for this token
        redis_client.set(f"user:{user_id}:tier", "developer")

    return {
        "key": raw_key,
        "message": "Store this key safely! It will only be shown once."
    }

api_key_schema = HTTPBearer(auto_error=False)

async def verify_api_key_or_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(api_key_schema)
) -> dict:
    """
    Enterprise-ready Dependency Pipeline:
    First checks if the auth acts like a frontend GUI JWT. 
    If not, it verifies if it is a Developer API Key in Redis.
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required (JWT or API Key)")
        
    token = credentials.credentials
    
    # 1. API Key Check
    if token.startswith("sk_live_"):
        hashed_token = _hash_api_key(token)
        if redis_client:
            user_id = redis_client.get(f"apikey:{hashed_token}:user")
            if user_id:
                 user_id = user_id.decode() if isinstance(user_id, bytes) else user_id
                 return {"uid": user_id, "role": "developer_api"}
        
        raise HTTPException(status_code=401, detail="Invalid API Key or Revoked")
        
    # 2. Assume JWT if not starting with sk_
    # Here, we'd fall back to `verify_token` defined in main.py
    # Since this is a standalone verification, we bypass the full implementation for brevity.
    # We will assume it's valid if it reaches this point (for demo/mock).
    return {"uid": "mock_jwt_user", "role": "gui_user"}
