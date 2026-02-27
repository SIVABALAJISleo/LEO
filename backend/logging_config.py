import logging
import json
import time
from typing import Any, Dict

class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings for production logs.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "func": record.funcName
        }
        
        # Include extra attributes if provided via 'extra' param
        if hasattr(record, "extra_data"):
            log_obj.update(record.extra_data)
            
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_obj)

def setup_production_logging(level=logging.INFO):
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    
    # Root logger config
    root = logging.getLogger()
    root.setLevel(level)
    
    # Remove existing handlers
    for h in root.handlers[:]:
        root.removeHandler(h)
        
    root.addHandler(handler)
    logging.info("Structured JSON Logging initialized.")

if __name__ == "__main__":
    setup_production_logging()
    logging.info("Test production log", extra={"extra_data": {"user_id": 123, "action": "test"}})
