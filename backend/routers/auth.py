import os
import time
import jwt
import uuid
from fastapi import APIRouter, HTTPException, Depends, Response, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from backend.core.database import get_db, User

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthRequest(BaseModel):
    email: str
    password: str

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

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
    return jwt.encode(payload, jwt_secret, algorithm="HS256")

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
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
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

