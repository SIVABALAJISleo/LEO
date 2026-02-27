import os
from typing import Optional
from fastapi import HTTPException

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    print("Warning: stripe module not found. Billing will operate in MOCK mode.")

# Initialize Stripe
if STRIPE_AVAILABLE:
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
else:
    WEBHOOK_SECRET = "mock_secret"

class StripeService:
    @staticmethod
    async def create_checkout_session(user_id: str, email: str, plan_id: str):
        """Creates a Stripe Checkout Session for a subscription."""
        # Map plan IDs to Stripe Price IDs (these should be in .env)
        price_map = {
            "pro": os.getenv("STRIPE_PRICE_ID_PRO"),
            "heavy": os.getenv("STRIPE_PRICE_ID_HEAVY"),
        }
        
        price_id = price_map.get(plan_id)
        if not price_id:
            raise HTTPException(status_code=400, detail=f"Invalid plan ID: {plan_id}")

        try:
            session = stripe.checkout.Session.create(
                customer_email=email,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=os.getenv("FRONTEND_URL", "http://localhost:8080") + "/billing/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=os.getenv("FRONTEND_URL", "http://localhost:8080") + "/billing/pricing",
                metadata={
                    'user_id': user_id,
                    'plan_id': plan_id
                }
            )
            return {"url": session.url}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def create_billing_portal_session(customer_id: str):
        """Creates a Stripe Customer Portal session for managing subscriptions."""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=os.getenv("FRONTEND_URL", "http://localhost:8080") + "/billing",
            )
            return {"url": session.url}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def handle_webhook(payload: str, sig_header: str):
        """Handles Stripe webhooks."""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, WEBHOOK_SECRET
            )
        except ValueError as e:
            # Invalid payload
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            raise HTTPException(status_code=400, detail="Invalid signature")

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            # Update user's subscription in DB (Supabase or local)
            print(f"Checkout completed for user {session.get('metadata', {}).get('user_id')}")
            # TODO: Call persistence layer to update user's plan
            
        elif event['type'] == 'invoice.paid':
            # Handle successful payment
            pass
            
        elif event['type'] == 'customer.subscription.deleted':
            # Handle cancellation
            pass

        return {"status": "success"}

stripe_service = StripeService()
