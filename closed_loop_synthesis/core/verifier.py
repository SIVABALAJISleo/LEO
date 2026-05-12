import subprocess
import os
import sys
import tempfile
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from closed_loop_synthesis.config import settings

logger = logging.getLogger(__name__)

class VerificationResult(BaseModel):
    success: bool
    errors: List[str] = []
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    type_check_pass: bool = False
    test_pass: bool = False

class Verifier:
    """
    CPU-only Verification Layer.
    Enforces correctness via isolated execution, mypy, and pytest.
    """
    def __init__(self, sandbox_dir: str = settings.SANDBOX_DIR):
        self.sandbox_dir = sandbox_dir
        os.makedirs(self.sandbox_dir, exist_ok=True)

    async def verify(self, code: str, tests: str) -> VerificationResult:
        # 1. Prepare Sandbox
        with tempfile.TemporaryDirectory(dir=self.sandbox_dir) as tmp_dir:
            code_path = os.path.join(tmp_dir, "solution.py")
            test_path = os.path.join(tmp_dir, "test_solution.py")
            
            # Ensure solution has type hints for mypy
            with open(code_path, "w") as f:
                f.write(code)
            
            with open(test_path, "w") as f:
                f.write(f"from solution import *\n\n{tests}")

            # 2. Mypy Type Check
            type_check = self._run_mypy(code_path)
            if not type_check["success"]:
                return VerificationResult(
                    success=False,
                    errors=[f"Mypy Error: {type_check['output']}"],
                    stderr=type_check['output'],
                    type_check_pass=False
                )

            # 3. Pytest Execution
            test_run = self._run_pytest(test_path)
            
            return VerificationResult(
                success=test_run["success"],
                errors=[] if test_run["success"] else [f"Test Failure: {test_run['output']}"],
                stdout=test_run["stdout"],
                stderr=test_run["stderr"],
                return_code=test_run["return_code"],
                type_check_pass=True,
                test_pass=test_run["success"]
            )

    def _run_mypy(self, file_path: str) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "mypy", "--ignore-missing-imports", "--follow-imports=silent", file_path],
                capture_output=True,
                text=True,
                timeout=settings.TIMEOUT_SECONDS
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout + result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "Mypy timed out."}
        except Exception as e:
            return {"success": False, "output": str(e)}

    def _run_pytest(self, test_path: str) -> Dict[str, Any]:
        try:
            # Run pytest in the sandbox
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-v", test_path],
                capture_output=True,
                text=True,
                timeout=settings.TIMEOUT_SECONDS,
                cwd=os.path.dirname(test_path)
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "output": result.stdout + result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False, 
                "stdout": "", 
                "stderr": "Execution timed out.", 
                "output": "Timeout", 
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False, 
                "stdout": "", 
                "stderr": str(e), 
                "output": str(e), 
                "return_code": -1
            }
