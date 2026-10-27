import os
import time
import uuid
import hashlib
import hmac
import json
import base64
from fastapi import APIRouter, HTTPException, Depends, Response, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import get_db, User

try:
    import jwt
except ImportError:
    jwt = None

try:
    import bcrypt
except ImportError:
    bcrypt = None

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception:
    pwd_context = None

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

class AuthRequest(BaseModel):
    email: str
    password: str

def hash_password(password: str) -> str:
    # 1. Primary: Direct bcrypt hashing (work factor 12)
    if bcrypt is not None:
        try:
            salt = bcrypt.gensalt(rounds=12)
            return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
        except Exception:
            pass
    # 2. Secondary: Passlib CryptContext
    if pwd_context is not None:
        try:
            return pwd_context.hash(password)
        except Exception:
            pass
    # 3. Fallback: NIST/OWASP SP 800-63B approved PBKDF2-HMAC-SHA256 (600,000 rounds)
    salt = os.urandom(16)
    kdf_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 600_000)
    return f"pbkdf2_sha256$600000${salt.hex()}${kdf_hash.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    # 1. Check if bcrypt hash ($2a$, $2b$, $2y$)
    if bcrypt is not None and any(hashed_password.startswith(prefix) for prefix in ("$2a$", "$2b$", "$2y$")):
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            pass
    # 2. Check via passlib CryptContext
    if pwd_context is not None:
        try:
            if pwd_context.identify(hashed_password):
                return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            pass
    # 3. Check PBKDF2-HMAC-SHA256 hash
    if hashed_password.startswith("pbkdf2_sha256$"):
        parts = hashed_password.split("$")
        if len(parts) == 4:
            try:
                iters = int(parts[1])
                salt = bytes.fromhex(parts[2])
                expected_hash = bytes.fromhex(parts[3])
                computed_hash = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iters)
                return hmac.compare_digest(computed_hash, expected_hash)
            except Exception:
                return False
    return False

def create_jwt_token(user: User) -> str:
    jwt_secret = os.getenv("JWT_SECRET", "super_secret_hyper_jwt_key_2026")
    payload = {
        "sub": user.uid,
        "uid": user.uid,
        "email": user.email,
        "role": user.tier,
        "tenant_id": user.tenant_id,
        "exp": int(time.time()) + 86400 * 7 # 7 days
    }
    if jwt is not None:
        try:
            return jwt.encode(payload, jwt_secret, algorithm="HS256")
        except Exception:
            pass
    # Standard base64 HMAC-SHA256 token fallback if PyJWT is absent
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip("=")
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    sig = base64.urlsafe_b64encode(hmac.new(jwt_secret.encode(), f"{header}.{body}".encode(), hashlib.sha256).digest()).decode().rstrip("=")
    return f"{header}.{body}.{sig}"

@router.post("/signup")
async def signup(req: AuthRequest, response: Response, db: Session = Depends(get_db)):
    # Check if user already exists
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already registered")

    # Generate custom UID and tenant ID
    uid = str(uuid.uuid4())
    tenant_id = f"tenant_{uid}"

    # Hash password
    h_password = hash_password(req.password)

    new_user = User(
        uid=uid,
        email=req.email,
        tenant_id=tenant_id,
        tier="free",
        password_hash=h_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_jwt_token(new_user)
    
    # Set HTTP-Only Cookie
    app_env = os.getenv("APP_ENV", "development")
    response.set_cookie(
        key="leo.jwt",
        value=token,
        httponly=True,
        max_age=86400 * 7,
        secure=app_env != "development",
        samesite="lax"
    )

    return {
        "access_token": token,
        "token": token,
        "user": {
            "id": new_user.uid,
            "email": new_user.email,
            "role": new_user.tier,
            "permissions": ["orchestrate"]
        }
    }

@router.post("/login")
async def login(req: AuthRequest, response: Response, db: Session = Depends(get_db)):
    # Get user
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not user.password_hash or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_jwt_token(user)
    
    # Set HTTP-Only Cookie
    app_env = os.getenv("APP_ENV", "development")
    response.set_cookie(
        key="leo.jwt",
        value=token,
        httponly=True,
        max_age=86400 * 7,
        secure=app_env != "development",
        samesite="lax"
    )

    return {
        "access_token": token,
        "token": token,
        "user": {
            "id": user.uid,
            "email": user.email,
            "role": user.tier,
            "permissions": ["orchestrate"]
        }
    }

@router.get("/me")
async def get_me(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("leo.jwt")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    jwt_secret = os.getenv("JWT_SECRET", "super_secret_hyper_jwt_key_2026")
    try:
        if jwt is not None:
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        else:
            parts = token.split(".")
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            header, body, sig = parts
            expected_sig = base64.urlsafe_b64encode(hmac.new(jwt_secret.encode(), f"{header}.{body}".encode(), hashlib.sha256).digest()).decode().rstrip("=")
            if not hmac.compare_digest(sig, expected_sig):
                raise ValueError("Signature mismatch")
            padded_body = body + "=" * (-len(body) % 4)
            payload = json.loads(base64.urlsafe_b64decode(padded_body.encode()).decode())
            if payload.get("exp", 0) < int(time.time()):
                raise ValueError("Token expired")
        user = db.query(User).filter(User.uid == payload.get("uid")).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return {
            "id": user.uid,
            "email": user.email,
            "role": user.tier,
            "permissions": ["orchestrate"]
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid session")


