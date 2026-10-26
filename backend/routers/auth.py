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
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except ImportError:
    pwd_context = None

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

class AuthRequest(BaseModel):
    email: str
    password: str

def hash_password(password: str) -> str:
    if pwd_context is not None:
        try:
            return pwd_context.hash(password)
        except Exception:
            pass
    salt = os.urandom(16).hex()
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"sha256${salt}${h}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if pwd_context is not None:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            pass
    if hashed_password.startswith("sha256$"):
        parts = hashed_password.split("$")
        if len(parts) == 3:
            salt, h = parts[1], parts[2]
            computed = hashlib.sha256((salt + plain_password).encode()).hexdigest()
            return hmac.compare_digest(computed, h)
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


