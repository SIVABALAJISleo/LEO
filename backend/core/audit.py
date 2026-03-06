import logging
import json
import time
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger("hyper.audit")

class ImmutableAuditLog:
    """
    Hyperscaler Compliance: Append-only WORM (Write Once Read Many) analog.
    In production, this streams directly to an S3 bucket with Object Lock enabled
    or a dedicated SIEM (Security Information and Event Management) system like Splunk.
    """
    
    def __init__(self, log_path: str = "/tmp/hyper_audit.log"):
        self.log_path = log_path
        
    def _generate_record_hash(self, payload: Dict[str, Any], previous_hash: str) -> str:
        """Creates a chained cryptographic hash for immutability verification."""
        data_string = json.dumps(payload, sort_keys=True) + previous_hash
        return hashlib.sha256(data_string.encode('utf-8')).hexdigest()

    def record_event(
        self, 
        event_type: str, 
        actor_id: str, 
        resource: str, 
        action: str, 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Records a compliance-grade audit event.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Simulate retrieving the last hash from the ledger (simplified for demo)
        previous_hash = "genesis_hash_000000000" 
        
        payload = {
            "timestamp": timestamp,
            "event_type": event_type,
            "actor_id": actor_id,
            "resource": resource,
            "action": action,
            "metadata": metadata or {}
        }
        
        record_hash = self._generate_record_hash(payload, previous_hash)
        
        audit_entry = {
            **payload,
            "record_hash": record_hash,
            "previous_hash": previous_hash
        }
        
        # In a real environment, this goes via Kinesis/Kafka to cold storage
        try:
            with open(self.log_path, 'a') as f:
                f.write(json.dumps(audit_entry) + '\n')
            logger.info(f"Audit log recorded: {event_type} by {actor_id}")
        except Exception as e:
            logger.critical(f"FAILED TO WRITE AUDIT LOG: {e}")
            # If audit logging fails, standard enterprise policy dictates halting the transaction
            raise SystemError("Compliance constraint: Audit logging unavailable.")

audit_logger = ImmutableAuditLog()
