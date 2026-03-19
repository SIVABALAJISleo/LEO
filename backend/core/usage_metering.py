"""
Usage Metering & Tier Limits
Enforces SaaS business rules for free/pro/enterprise users.
"""

class UsageMetering:
    TIERS = {
        "free": {"limit": 100, "priority": 3},
        "pro": {"limit": 1000, "priority": 2},
        "enterprise": {"limit": 999999, "priority": 1}
    }

    def __init__(self):
        self.usage_counters = {} # user_id -> int

    def check_limit(self, user_id: str, tier: str = "free") -> bool:
        current = self.usage_counters.get(user_id, 0)
        limit = self.TIERS.get(tier, self.TIERS["free"])["limit"]
        return current < limit

    def record_usage(self, user_id: str):
        self.usage_counters[user_id] = self.usage_counters.get(user_id, 0) + 1

    def get_tier_info(self, tier: str) -> dict:
        return self.TIERS.get(tier, self.TIERS["free"])

global_usage_meter = UsageMetering()
