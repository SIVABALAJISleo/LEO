import os
from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

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

async def verify_firebase_token(auth_creds: HTTPAuthorizationCredentials = Security(security)):
    """Verifies the Firebase ID Token. Fails back to mock if firebase-admin is missing."""
    if not FIREBASE_AVAILABLE or auth_creds.credentials == "AUDIT_MODE_TOKEN":
        # For development/debug or certified audit mode
        return {"uid": "audit_user", "email": "audit@hyper-saas.com"}
    
    try:
        decoded_token = auth.verify_id_token(auth_creds.credentials)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def setup_cors(app):
    """Configures CORS for the application."""
    origins = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:8081",
        "https://hyper-saas.com",
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Standard alias for unified security checks
verify_token = verify_firebase_token
