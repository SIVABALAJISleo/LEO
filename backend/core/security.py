import os
import logging
from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

try:
    import firebase_admin
    from firebase_admin import auth, credentials
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("Warning: firebase-admin not found. Security will be strictly mock/bypass if configured.")

# Initialize Firebase Admin
if FIREBASE_AVAILABLE:
    cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        try:
            firebase_admin.initialize_app()
        except Exception as e:
            print(f"Warning: Firebase Admin not initialized. {e}")

import jwt
import time
from typing import Optional

security = HTTPBearer(auto_error=False)

# Module-level guard against missing JWT secret
if os.getenv("APP_ENV", "production") == "production" and not os.getenv("JWT_SECRET"):
    raise RuntimeError("CRITICAL SECURITY ERROR: JWT_SECRET environment variable is missing in production. Refusing to boot.")

async def verify_firebase_token(request: Request, auth_creds: Optional[HTTPAuthorizationCredentials] = Security(security)):
    """Verifies the Firebase ID Token or local JWT. Fails back to mock only in DEV."""
    app_env = os.getenv("APP_ENV", "production")
    
    token_str = None
    if auth_creds and auth_creds.credentials:
        token_str = auth_creds.credentials
    else:
        # Fallback to cookie
        token_str = request.cookies.get("leo.jwt")

    if not token_str:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    is_dev = app_env == "development"
    is_audit_token = token_str == "AUDIT_MODE_TOKEN"
    is_test_token = token_str.startswith("token-")
    
    # 1. Dev Mode Bypass Check (strictly restricted to APP_ENV == "development")
    if is_dev and os.getenv("LEO_ALLOW_DEV_AUTH_BYPASS") == "1" and (is_audit_token or is_test_token or not FIREBASE_AVAILABLE or os.getenv("LEO_OFFLINE") == "1"):
        uid = token_str.replace("token-", "") if is_test_token else "dev_user"
        decoded = {
            "uid": uid, 
            "email": f"{uid}@hyper-saas.com", 
            "role": "admin",
            "tenant_id": f"tenant_{uid}",
            "exp": int(time.time()) + 3600
        }
        request.state.user = decoded
        return decoded
    
    # 2. Local JWT Signature Validation (for backend-issued custom JWTs)
    jwt_secret = os.getenv("JWT_SECRET")
    if not jwt_secret:
        raise HTTPException(status_code=500, detail="JWT_SECRET is not configured on the server.")
    try:
        decoded = jwt.decode(token_str, jwt_secret, algorithms=["HS256"])
        if decoded.get("exp") and decoded["exp"] < time.time():
            raise HTTPException(status_code=401, detail="Token has expired")
        request.state.user = decoded
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        pass

    # 3. Firebase Token Validation
    if not FIREBASE_AVAILABLE:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed: Firebase service unavailable and mock auth disabled.",
        )
        
    try:
        decoded_token = auth.verify_id_token(token_str)
        if decoded_token.get("exp") and decoded_token["exp"] < time.time():
            raise HTTPException(status_code=401, detail="Token has expired")
            
        if "tenant_id" not in decoded_token:
            decoded_token["tenant_id"] = f"tenant_{decoded_token.get('uid')}"
        
        request.state.user = decoded_token
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def setup_cors(app):
    """Configures CORS for the application."""
    # Read from env if available, otherwise use defaults
    env_origins = os.getenv("ALLOWED_ORIGINS", "")
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:8081",
        "https://hyper-saas.com",
    ]
    if env_origins:
        origins.extend([o.strip() for o in env_origins.split(",")])
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Standard alias for unified security checks
verify_token = verify_firebase_token


def patch_onnx_security():
    """
    Zero-trust overlay for onnx module load.
    Completes the mitigation for the unpatched onnx.hub.load CVE.
    Upstream resolved this by removing the feature entirely. We mimic that here.
    """
    try:
        import onnx.hub as _hub # type: ignore
        def _removed_feature(*args, **kwargs):
            raise SecurityError(
                "onnx.hub.load() has been permanently disabled due to a critical "
                "supply-chain vulnerability (Silent execution via silent=True). "
                "This feature was removed to enforce zero-trust architecture."
            )
        _hub.load = _removed_feature
        
        import logging
        logging.getLogger("hyper.security").info("onnx load module patched — feature removed (CVE mitigation)")
    except ImportError:
        pass  # onnx not installed, nothing to patch

class SecurityError(Exception):
    pass

def patch_gitpython_security():
    """
    Patches GitPython <= 3.1.49 against CVE-2026-42215 newline injection bypass.
    Validates section and option parameters in config_writer() set_value()
    to prevent forged core.hooksPath headers causing RCE.
    """
    try:
        import git.config
        
        original_set_value = git.config.GitConfigParser.set_value
        
        _FORBIDDEN_CHARS = {'\n', '\r', '\x00'}

        def safe_set_value(self, section: str, option: str, value):
            # Check actual control characters — NOT escaped literals
            if any(c in section for c in _FORBIDDEN_CHARS):
                raise ValueError(
                    "Security violation: control characters (\\n, \\r, NUL) are not allowed "
                    "in Git config section names (CVE-2026-42215 mitigation)"
                )
            if any(c in option for c in _FORBIDDEN_CHARS):
                raise ValueError(
                    "Security violation: control characters (\\n, \\r, NUL) are not allowed "
                    "in Git config option names (CVE-2026-42215 mitigation)"
                )
            return original_set_value(self, section, option, value)
            
        git.config.GitConfigParser.set_value = safe_set_value
        
        import logging
        logging.getLogger("hyper.security").info("GitPython config_writer patched — newline injection prevented (CVE mitigation)")
    except ImportError:
        pass  # GitPython not installed, nothing to patch

# Apply the patches at import time so they take effect before any other code
patch_onnx_security()
patch_gitpython_security()
