"""
backend/crystallization/crystallizer.py
Reasoning trace crystallization compiler (Tier 5).
Converts repeated neural reasoning traces into deterministic symbolic shortcuts, FSM rules,
and lookups to permanently minimize GPU computation costs.
"""
import re
import sqlite3
import logging
from typing import Dict, Any, List, Optional, Tuple
import os

logger = logging.getLogger(__name__)

class TraceCompiler:
    """
    Analyzes historical query execution traces, identifies repeated structural patterns,
    and compiles them into deterministic rule-based shortcuts.
    """

    def __init__(self, db_path: str = "hyper_engine.db"):
        self.db_path = db_path
        self._initialize_sqlite()

    @property
    def _decisions(self):
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM compiled_shortcuts")
            count = cursor.fetchone()[0]
            conn.close()
            return [None] * count
        except Exception:
            return []


    def _initialize_sqlite(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table to store raw logs of neural reasoning passes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reasoning_traces (
                trace_id TEXT PRIMARY KEY,
                query TEXT,
                response TEXT,
                workload_class TEXT,
                latency_ms REAL,
                timestamp REAL
            )
        """)

        # Table for compiled shortcuts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compiled_shortcuts (
                shortcut_id TEXT PRIMARY KEY,
                pattern_regex TEXT,
                response_template TEXT,
                variable_keys TEXT,
                hit_count INTEGER DEFAULT 0,
                created_at REAL
            )
        """)
        
        conn.commit()
        conn.close()

    def record_trace(self, trace_id: str, query: str, response: str, w_class: str, latency: float):
        """Records an execution trace from the orchestrator for off-peak crystallization review."""
        import time
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO reasoning_traces (trace_id, query, response, workload_class, latency_ms, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (trace_id, query, response, w_class, latency, time.time()))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to record reasoning trace: {e}")
        finally:
            conn.close()

    def _find_slots(self, texts: List[str]) -> Tuple[str, List[str]]:
        """
        Extracts variable slots from a list of structurally similar text queries.
        Ex: ["approve user sivabalaji", "approve user alpha"] -> ("approve user (.*)", ["sivabalaji", "alpha"])
        """
        if not texts:
            return "", []

        # Split into tokens
        tokenized = [t.lower().split() for t in texts]
        min_len = min(len(t) for t in tokenized)
        
        pattern_tokens = []
        variable_indices = []

        for i in range(min_len):
            words_at_i = [t[i] for t in tokenized]
            if len(set(words_at_i)) == 1:
                # Constant token
                pattern_tokens.append(words_at_i[0])
            else:
                # Variable slot
                pattern_tokens.append("(.*)")
                variable_indices.append(i)

        pattern_regex = "^" + " ".join(pattern_tokens) + "$"
        return pattern_regex, variable_indices

    def crystallize_frequent_patterns(self, min_hits: int = 2) -> int:
        """
        Scans all reasoning traces, groups structurally identical pathways,
        and compiles them into deterministic rule sets in SQLite.
        """
        import time
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT query, response FROM reasoning_traces")
        traces = cursor.fetchall()
        
        if len(traces) < min_hits:
            conn.close()
            return 0

        # Group by simple token structures
        structure_groups: Dict[str, List[Tuple[str, str]]] = {}
        for query, response in traces:
            # Mask out dynamic values like numbers/names
            masked = re.sub(r"\d+", "[NUM]", query.lower())
            words = masked.split()
            # Generate a structural signature key
            sig = f"{len(words)}_{'_'.join([w for w in words if w.startswith('[')])}"
            if sig not in structure_groups:
                structure_groups[sig] = []
            structure_groups[sig].append((query, response))

        compiled_count = 0

        for sig, group in structure_groups.items():
            if len(group) >= min_hits:
                queries = [item[0] for item in group]
                responses = [item[1] for item in group]
                
                # Check if responses are structurally similar or constant
                # If they are constant or simple templates, we compile them
                if len(set(responses)) == 1:
                    pattern_regex, var_indices = self._find_slots(queries)
                    if pattern_regex and "(.*)" in pattern_regex:
                        shortcut_id = f"shortcut_{hash(pattern_regex) & 0xffffffff}"
                        var_keys_str = ",".join([str(idx) for idx in var_indices])
                        
                        cursor.execute("""
                            INSERT OR REPLACE INTO compiled_shortcuts (shortcut_id, pattern_regex, response_template, variable_keys, created_at)
                            VALUES (?, ?, ?, ?, ?)
                        """, (shortcut_id, pattern_regex, responses[0], var_keys_str, time.time()))
                        compiled_count += 1
                        logger.info(f"Crystallized pattern compiled: '{pattern_regex}' -> '{responses[0][:40]}...'")

        conn.commit()
        conn.close()
        return compiled_count

    def match_shortcut(self, query: str) -> Optional[Dict[str, Any]]:
        """Compares incoming queries directly against crystallized FSM shortcuts to bypass neural loops."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT shortcut_id, pattern_regex, response_template, variable_keys FROM compiled_shortcuts")
        shortcuts = cursor.fetchall()
        
        clean_query = query.lower().strip()
        
        for shortcut_id, pattern, template, var_keys in shortcuts:
            match = re.match(pattern, clean_query)
            if match:
                # Capture variables
                variables = match.groups()
                # Track hit metrics
                cursor.execute("UPDATE compiled_shortcuts SET hit_count = hit_count + 1 WHERE shortcut_id = ?", (shortcut_id,))
                conn.commit()
                conn.close()
                
                return {
                    "shortcut_id": shortcut_id,
                    "response": template,
                    "variables": variables,
                    "method": "crystallized_shortcut"
                }

        conn.close()
        return None
