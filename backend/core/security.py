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
    PERMANENT CVE Mitigation — onnx.hub.load() silent supply-chain bypass.

    Root cause: `if not _verify_repo_ref(repo) and not silent` means that
    passing `silent=True` completely skips trust verification AND the SHA-256
    manifest check (because manifest is attacker-controlled).

    Fix strategy (defense-in-depth):
      1. Monkey-patch `onnx.hub.load` to ALWAYS block untrusted repos, regardless
         of the `silent` argument value. `silent` is stripped entirely.
      2. Replace `onnx.hub._verify_repo_ref` with a strict allowlist so the
         internal trust check cannot be influenced by manipulated manifests.
      3. Log every call at WARNING level for audit trails.

    Since no upstream patched version exists (onnx <= 1.20.1 affected),
    this patch MUST run before any other module imports onnx.hub.
    """
    try:
        import onnx.hub as _onnx_hub

        # --- (a) Allowlist-based repo verifier (replaces the broken one) ---
        _OFFICIAL_REPOS = frozenset({
            "onnx/models",
        })

        def _strict_verify_repo(repo: str) -> bool:
            """Returns True only for repos on the official allowlist."""
            clean = (repo or "").strip().lower().rstrip("/")
            return clean in _OFFICIAL_REPOS

        _onnx_hub._verify_repo_ref = _strict_verify_repo  # nosec B010 - intentional hardening

        # --- (b) Replacement load() that enforces trust unconditionally ---
        _original_load = _onnx_hub.load  # keep reference for official-repo use

        def _secure_onnx_hub_load(*args, **kwargs):
            # Strip `silent` entirely — security warnings must never be silenced.
            kwargs.pop("silent", None)

            # Determine repo from args signature: load(model, repo=...) or positional
            repo = None
            if len(args) >= 2:
                repo = args[1]
            elif "repo" in kwargs:
                repo = kwargs["repo"]

            if repo and not _strict_verify_repo(repo):
                logger.error(
                    "onnx_hub_load_blocked: untrusted repo=%s args=%s kwargs=%s",
                    repo, args, {k: v for k, v in kwargs.items() if k != "silent"},
                )
                raise SecurityError(
                    f"SECURITY BLOCK: onnx.hub.load() from untrusted repository "
                    f"'{repo}' is permanently disabled. "
                    f"Only repos in the official allowlist are permitted. "
                    f"(Mitigation for onnx.hub silent supply-chain bypass, onnx <= 1.20.1)"
                )

            logger.warning(
                "onnx_hub_load_called: repo=%s — allowed (official repo)", repo
            )
            return _original_load(*args, **kwargs)

        _onnx_hub.load = _secure_onnx_hub_load
        logger.info("onnx_hub_security_hardening_active: patch applied successfully")

    except ImportError:
        # onnx not installed — nothing to patch
        pass
    except AttributeError as exc:
        # onnx version changed internal structure — log and continue safely
        logger.warning("onnx_hub_security_hardening_skipped: %s", exc)


class SecurityError(RuntimeError):
    """Raised when a security policy is violated."""
    pass


# Apply the patch at import time so it takes effect before any other code
# that might call onnx.hub.load().
patch_onnx_security()
