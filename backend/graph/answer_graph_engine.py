"""
Answer Graph Engine (AGE)
Core engine that matches new queries to stored reasoning patterns
and returns reused answers without model calls.
Expands Layer 4 with Source-Document cache invalidation.
"""
import logging
import sqlite3
from typing import Optional, Dict, Any, List
from backend.core.db_utils import get_concurrent_db_connection

logger = logging.getLogger(__name__)

class AnswerGraphEngine:
    """
    Manages the dependency graph between source documents and crystallized answers.
    When a source document is updated, invalidates only the affected answers.
    """

    def __init__(self, db_path: str = "hyper_engine.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = get_concurrent_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS answer_sources (
                trace_id TEXT,
                source_doc_id TEXT,
                PRIMARY KEY (trace_id, source_doc_id)
            )
        """)
        conn.commit()
        conn.close()

    def register_answer_sources(self, trace_id: str, source_doc_ids: List[str]):
        """
        Maps a crystallized answer (trace_id) to the documents used to generate it.
        """
        if not source_doc_ids:
            return
            
        conn = get_concurrent_db_connection(self.db_path)
        cursor = conn.cursor()
        try:
            for doc_id in source_doc_ids:
                cursor.execute("""
                    INSERT OR IGNORE INTO answer_sources (trace_id, source_doc_id)
                    VALUES (?, ?)
                """, (trace_id, doc_id))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to register answer sources: {e}")
        finally:
            conn.close()

    def invalidate_by_document(self, source_doc_id: str):
        """
        When a document changes, invalidate all cached answers that relied on it.
        """
        conn = get_concurrent_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT trace_id FROM answer_sources WHERE source_doc_id = ?", (source_doc_id,))
        rows = cursor.fetchall()
        
        if rows:
            trace_ids = [row[0] for row in rows]
            logger.info(f"Document {source_doc_id} changed. Invalidating {len(trace_ids)} crystallized answers.")
            
            # Remove from semantic cache
            from backend.crystallization.crystallizer import SemanticCrystallizer
            crystallizer = SemanticCrystallizer(self.db_path)
            
            for trace_id in trace_ids:
                crystallizer.invalidate_trace(trace_id)
                cursor.execute("DELETE FROM answer_sources WHERE trace_id = ?", (trace_id,))
            conn.commit()
            
        conn.close()

global_age = AnswerGraphEngine()
