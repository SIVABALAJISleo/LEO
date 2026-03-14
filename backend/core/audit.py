import structlog
import time
from typing import Dict, Any, Optional

# Structured logger for security-critical events
audit_logger = structlog.get_logger("audit")

class AuditLogger:
    """
    SaaS Security Layer:
    Provides standardized, immutable-style audit logging for compliance.
    """
    @staticmethod
    def log_event(
        action: str,
        user_id: str,
        tenant_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        status: str = "success",
        ip_address: str = "internal"
    ):
        """
        Logs a security-significant event with full context.
        """
        audit_logger.info(
            "audit_event",
            action=action,
            user_id=user_id,
            tenant_id=tenant_id,
            status=status,
            ip_address=ip_address,
            timestamp=time.time(),
            **(metadata or {})
        )

# Global utility instance
audit = AuditLogger()
