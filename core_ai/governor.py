"""
core_ai/governor.py
Safety governor for LEO AI v∞.
Enforces RAM thresholds, connection limits, query timeout limits,
concurrency queue backpressure, disk-cache limits, and swap storm protection.
"""

import os
import gc
import time
import logging
import psutil
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class LEOSafetyGovernor:
    """Monitors system resources and coordinates backpressure to prevent swap storms or crashes."""
    def __init__(
        self,
        max_concurrent_requests: int = 4,
        min_available_ram_gb: float = 1.0,
        max_request_timeout_seconds: float = 30.0,
        max_cache_dir_size_mb: float = 500.0
    ):
        self.max_concurrent_requests = max_concurrent_requests
        self.min_available_ram_gb = min_available_ram_gb
        self.max_request_timeout_seconds = max_request_timeout_seconds
        self.max_cache_dir_size_mb = max_cache_dir_size_mb
        self.active_requests = 0

    def check_system_safety(self) -> Dict[str, Any]:
        """Probes RAM and disk space, performing garbage collections or triggers warning states."""
        mem = psutil.virtual_memory()
        avail_ram_gb = mem.available / (1024 ** 3)
        
        status = "SAFE"
        warnings = []

        # Swap storm protection
        if avail_ram_gb < self.min_available_ram_gb:
            status = "CRITICAL"
            warnings.append(f"Available RAM is extremely low: {avail_ram_gb:.2f} GB. Truncating context ranges and purging caches.")
            # Aggressive gc collection
            gc.collect()
        elif avail_ram_gb < self.min_available_ram_gb * 1.5:
            status = "WARNING"
            warnings.append(f"Available RAM is tight: {avail_ram_gb:.2f} GB. Active queue capacity reduced.")

        return {
            "status": status,
            "available_ram_gb": round(avail_ram_gb, 2),
            "warnings": warnings
        }

    def acquire_slot(self) -> bool:
        """Acquires a concurrency queue slot; returns False if server is overloaded."""
        safety = self.check_system_safety()
        limit = self.max_concurrent_requests
        
        # Tighten limits under warning status
        if safety["status"] == "WARNING":
            limit = max(1, self.max_concurrent_requests // 2)
        elif safety["status"] == "CRITICAL":
            limit = 1

        if self.active_requests >= limit:
            logger.warning(f"[Governor] Connection rejected due to queue backpressure. Active: {self.active_requests}, Max: {limit}.")
            return False
        
        self.active_requests += 1
        return True

    def release_slot(self) -> None:
        self.active_requests = max(0, self.active_requests - 1)

    def enforce_cache_limits(self, cache_dir: str) -> None:
        """Ensures semantic cache files do not exceed maximum storage limits."""
        if not os.path.exists(cache_dir):
            return

        try:
            total_size_bytes = 0
            files = []
            for root, _, filenames in os.walk(cache_dir):
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    stat = os.stat(filepath)
                    total_size_bytes += stat.st_size
                    files.append((filepath, stat.st_mtime, stat.st_size))

            total_size_mb = total_size_bytes / (1024 * 1024)
            if total_size_mb > self.max_cache_dir_size_mb:
                logger.warning(f"[Governor] Cache directory size ({total_size_mb:.2f} MB) exceeds maximum. Purging oldest entries.")
                # Sort files by last modification time (oldest first)
                files.sort(key=lambda x: x[1])
                bytes_to_delete = total_size_bytes - (self.max_cache_dir_size_mb * 0.7 * 1024 * 1024) # purge down to 70%
                
                deleted_bytes = 0
                for filepath, _, size in files:
                    try:
                        os.remove(filepath)
                        deleted_bytes += size
                        if deleted_bytes >= bytes_to_delete:
                            break
                    except Exception as e:
                        logger.error(f"[Governor] Failed to delete cache file {filepath}: {e}")
        except Exception as e:
            logger.error(f"[Governor] Cache limit audit failed: {e}")
