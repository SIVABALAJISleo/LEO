import logging
from fastapi import Request, HTTPException, UploadFile, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Security configuration
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB limit for vision models
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/webp"]

class SecureHeadersMiddleware(BaseHTTPMiddleware):
    """
    Injects enterprise-grade security headers into every FastAPI response.
    """
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # In full production we'd configure a strict CSP
        # response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

from backend.core.hsm import cloud_hsm

def verify_token_locally(token: str):
    """Passes cryptographic validation to the HSM boundary."""
    return cloud_hsm.verify_jwt(token)

def verify_jwt_token(token: str):
    """
    Simulates JWT Validation.
    """
    decoded = verify_token_locally(token)
    if "error" in decoded:
        logger.warning(f"JWT Validation Failed: {decoded['error']}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {decoded['error']}",
        )
    return decoded

async def verify_upload_safety(file: UploadFile):
    """
    Defense-in-depth utility.
    Ensures that bad actors don't upload malicious payloads or massive zip bombs 
    that could bring down the underlying vision engines.
    """
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported media type: {file.content_type}. Allowed: {', '.join(ALLOWED_MIME_TYPES)}"
        )
        
    # Read snippet to verify size stream without loading fully into memory if needed
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File size visually exceeds limit of {MAX_UPLOAD_SIZE / (1024*1024)}MB"
        )
        
    # Magic Number (Byte Signature) Checking for Images
    MAGIC_NUMBERS = {
        "image/jpeg": [b'\xFF\xD8\xFF'],
        "image/png": [b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'],
        "image/webp": [b'RIFF', b'WEBP']  # RIFF starts at 0, WEBP at 8, we simplify
    }
    
    file_header = file.file.read(12)
    file.file.seek(0) # Reset stream
    
    expected_magics = MAGIC_NUMBERS.get(file.content_type, [])
    is_valid = False
    
    for magic in expected_magics:
         if magic in file_header:
             is_valid = True
             break
             
    # Strict handling: If it doesn't match its own claimed MIME header
    if expected_magics and not is_valid:
        logger.error(f"Malware/Tampering Detection: IP Attempted to disguise file signature as {file.content_type}")
        raise HTTPException(status_code=415, detail="Invalid file signature (tampering detected)")
        
    return True
