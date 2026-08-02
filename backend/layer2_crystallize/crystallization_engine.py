"""
backend/layer2_crystallize/crystallization_engine.py
Aggressive crystallization pipeline. Clusters query traces to proactively compile
canonical templates during idle times.
"""
import re
import time
import logging
from typing import List, Dict, Any, Optional

from backend.layer2_crystallize.crystallizer import TraceCompiler

logger = logging.getLogger(__name__)

class CrystalCompiler(TraceCompiler):
    """
    Extends TraceCompiler with automated clustering and jinja-style parameterization.
    """
    def __init__(self, db_path: str = "hyper_engine.db"):
        super().__init__(db_path)
        self.intent_templates = {}

    def cluster_and_compile_idle(self) -> int:
        """
        Runs during system idle times (dream state).
        Identifies high-frequency query structures, compiles template placeholders,
        and saves them.
        """
        logger.info("Beginning idle crystallization cycle...")
        # Mine queries and compile slots
        count = self.crystallize_frequent_patterns(min_hits=2)
        logger.info(f"Idle crystallization cycle complete. Compiled {count} new shortcuts.")
        return count

    def render_shortcut(self, shortcut: Dict[str, Any], raw_query: str) -> str:
        """
        Fills dynamic variables from a matched query into the crystallized template.
        """
        template = shortcut.get("response", "")
        variables = shortcut.get("variables", [])
        
        # Simple placeholder replacement (e.g. {company} or {0})
        rendered = template
        for i, var in enumerate(variables):
            rendered = rendered.replace(f"{{{i}}}", var)
            
        return rendered
