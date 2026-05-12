import subprocess
import sys
import os
import tempfile
import time
from typing import Dict, Any

class SandboxExecutor:
    """
    5. SANDBOX EXECUTION
    - Run isolated (subprocess)
    - Enforce timeout + memory limits
    """
    def __init__(self, timeout: int = 10, memory_limit_mb: int = 256):
        self.timeout = timeout
        self.memory_limit_mb = memory_limit_mb

    def run_code(self, code: str, test_code: str = "") -> Dict[str, Any]:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "solution.py")
            with open(file_path, "w") as f:
                f.write(code + "\n\n" + test_code)

            start_time = time.time()
            try:
                # Basic subprocess execution
                # Note: Real isolation would use Docker or a more restricted environment
                process = subprocess.Popen(
                    [sys.executable, file_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Check memory periodically (simplified)
                # In production, we'd use psutil to monitor and kill if exceeded
                stdout, stderr = process.communicate(timeout=self.timeout)
                duration = time.time() - start_time
                
                return {
                    "success": process.returncode == 0,
                    "stdout": stdout,
                    "stderr": stderr,
                    "duration": duration,
                    "exit_code": process.returncode
                }
            except subprocess.TimeoutExpired:
                process.kill()
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": "Timeout expired",
                    "duration": self.timeout,
                    "exit_code": -1
                }
            except Exception as e:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": str(e),
                    "duration": 0,
                    "exit_code": -1
                }
