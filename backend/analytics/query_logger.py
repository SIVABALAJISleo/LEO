import logging
from backend.core.database import SessionLocal, UsageLog

logger = logging.getLogger(__name__)

class QueryLogger:
    """
    Subsystem for high-performance structured logging of user queries.
    Powers PPE pattern mining, Shadow prediction, and Billing.
    """
    def log(self, 
            workspace_id: str, 
            user_id: str, 
            query: str, 
            answer: str, 
            response_type: str, 
            latency_ms: int,
            inference_used: bool):
        
        db = SessionLocal()
        try:
            log_entry = UsageLog(
                workspace_id=workspace_id,
                user_id=user_id,
                query=query,
                answer=answer,
                response_type=response_type,
                latency_ms=latency_ms,
                inference_used=inference_used
            )
            db.add(log_entry)
            db.commit()
            logger.info(f"query_logged: {workspace_id} type={response_type}")
        except Exception as e:
            logger.error(f"query_logging_failed: {e}")
            db.rollback()
        finally:
            db.close()

global_query_logger = QueryLogger()
