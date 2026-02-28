import os
import stripe
import logging
from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Dict, Any

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/billing", tags=["Billing"])

# Load Secrets strictly from ENV
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

stripe.api_key = STRIPE_SECRET_KEY

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Listens for active Stripe Subscription updates to bind user quotas.
    """
    if not STRIPE_WEBHOOK_SECRET:
         logger.warning("Stripe Webhook Secret not configured. Ignoring webhook.")
         return {"status": "ignored", "reason": "unconfigured"}
         
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid Stripe Webhook Payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid Stripe Webhook Signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event['type'] == 'customer.subscription.created':
        subscription = event['data']['object']
        logger.info(f"Subscription Created: {subscription.get('id')} for Customer: {subscription.get('customer')}")
        # Phase 8: Here we would trigger Supabase to set the user tier to PRO/HEAVY
        
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        logger.info(f"Subscription Updated: {subscription.get('id')}")
        
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        logger.info(f"Subscription Canceled: {subscription.get('id')}")
        # Phase 8: Downgrade user to FREE tier in Supabase

    else:
        logger.debug(f"Unhandled Stripe Event: {event['type']}")

    return {"status": "success"}

@router.get("/config")
async def get_billing_config() -> Dict[str, Any]:
    """Provides the frontend with the public Stripe key for the checkout SDK."""
    pub_key = os.getenv("VITE_STRIPE_PUBLIC_KEY", "")
    return {
        "publishableKey": pub_key,
        "active": bool(pub_key)
    }
