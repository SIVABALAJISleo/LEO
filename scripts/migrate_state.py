import logging
from backend.core.middleware import redis_client
from backend.core.database import SessionLocal, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migration")

def migrate_redis_to_db():
    """
    Utility to migrate existing user tiers from Redis (volatile) to PostgreSQL (durable).
    Useful during the hyperscaler evolution to ensure no state is lost.
    """
    db = SessionLocal()
    try:
        # We only migrate users we know exist or have tier data for
        # In a real system, we'd scan Redis for 'user:*:tier' keys
        # For this implementation, we check if redis_client is functional
        if hasattr(redis_client, "_storage"):
            # Mock/FakeRedis case for local dev
            keys = [k for k in redis_client._storage.keys() if k.startswith("user:") and k.endswith(":tier")]
        else:
            # Genuine Redis case
            try:
                keys = redis_client.keys("user:*:tier")
            except:
                logger.warning("Could not scan Redis keys. Migration skipped.")
                return

        logger.info(f"Found {len(keys)} user tiers to migrate.")
        
        for key in keys:
            user_id = key.split(":")[1]
            tier = redis_client.get(key)
            
            # Check if user exists in DB
            user = db.query(User).filter(User.uid == user_id).first()
            if not user:
                logger.info(f"Creating durable user record for {user_id} with tier {tier}")
                user = User(uid=user_id, tier=tier)
                db.add(user)
            else:
                if user.tier != tier:
                    logger.info(f"Updating user {user_id} tier to {tier}")
                    user.tier = tier
        
        db.commit()
        logger.info("Migration complete.")
    except Exception as e:
        db.rollback()
        logger.error(f"Migration failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_redis_to_db()
