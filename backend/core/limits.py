# SaaS Tiers and Limits
TIER_LIMITS = {
    "free": {
        "requests_per_day": 10,
        "storage_mb": 50,
        "concurrent_jobs": 1
    },
    "pro": {
        "requests_per_day": 500,
        "storage_mb": 2000,
        "concurrent_jobs": 5
    },
    "enterprise": {
        "requests_per_day": 10000, # Effectively unlimited for most
        "storage_mb": 100000,
        "concurrent_jobs": 20
    }
}
