import subprocess
import os
import sys
import tempfile
from typing import List, Tuple
from pydantic import BaseModel
from archive_engines.perfect_verification_system.config import settings

class DetailedResult(BaseModel):
    success: bool
    coverage: float = 0.0
    mypy_pass: bool = False
    pytest_pass: bool = False
    hypothesis_pass: bool = False
    errors: List[str] = []

class ExtremeVerifier:
    """
    5. VERIFIER (STRICT) + 6. TEST BOOST
    - pytest (unit tests)
    - mypy (type checks)
    - Hypothesis (property-based)
    - coverage >= 85%
    """
    def __init__(self, sandbox_dir: str = settings.SANDBOX_DIR):
        self.sandbox_dir = sandbox_dir

    async def verify(self, code: str, tests: str, properties: str = "") -> DetailedResult:
        with tempfile.TemporaryDirectory(dir=self.sandbox_dir) as tmp_dir:
            sol_path = os.path.join(tmp_dir, "solution.py")
            test_path = os.path.join(tmp_dir, "test_extreme.py")
            
            with open(sol_path, "w") as f: f.write(code)
            
            # Combine unit tests and property-based tests (Hypothesis)
            full_test_code = f"from solution import *\nimport hypothesis\nfrom hypothesis import given, strategies as st\n\n{tests}\n\n{properties}"
            with open(test_path, "w") as f: f.write(full_test_code)

            # 1. Mypy
            mypy_res = self._run_cmd([sys.executable, "-m", "mypy", sol_path], tmp_dir)
            
            # 2. Pytest + Coverage
            # We use 'pytest-cov' to measure coverage
            pytest_cmd = [
                sys.executable, "-m", "pytest", 
                "--cov=solution", "--cov-report=term-missing", 
                test_path
            ]
            pytest_res = self._run_cmd(pytest_cmd, tmp_dir)
            
            # Extract coverage percentage from stdout
            coverage = self._parse_coverage(pytest_res[1])
            
            # 3. Decision Logic
            success = (
                mypy_res[0] == 0 and 
                pytest_res[0] == 0 and 
                coverage >= settings.MIN_COVERAGE
            )
            
            errors = []
            if mypy_res[0] != 0: errors.append(f"Mypy: {mypy_res[1]}")
            if pytest_res[0] != 0: errors.append(f"Pytest/Hypothesis: {pytest_res[1]}")
            if coverage < settings.MIN_COVERAGE: errors.append(f"Low Coverage: {coverage*100:.1%}")

            return DetailedResult(
                success=success,
                coverage=coverage,
                mypy_pass=(mypy_res[0] == 0),
                pytest_pass=(pytest_res[0] == 0),
                hypothesis_pass=(pytest_res[0] == 0), # Simplified for demo
                errors=errors
            )

    def _run_cmd(self, cmd: List[str], cwd: str) -> Tuple[int, str]:
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=settings.TIMEOUT_SECONDS, cwd=cwd)
            return res.returncode, res.stdout + res.stderr
        except Exception as e:
            return -1, str(e)

    def _parse_coverage(self, output: str) -> float:
        # Look for "TOTAL ... 100%"
        match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
        if match:
            return float(match.group(1)) / 100.0
        return 0.0

import re
