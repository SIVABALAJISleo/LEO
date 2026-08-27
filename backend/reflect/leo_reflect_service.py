"""
LEO Reflection & Meta-Learning Backend Service
Integrates Claude Reflect System with LEO v7 Engine for self-improving scalability.
"""

import sys
import os
import time
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add reflect scripts directory to sys.path
REFLECT_ROOT = Path(__file__).parent
SCRIPTS_DIR = REFLECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from learning_ledger import LearningLedger
    from meta_learning import log_feedback
    from semantic_detector import detect_semantic_signals
except ImportError:
    LearningLedger = None
    log_feedback = None
    detect_semantic_signals = None


class LeoReflectService:
    """
    Unified Reflection & Scalability Service for LEO Backend.
    
    Capabilities:
    1. Continuous signal extraction from query & execution traces.
    2. Persistent cross-session Learning Ledger (SQLite).
    3. Auto-promotion of repeated/corrected patterns directly into LEO semantic cache.
    4. Meta-learning analytics & productivity telemetry.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_dir = REFLECT_ROOT / ".state"
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path or (self.db_dir / "leo_learnings.db")
        
        if LearningLedger is not None:
            self.ledger = LearningLedger(db_path=self.db_path)
        else:
            self.ledger = None
            
        self._init_extended_schema()
        print(f"[REFLECT] LEO Reflect Service initialized (Ledger: {self.db_path.name})")

    def _init_extended_schema(self):
        """Ensure extended telemetry and reflection metrics tables exist."""
        conn = sqlite3.connect(self.db_path)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS query_reflections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                source TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                similarity REAL,
                response TEXT,
                corrected_response TEXT,
                promoted_to_cache INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS productivity_metrics (
                metric_key TEXT PRIMARY KEY,
                metric_value REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        conn.close()

    def record_query_trace(self, query: str, result: Dict[str, Any], feedback_score: float = 1.0) -> Dict[str, Any]:
        """
        Record query execution result and extract self-improvement signals.
        """
        source = result.get("source", "UNKNOWN")
        latency_ms = result.get("latency_ms", 0.0)
        similarity = result.get("similarity", 0.0)
        response = result.get("response", "")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO query_reflections (query, source, latency_ms, similarity, response)
            VALUES (?, ?, ?, ?, ?)
        """, (query, source, latency_ms, similarity, response[:500]))
        trace_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # If cache miss with high latency, register in ledger as candidate for pre-computed promotion
        learning_id = None
        if source == "LLM" and self.ledger is not None:
            learning_id = self.ledger.record_learning(
                content=f"FAQ Auto-Synthesis: {query} -> {response[:200]}",
                learning_type="cache_candidate",
                skill_name="leo_engine",
                confidence=0.85
            )
            
        return {
            "trace_id": trace_id,
            "learning_id": learning_id,
            "recorded": True,
            "source": source
        }

    def promote_to_cache(self, query: str, response: str, cache_file: Path = Path("leo_cache.json")) -> bool:
        """
        Promote a validated learning or query-response pair to permanent LEO semantic cache.
        """
        try:
            cache = {}
            if cache_file.exists():
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            
            clean_q = query.lower().strip()
            cache[clean_q] = response
            
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2)
                
            # Update reflection trace
            conn = sqlite3.connect(self.db_path)
            conn.execute("UPDATE query_reflections SET promoted_to_cache = 1 WHERE query LIKE ?", (f"%{query}%",))
            conn.commit()
            conn.close()
            
            print(f"[Reflect] Promoted '{query[:40]}...' to permanent semantic cache (0ms lookup)")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to promote to cache: {e}")
            return False

    def get_productivity_stats(self) -> Dict[str, Any]:
        """
        Calculate productivity metrics, compute savings, and cache hit acceleration.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total, AVG(latency_ms) as avg_lat FROM query_reflections")
        row = cursor.fetchone()
        total_queries = row["total"] if row else 0
        avg_latency = row["avg_lat"] if row and row["avg_lat"] else 0.0
        
        cursor.execute("SELECT COUNT(*) as cache_hits FROM query_reflections WHERE source = 'CACHE'")
        hits_row = cursor.fetchone()
        cache_hits = hits_row["cache_hits"] if hits_row else 0
        
        cursor.execute("SELECT COUNT(*) as promoted FROM query_reflections WHERE promoted_to_cache = 1")
        prom_row = cursor.fetchone()
        promoted = prom_row["promoted"] if prom_row else 0
        
        conn.close()
        
        hit_rate = (cache_hits / total_queries * 100) if total_queries > 0 else 0.0
        # Estimated time saved assuming LLM avg 1500ms vs Cache < 5ms
        time_saved_sec = (cache_hits * 1.495)
        
        return {
            "total_queries_analyzed": total_queries,
            "cache_hits": cache_hits,
            "cache_hit_rate_pct": round(hit_rate, 1),
            "avg_latency_ms": round(avg_latency, 2),
            "promoted_learnings": promoted,
            "estimated_compute_time_saved_sec": round(time_saved_sec, 2),
            "status": "HEALTHY_SCALING"
        }


# Global singleton instance
_reflect_service = None

def get_reflect_service() -> LeoReflectService:
    global _reflect_service
    if _reflect_service is None:
        _reflect_service = LeoReflectService()
    return _reflect_service


if __name__ == "__main__":
    service = get_reflect_service()
    # Test trace
    res = service.record_query_trace(
        query="How to configure automated backup?",
        result={"source": "CACHE", "latency_ms": 1.2, "similarity": 0.94, "response": "Use backup schedule cron."}
    )
    print("Test reflection trace recorded:", res)
    stats = service.get_productivity_stats()
    print("Productivity & Scalability Metrics:", json.dumps(stats, indent=2))
