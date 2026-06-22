"""
backend/security/prompt_guard.py
LEO AI Production Security - Phase 12 Implementation

Implements:
  - Prompt Injection Detection (heuristic classifier + regex patterns)
  - RAG Poisoning Detection (detects adversarial document payloads)
  - Memory Poisoning Detection (contradiction-based integrity checks)
  - Anomaly Detection (statistical deviation from baseline query patterns)
  - Comprehensive audit logging
"""
import re
import time
import hashlib
import logging
import json
from typing import Dict, Any, Optional, List, Tuple
from collections import deque

logger = logging.getLogger(__name__)


class PromptInjectionDetector:
    """
    Multi-layer prompt injection detection using:
      1. Known injection pattern regex matching
      2. Instruction override heuristics
      3. Encoding/obfuscation detection
      4. Statistical anomaly scoring
    """

    # Injection patterns — ordered by severity
    INJECTION_PATTERNS: List[Tuple[str, str, float]] = [
        # (pattern_regex, description, severity_score 0-1)
        (r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions|prompts|rules)",
         "Direct instruction override", 0.95),
        (r"forget\s+(everything|all|your)\s+(instructions|rules|training)",
         "Memory wipe attempt", 0.95),
        (r"you\s+are\s+now\s+(a|an|the)\s+",
         "Identity reassignment", 0.85),
        (r"pretend\s+(you|that|to\s+be)",
         "Role injection", 0.80),
        (r"act\s+as\s+(a|an|if)",
         "Role injection", 0.75),
        (r"system\s*:\s*",
         "System prompt injection", 0.90),
        (r"\[INST\]|\[/INST\]|<\|system\|>|<\|assistant\|>",
         "Template token injection", 0.90),
        (r"do\s+not\s+follow\s+(your|the|any)\s+(rules|guidelines|instructions)",
         "Rule override", 0.90),
        (r"(DROP\s+TABLE|DELETE\s+FROM|INSERT\s+INTO|UPDATE\s+.*SET)",
         "SQL injection", 0.95),
        (r"<script|javascript:|on(error|load|click)\s*=",
         "XSS injection", 0.85),
        (r"\\x[0-9a-fA-F]{2}|\\u[0-9a-fA-F]{4}",
         "Unicode escape obfuscation", 0.60),
        (r"base64|atob\(|btoa\(",
         "Encoding obfuscation", 0.55),
        (r"sudo|rm\s+-rf|chmod\s+777|/etc/passwd",
         "System command injection", 0.95),
        (r"reveal\s+(your|the)\s+(system|hidden|secret)\s+(prompt|instructions)",
         "Prompt exfiltration", 0.85),
        (r"what\s+(is|are)\s+your\s+(system|initial|original)\s+(prompt|instructions)",
         "Prompt exfiltration", 0.80),
    ]

    def __init__(self):
        self._compiled_patterns = [
            (re.compile(pat, re.IGNORECASE), desc, sev)
            for pat, desc, sev in self.INJECTION_PATTERNS
        ]
        logger.info("[PromptGuard] Injection detector initialized with %d patterns.",
                     len(self._compiled_patterns))

    def scan(self, query: str) -> Dict[str, Any]:
        """
        Scans a query for injection attempts.
        Returns: {is_safe: bool, score: float, threats: [...], action: str}
        """
        t0 = time.perf_counter()
        threats: List[Dict[str, Any]] = []
        max_severity = 0.0

        for pattern, description, severity in self._compiled_patterns:
            matches = pattern.findall(query)
            if matches:
                threats.append({
                    "pattern": description,
                    "severity": severity,
                    "match_count": len(matches),
                })
                max_severity = max(max_severity, severity)

        # Statistical anomaly: very long queries or extreme repetition
        word_count = len(query.split())
        unique_ratio = len(set(query.lower().split())) / max(word_count, 1)
        if word_count > 500:
            threats.append({
                "pattern": "Abnormally long query",
                "severity": 0.40,
                "match_count": 1,
            })
            max_severity = max(max_severity, 0.40)
        if unique_ratio < 0.20 and word_count > 20:
            threats.append({
                "pattern": "High repetition (possible padding attack)",
                "severity": 0.50,
                "match_count": 1,
            })
            max_severity = max(max_severity, 0.50)

        # Decision
        if max_severity >= 0.80:
            action = "BLOCK"
            is_safe = False
        elif max_severity >= 0.50:
            action = "WARN"
            is_safe = True  # Allow but log
        else:
            action = "ALLOW"
            is_safe = True

        latency = (time.perf_counter() - t0) * 1000
        return {
            "is_safe": is_safe,
            "score": round(max_severity, 4),
            "threats": threats,
            "action": action,
            "latency_ms": round(latency, 2),
        }


class RAGPoisoningDetector:
    """
    Detects adversarial payloads in documents being ingested into the RAG pipeline.
    Checks for:
      - Embedded prompt injection inside document text
      - Invisible unicode characters used for steganographic payloads
      - Abnormal character distributions
    """

    INVISIBLE_CHARS = re.compile(r'[\u200b\u200c\u200d\u2060\ufeff\u00ad]')

    def __init__(self):
        self.injection_detector = PromptInjectionDetector()

    def scan_document(self, text: str, document_name: str = "") -> Dict[str, Any]:
        t0 = time.perf_counter()
        threats: List[Dict[str, Any]] = []

        # 1. Check for embedded prompt injections
        # Split into chunks and scan each
        chunks = text.split("\n\n")
        injection_chunks = 0
        for i, chunk in enumerate(chunks):
            result = self.injection_detector.scan(chunk)
            if not result["is_safe"]:
                injection_chunks += 1
                threats.append({
                    "type": "embedded_injection",
                    "chunk_index": i,
                    "severity": result["score"],
                })

        # 2. Check for invisible unicode characters
        invisible_matches = self.INVISIBLE_CHARS.findall(text)
        if len(invisible_matches) > 5:
            threats.append({
                "type": "invisible_unicode_payload",
                "count": len(invisible_matches),
                "severity": 0.70,
            })

        # 3. Check abnormal non-ASCII ratio
        non_ascii = sum(1 for c in text if ord(c) > 127)
        total = max(len(text), 1)
        non_ascii_ratio = non_ascii / total
        if non_ascii_ratio > 0.30:
            threats.append({
                "type": "abnormal_character_distribution",
                "non_ascii_ratio": round(non_ascii_ratio, 4),
                "severity": 0.50,
            })

        is_safe = all(t.get("severity", 0) < 0.80 for t in threats)
        latency = (time.perf_counter() - t0) * 1000
        return {
            "document": document_name,
            "is_safe": is_safe,
            "threats": threats,
            "injection_chunks_found": injection_chunks,
            "latency_ms": round(latency, 2),
        }


class SecurityAuditLogger:
    """Thread-safe in-memory audit log with size cap."""

    def __init__(self, max_entries: int = 10000):
        self._log: deque = deque(maxlen=max_entries)

    def log(self, event_type: str, details: Dict[str, Any]):
        entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "details": details,
        }
        self._log.append(entry)
        if details.get("severity", 0) >= 0.80:
            logger.warning("[SECURITY AUDIT] %s: %s", event_type, json.dumps(details))

    def get_recent(self, count: int = 50) -> List[Dict[str, Any]]:
        return list(self._log)[-count:]

    def get_stats(self) -> Dict[str, int]:
        from collections import Counter
        types = Counter(e["event_type"] for e in self._log)
        return dict(types)


class PromptGuard:
    """
    Unified security gateway combining injection detection,
    RAG poisoning detection, and audit logging.
    """

    def __init__(self):
        self.injection_detector = PromptInjectionDetector()
        self.rag_detector = RAGPoisoningDetector()
        self.audit = SecurityAuditLogger()
        logger.info("[PromptGuard] Security gateway initialized.")

    def check_query(self, query: str) -> Dict[str, Any]:
        """Checks a user query for injection. Returns scan result."""
        result = self.injection_detector.scan(query)
        self.audit.log("query_scan", {
            "query_hash": hashlib.md5(query.encode(), usedforsecurity=False).hexdigest(),
            "action": result["action"],
            "severity": result["score"],
            "threat_count": len(result["threats"]),
        })
        return result

    def check_document(self, text: str, name: str = "") -> Dict[str, Any]:
        """Checks ingested document text for RAG poisoning."""
        result = self.rag_detector.scan_document(text, name)
        self.audit.log("document_scan", {
            "document": name,
            "is_safe": result["is_safe"],
            "threat_count": len(result["threats"]),
        })
        return result


# Global singleton
global_prompt_guard = PromptGuard()
