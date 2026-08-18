"""Database security utilities for safe parameterized queries."""
from typing import Any, Dict, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.engine import CursorResult


def safe_query(
    db: Session,
    query_str: str,
    params: Optional[Dict[str, Any]] = None
) -> CursorResult:
    """
    Execute parameterized queries to prevent SQL injection vulnerabilities.

    Example usage:
        safe_query(db, "SELECT * FROM users WHERE id = :id", {"id": user_id})
    """
    stmt = text(query_str)
    return db.execute(stmt, params or {})
