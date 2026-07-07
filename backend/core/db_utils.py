import sqlite3

def get_concurrent_db_connection(db_path: str) -> sqlite3.Connection:
    """
    Creates a highly concurrent SQLite connection.
    - check_same_thread=False allows FastAPI threads to share the connection.
    - timeout=15.0 gracefully waits for locks instead of throwing OperationalError.
    - PRAGMA journal_mode=WAL enables simultaneous readers and a writer.
    """
    conn = sqlite3.connect(db_path, check_same_thread=False, timeout=15.0)
    
    # Enable WAL mode for high concurrency
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    
    return conn
