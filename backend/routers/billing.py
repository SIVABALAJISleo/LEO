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

    # Initialize Redis Client if Available
    from backend.core.middleware import redis_client
    
    event_id = event.get('id')
    
    # Duplicate Webhook Protection (Idempotency)
    if redis_client and event_id:
        is_new_event = redis_client.setnx(f"webhook_lock:{event_id}", "locked")
        if not is_new_event:
            logger.info(f"Duplicate Stripe Event Received and Ignored: {event_id}")
            return {"status": "success", "reason": "Already processed"}
        redis_client.expire(f"webhook_lock:{event_id}", 86400)
    
    # Handle the event
    try:
        if event['type'] == 'customer.subscription.created':
            subscription = event['data']['object']
            customer_id = subscription.get('customer')
            # For this MVP, we naively map the stripe customer as the user_id.
            if redis_client:
                # In real life, query DB to map Stripe Customer ID -> Internal User ID
                # We'll just assume they match or have a fallback for this snippet.
                redis_client.set(f"user:{customer_id}:tier", "pro")
            logger.info(f"Subscription Created: {subscription.get('id')} for Customer: {customer_id}")
            
        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            logger.info(f"Subscription Updated: {subscription.get('id')}")
            
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            customer_id = subscription.get('customer')
            if redis_client:
                redis_client.set(f"user:{customer_id}:tier", "free")
            logger.info(f"Subscription Canceled: {subscription.get('id')}")

        else:
            logger.debug(f"Unhandled Stripe Event: {event['type']}")
            
    except Exception as e:
        logger.error(f"Failed processing Stripe Webhooks into Redis state: {e}")

    return {"status": "success"}

@router.get("/config")
async def get_billing_config() -> Dict[str, Any]:
    """Provides the frontend with the public Stripe key for the checkout SDK."""
    pub_key = os.getenv("VITE_STRIPE_PUBLIC_KEY", "")
    return {
        "publishableKey": pub_key,
        "active": bool(pub_key)
    }
