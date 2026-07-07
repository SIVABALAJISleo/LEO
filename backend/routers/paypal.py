import os
import json
import logging
import httpx
from fastapi import APIRouter, Request, HTTPException, Header, Depends
from pydantic import BaseModel
from backend.core.security import verify_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/paypal", tags=["PayPal"])

# Load Secrets strictly from ENV
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", "")
PAYPAL_WEBHOOK_ID = os.getenv("PAYPAL_WEBHOOK_ID", "")
PAYPAL_API_BASE = os.getenv("PAYPAL_API_BASE", "https://api-m.sandbox.paypal.com")  # Use sandbox as default

async def get_paypal_access_token():
    """Retrieves an access token from PayPal for API authentication."""
    url = f"{PAYPAL_API_BASE}/v1/oauth2/token"
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
            data={"grant_type": "client_credentials"},
            headers={"Accept": "application/json", "Accept-Language": "en_US"}
        )
        if response.status_code != 200:
            logger.error(f"Failed to get PayPal access token: {response.text}")
            return None
        return response.json().get("access_token")

class CheckoutRequest(BaseModel):
    plan_id: str

@router.post("/checkout")
async def create_paypal_order(request: CheckoutRequest, token: dict = Depends(verify_token)):
    """Creates a PayPal order and returns the approval link."""
    user_id = token.get("uid") or token.get("sub", "anonymous")
    
    # Map plans to mocked values for now
    plan_prices = {
        "pro": "49.00",
        "heavy": "249.00"
    }
    
    price = plan_prices.get(request.plan_id, "49.00")
    
    access_token = await get_paypal_access_token()
    if not access_token:
        raise HTTPException(status_code=500, detail="PayPal config missing or auth failed")
        
    url = f"{PAYPAL_API_BASE}/v2/checkout/orders"
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "custom_id": user_id,
            "amount": {
                "currency_code": "USD",
                "value": price
            }
        }],
        "application_context": {
            "return_url": f"http://localhost:5173/dashboard?payment=success",
            "cancel_url": f"http://localhost:5173/dashboard?payment=cancelled"
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            },
            json=payload
        )
        
        if response.status_code not in (200, 201):
            logger.error(f"Failed to create PayPal order: {response.text}")
            raise HTTPException(status_code=500, detail="Could not create payment session")
            
        data = response.json()
        
        # Find the 'approve' link from the HATEOAS links provided by PayPal
        approval_url = next((link["href"] for link in data.get("links", []) if link["rel"] == "approve"), None)
        
        if not approval_url:
            raise HTTPException(status_code=500, detail="Missing approval link from PayPal")
            
        return {"url": approval_url, "order_id": data.get("id")}

@router.post("/webhook")
async def paypal_webhook(
    request: Request,
    paypal_transmission_id: str = Header(None, alias="PAYPAL-TRANSMISSION-ID"),
    paypal_transmission_time: str = Header(None, alias="PAYPAL-TRANSMISSION-TIME"),
    paypal_cert_url: str = Header(None, alias="PAYPAL-CERT-URL"),
    paypal_auth_algo: str = Header(None, alias="PAYPAL-AUTH-ALGO"),
    paypal_transmission_sig: str = Header(None, alias="PAYPAL-TRANSMISSION-SIG"),
):
    """
    Listens for PayPal payment events and verifies their cryptographic signature.
    """
    if not all([PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_WEBHOOK_ID]):
        logger.warning("PayPal Webhook configuration incomplete. Ignoring.")
        return {"status": "ignored", "reason": "unconfigured"}

    # SECTION 1: Capture Raw Request Data
    body_bytes = await request.body()
    try:
        event = json.loads(body_bytes)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    # SECTION 2: Verify PayPal Webhook Signature
    access_token = await get_paypal_access_token()
    if not access_token:
         raise HTTPException(status_code=500, detail="Authentication with PayPal failed")

    verify_url = f"{PAYPAL_API_BASE}/v1/notifications/verify-webhook-signature"
    verification_payload = {
        "transmission_id": paypal_transmission_id,
        "transmission_time": paypal_transmission_time,
        "cert_url": paypal_cert_url,
        "auth_algo": paypal_auth_algo,
        "transmission_sig": paypal_transmission_sig,
        "webhook_id": PAYPAL_WEBHOOK_ID,
        "webhook_event": event
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            verify_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            },
            json=verification_payload
        )
        
        if response.status_code != 200:
            logger.error(f"PayPal Signature Verification Request Failed: {response.text}")
            raise HTTPException(status_code=400, detail="Signature verification failed")

        verification_result = response.json()
        if verification_result.get("verification_status") != "SUCCESS":
            # SECTION 3: Reject Invalid Events
            logger.warning(f"PayPal Webhook Signature Verification FAILED: {verification_result}")
            raise HTTPException(status_code=400, detail="Invalid signature")

    # SECTION 4: Process Valid Events
    from backend.core.middleware import redis_client
    from backend.core.database import SessionLocal, User, Subscription
    
    event_id = event.get("id")
    event_type = event.get("event_type")
    resource = event.get("resource", {})
    
    # Duplicate Webhook Protection (Idempotency via Redis)
    if redis_client and event_id:
        is_new_event = redis_client.setnx(f"webhook_lock:{event_id}", "locked")
        if not is_new_event:
            logger.info(f"Duplicate PayPal Event Received and Ignored: {event_id}")
            return {"status": "success", "reason": "Already processed"}
        redis_client.expire(f"webhook_lock:{event_id}", 86400)
    
    logger.info(f"Verified PayPal Event Received: {event_type} [{event_id}]")

    db = SessionLocal()
    try:
        user_id_str = resource.get("custom_id") or resource.get("subscriber", {}).get("custom_id")
        
        if not user_id_str or user_id_str == "anonymous":
            logger.warning(f"PayPal event {event_type} received but no valid user_id found")
            return {"status": "success", "reason": "No user ID"}

        # Sync with Database (Source of Truth)
        user = db.query(User).filter(User.uid == user_id_str).first()
        if not user:
            # Create user if missing
            user = User(uid=user_id_str, tier="free")
            db.add(user)
            db.flush()

        if event_type in ["PAYMENT.SALE.COMPLETED", "CHECKOUT.ORDER.APPROVED", "BILLING.SUBSCRIPTION.ACTIVATED"]:
            user.tier = "pro" # type: ignore
            # Record subscription
            sub = Subscription(user_id=user.id, paypal_order_id=resource.get("id"), status="active")
            db.add(sub)
            logger.info(f"User {user_id_str} upgraded to PRO in Database")
            
            # Sync to Redis (Caching Layer)
            if redis_client:
                redis_client.set(f"user:{user_id_str}:tier", "pro")
            
        elif event_type == "BILLING.SUBSCRIPTION.CANCELLED":
            user.tier = "free" # type: ignore
            logger.info(f"User {user_id_str} downgraded to FREE in Database")
            if redis_client:
                redis_client.set(f"user:{user_id_str}:tier", "free")

        db.commit()
    except Exception as e:
        db.rollback()
        # SECTION 5: Secure the Endpoint (Exception Handling)
        logger.error(f"Failed processing PayPal Webhook into Database state: {e}")
    finally:
        db.close()

    return {"status": "success"}
