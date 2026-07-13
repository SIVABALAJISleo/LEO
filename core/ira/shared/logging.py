"""
IRA-specific logging system.
Every pillar logs through this single interface.
Logs are structured JSON for machine parsing.
"""
import logging
import json
import os
import sys
import time
import threading
from typing import Optional, Dict, Any
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Formats log records as JSON."""
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread_id": record.thread,
            "thread_name": record.threadName
        }
        if hasattr(record, 'ira_data') and record.ira_data:
            log_entry["ira_data"] = record.ira_data
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False)

class IRALogger:
    """
    Centralized logger for the entire IRA system.
    Each pillar gets its own named logger.
    """
    _loggers: Dict[str, logging.Logger] = {}
    _lock = threading.Lock()
    _log_dir: str = "logs/ira"

    @classmethod
    def set_log_dir(cls, log_dir: str):
        cls._log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

    @classmethod
    def get_logger(cls, pillar_name: str) -> logging.Logger:
        with cls._lock:
            if pillar_name in cls._loggers:
                return cls._loggers[pillar_name]

            logger = logging.getLogger(f"IRA.{pillar_name}")
            logger.setLevel(logging.DEBUG)
            logger.propagate = False

            # Console handler (human-readable)
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_fmt = logging.Formatter(
                f"[%(asctime)s] [IRA.{pillar_name}] [%(levelname)s] %(message)s",
                datefmt="%H:%M:%S.%f"
            )
            console_handler.setFormatter(console_fmt)
            logger.addHandler(console_handler)

            # File handler (JSON format)
            os.makedirs(cls._log_dir, exist_ok=True)
            file_path = os.path.join(cls._log_dir, f"{pillar_name}.jsonl")
            file_handler = logging.FileHandler(file_path, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(JSONFormatter())
            logger.addHandler(file_handler)

            cls._loggers[pillar_name] = logger
            return logger

    @classmethod
    def log_performance(cls, pillar: str, operation: str,
                       duration_ms: float, **kwargs):
        """Shorthand for performance logging."""
        logger = cls.get_logger(pillar)
        logger.info(
            f"PERF: {operation} = {duration_ms:.3f}ms",
            extra={"ira_data": {
                "operation": operation,
                "duration_ms": round(duration_ms, 6),
                **kwargs
            }}
        )
