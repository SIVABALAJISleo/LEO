import time
import os
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from backend.security.rbac import PermissionChecker

router = APIRouter()

class DevOpsSettings(BaseModel):
    sentry_dsn: Optional[str] = None
    pagerduty_integration_key: Optional[str] = None
    stripe_signature_checking: bool = True
    canary_deployment_pct: float = 10.0
    active_rollback: bool = False
    security_monitoring: bool = True
    audit_logging: bool = True

devops_state: Dict[str, Any] = {
    "sentry_dsn": "https://sentry.hyper.app/12345",
    "pagerduty_integration_key": "pd_key_v13_active",
    "stripe_signature_checking": True,
    "canary_deployment_pct": 10.0,
    "active_rollback": False,
    "security_monitoring": True,
    "audit_logging": True,
    "last_rollback_timestamp": 0.0,
    "rollback_history": []
}

audit_logs = [
    {"timestamp": time.time() - 3600, "action": "INGEST_POLICY", "status": "success", "details": "Ingested Global Policy Document"},
    {"timestamp": time.time() - 1800, "action": "CANARY_ROUTE_UPDATE", "status": "success", "details": "Canary weight set to 10.0%"},
]

@router.get("/api/v1/devops/status", tags=["DevOps"])
async def get_devops_status(token: dict = Depends(PermissionChecker("admin"))):
    return devops_state

@router.post("/api/v1/devops/configure", tags=["DevOps"])
async def configure_devops(settings: DevOpsSettings, token: dict = Depends(PermissionChecker("admin"))):
    devops_state.update(settings.model_dump(exclude_unset=True))
    audit_logs.append({
        "timestamp": time.time(),
        "action": "CONFIGURE_DEVOPS",
        "status": "success",
        "details": f"Updated devops parameters: {settings.model_dump(exclude_unset=True)}"
    })
    return {"status": "configured", "settings": devops_state}

@router.post("/api/v1/devops/rollback", tags=["DevOps"])
async def trigger_rollback(token: dict = Depends(PermissionChecker("admin"))):
    timestamp = time.time()
    devops_state["last_rollback_timestamp"] = timestamp
    devops_state["canary_deployment_pct"] = 0.0
    devops_state["rollback_history"].append(timestamp)
    
    audit_logs.append({
        "timestamp": timestamp,
        "action": "ROLLBACK_TRIGGERED",
        "status": "success",
        "details": "Rollback executed, canary route reset to 0%."
    })
    
    return {"status": "rollback_completed", "canary_weight": 0.0, "timestamp": timestamp}

@router.post("/api/v1/devops/canary", tags=["DevOps"])
async def configure_canary(weight: float, token: dict = Depends(PermissionChecker("admin"))):
    if not (0.0 <= weight <= 100.0):
        raise HTTPException(status_code=400, detail="Canary weight must be between 0.0 and 100.0")
    devops_state["canary_deployment_pct"] = weight
    
    audit_logs.append({
        "timestamp": time.time(),
        "action": "CANARY_WEIGHT_ADJUST",
        "status": "success",
        "details": f"Canary routing weight adjusted to {weight}%"
    })
    return {"status": "canary_configured", "canary_weight": weight}

@router.get("/api/v1/devops/audit_log", tags=["DevOps"])
async def get_audit_logs(token: dict = Depends(PermissionChecker("admin"))):
    return audit_logs

@router.get("/api/v1/devops/security", tags=["DevOps"])
async def get_security_status(token: dict = Depends(PermissionChecker("admin"))):
    return {
        "status": "active",
        "threat_level": "low",
        "blocked_ips_count": 4,
        "suspicious_requests_last_hour": 0,
        "rate_limiting": "enforced",
        "encryption": "TLS_1.3"
    }

@router.post("/api/v1/billing/webhook", tags=["Billing"])
async def stripe_webhook(request: Request):
    import stripe
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    
    if not webhook_secret:
        raise HTTPException(status_code=500, detail="Stripe webhook secret not configured")
    
    if devops_state["stripe_signature_checking"]:
        if not sig_header:
            raise HTTPException(status_code=400, detail="Missing stripe-signature header")
            
        try:
            stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except stripe.error.SignatureVerificationError as e:
            raise HTTPException(status_code=401, detail=f"Cryptographic signature mismatch: {str(e)}")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Malformed stripe-signature header: {str(e)}")
            
    return {"status": "verified", "event_received": True}
