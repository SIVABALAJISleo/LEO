import subprocess
import os
import sys
import tempfile
from typing import Dict, Any

class VerifierEngine:
    """
    Isolated execution engine for verifying code and logic.
    """
    def __init__(self, sandbox_dir: str = "sandbox"):
        self.sandbox_dir = sandbox_dir
        os.makedirs(self.sandbox_dir, exist_ok=True)

    async def verify_python(self, code: str, tests: str) -> Dict[str, Any]:
        with tempfile.TemporaryDirectory(dir=self.sandbox_dir) as tmp_dir:
            sol_path = os.path.join(tmp_dir, "solution.py")
            test_path = os.path.join(tmp_dir, "test_solution.py")
            
            with open(sol_path, "w") as f: f.write(code)
            with open(test_path, "w") as f: f.write(f"from solution import *\n\n{tests}")

            # 1. Mypy
            mypy_res = subprocess.run(
                [sys.executable, "-m", "mypy", sol_path],
                capture_output=True, text=True, timeout=10
            )
            
            # 2. Pytest
            test_res = subprocess.run(
                [sys.executable, "-m", "pytest", test_path],
                capture_output=True, text=True, timeout=10, cwd=tmp_dir
            )
            
            success = (mypy_res.returncode == 0 and test_res.returncode == 0)
            
            return {
                "success": success,
                "mypy_output": mypy_res.stdout + mypy_res.stderr,
                "test_output": test_res.stdout + test_res.stderr,
                "error_signal": self._extract_signal(test_res.stderr or test_res.stdout)
            }

    def _extract_signal(self, output: str) -> str:
        # Compact error extraction
        import re
        match = re.search(r"([a-zA-Z]+Error: .+)", output)
        if match: return match.group(1)
        if "AssertionError" in output: return "Assertion failed."
        return "Execution failed."
