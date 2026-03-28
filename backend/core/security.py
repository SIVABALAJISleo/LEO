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

security = HTTPBearer()

async def verify_firebase_token(request: Request, auth_creds: HTTPAuthorizationCredentials = Security(security)):
    """Verifies the Firebase ID Token. Fails back to mock if firebase-admin is missing or in DEV."""
    app_env = os.getenv("APP_ENV", "development")
    
    is_dev = app_env == "development"
    is_audit_token = auth_creds.credentials == "AUDIT_MODE_TOKEN" # nosec B105
    
    if (is_dev and is_audit_token) or (is_dev and not FIREBASE_AVAILABLE):
        # Development bypass logic
        return {
            "uid": "dev_user", 
            "email": "dev@hyper-saas.com", 
            "role": "admin",
            "tenant_id": "dev_tenant_1"
        }
    
    try:
        decoded_token = auth.verify_id_token(auth_creds.credentials)
        # Ensure tenant_id exists, fallback to uid if custom claim missing
        if "tenant_id" not in decoded_token:
            decoded_token["tenant_id"] = f"tenant_{decoded_token.get('uid')}"
        
        # Attach to request state for middleware access
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
    Zero-trust overlay for onnx.hub.load().
    Forces silent=False and blocks untrusted repos.
    Called at application startup as a defence-in-depth measure.
    """
    try:
        import onnx.hub as _hub
        _original_load = _hub.load

        def _secure_load(model, repo=None, silent=False, **kwargs):
            import logging
            _log = logging.getLogger("hyper.security.onnx")
            # Force trust verification regardless of caller's silent flag
            if repo and repo != "onnx/models":
                raise SecurityError(
                    f"Untrusted onnx model repo blocked: '{repo}'. "
                    "Only 'onnx/models' is permitted. "
                    "Use onnxruntime.InferenceSession() for local models."
                )
            _log.info(f"onnx.hub.load called with repo={repo} — trust verified")
            return _original_load(model, repo=repo, silent=False, **kwargs)

        _hub.load = _secure_load
        logging.getLogger("hyper.security").info("onnx.hub.load patched — zero-trust active")
    except ImportError:
        pass  # onnx not installed, nothing to patch

class SecurityError(Exception):
    pass


# Apply the patch at import time so it takes effect before any other code
# that might call onnx.hub.load().
patch_onnx_security()
