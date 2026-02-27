from fastapi import APIRouter, Depends, Request, Header
from hyper_saas.backend.core.security import verify_firebase_token
from hyper_saas.backend.core.stripe_service import stripe_service
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])

class CheckoutRequest(BaseModel):
    plan_id: str

@router.post("/checkout")
async def create_checkout_session(request: CheckoutRequest, token: dict = Depends(verify_firebase_token)):
    user_id = token.get("uid")
    email = token.get("email")
    return await stripe_service.create_checkout_session(user_id, email, request.plan_id)

@router.post("/portal")
async def create_portal_session(token: dict = Depends(verify_firebase_token)):
    # In a real app, we'd lookup the stripe_customer_id for this user_id
    # For now, we assume user_metadata contains it or handle first-time
    customer_id = token.get("stripe_customer_id", "cus_default_mock")
    return await stripe_service.create_billing_portal_session(customer_id)

@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()
    return stripe_service.handle_webhook(payload.decode("utf-8"), stripe_signature)
