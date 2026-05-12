import logging
from typing import Dict, Any
from backend.core.database import SessionLocal, Workspace

logger = logging.getLogger(__name__)

class SubscriptionManager:
    """
    Manages SaaS subscription tiers and enforces usage limits.
    Tiers: Free, Pro, Enterprise
    """
    TIERS = {
        "free": {"query_limit": 100, "storage_limit_mb": 50},
        "pro": {"query_limit": 5000, "storage_limit_mb": 5000},
        "enterprise": {"query_limit": 1000000, "storage_limit_mb": 1000000}
    }

    def get_tier_limits(self, tier: str) -> Dict[str, Any]:
        return self.TIERS.get(tier.lower(), self.TIERS["free"])

    def enforce_limits(self, tenant_id: str, daily_usage: int) -> bool:
        # In real prod, lookup tenant's tier from DB
        tier = "free" # Default
        limits = self.get_tier_limits(tier)
        
        if daily_usage >= limits["query_limit"]:
            logger.warning(f"limit_exceeded: tenant={tenant_id} usage={daily_usage}")
            return False
        return True

global_subscription_manager = SubscriptionManager()
