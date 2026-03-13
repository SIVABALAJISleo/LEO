import asyncio
import os
import sys

# Add backend to path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.audit import audit_logger
from backend.tasks.compliance_tasks import gather_user_data_task, purge_user_data_task

def run_compliance_dry_run():
    print("Simulating GDPR / SOC2 Pipeline Execution...")
    
    # 1. Simulate an authenticated user requesting data export
    print("-> Triggering GDPR Article 20 Request (Data Portability)")
    audit_logger.record_event(
        event_type="DATA_ACCESS",
        actor_id="user_8910",
        resource="user_data:user_8910",
        action="EXPORT_REQUESTED",
        metadata={"reason": "Customer triggered export via UI"}
    )
    
    # 2. Simulate Celery Worker compiling it
    gather_user_data_task("user_8910")
    
    # 3. Simulate a user requesting right to be forgotten
    print("-> Triggering GDPR Article 17 Request (Right to Erasure)")
    audit_logger.record_event(
        event_type="DATA_DESTRUCTION",
        actor_id="user_8910",
        resource="user_data:user_8910",
        action="ERASURE_REQUESTED"
    )
    
    # 4. Simulate Celery Worker purging the database & S3
    purge_user_data_task("user_8910")
    
    print("✅ Compliance dry-run complete. Events serialized to immutable log.")

if __name__ == "__main__":
    run_compliance_dry_run()
