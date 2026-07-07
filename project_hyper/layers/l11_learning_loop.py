import sqlite3
from backend.core.db_utils import get_concurrent_db_connection

class LearningLoop:
    """
    Layer 9: Learning Loop
    Stores query/response pairs to improve future performance.
    """
    def __init__(self, db_path: str = "project_hyper/data/learning.db"):
        self.conn = get_concurrent_db_connection(db_path)
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY,
                query TEXT,
                response TEXT,
                trace TEXT,
                latency REAL
            )
        """)
        self.conn.commit()

    def record(self, query: str, response: str, trace: str, latency: float):
        self.conn.execute(
            "INSERT INTO audit_log (query, response, trace, latency) VALUES (?, ?, ?, ?)",
            (query, response, trace, latency)
        )
        self.conn.commit()

if __name__ == "__main__":
    loop = LearningLoop()
    loop.record("Test", "Response", "L0->L1", 0.05)
