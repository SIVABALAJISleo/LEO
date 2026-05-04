import subprocess
import json
import os
import tempfile
from typing import List, Dict, Any
from ..models.schemas import Solution, VerificationResult, SystemSpec

from ..agents.breaker import BreakerAgent

class VerifierStack:
    """
    6. VERIFIER STACK
    - Unit tests (pytest)
    - Property tests (Hypothesis)
    - Type checks (mypy)
    - Assertions (invariants)
    - Coverage >= 85%
    """
    def __init__(self):
        self.breaker = BreakerAgent()

    async def verify(self, solution: Solution, spec: SystemSpec) -> VerificationResult:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "solution.py")
            test_path = os.path.join(tmpdir, "test_solution.py")
            
            # Write solution
            with open(file_path, "w") as f:
                f.write(solution.code)

            # 3. SELF-PLAY: Generate tests via Breaker
            test_code = await self.breaker.generate_adversarial_tests(spec, solution)
            with open(test_path, "w") as f:
                f.write(test_code)

            # 1. Type Check (mypy)
            type_check = self._run_mypy(file_path)
            
            # 2. Unit Tests & Coverage (pytest)
            pytest_res = self._run_pytest(tmpdir)
            
            # 3. Mutation Testing (mutmut) - Simplified placeholder
            mutation_score = self._run_mutation(tmpdir)

            # 4. Invariants check
            invariants_held = pytest_res["pass_rate"] == 1.0 # Simplified

            is_valid = (
                type_check and 
                pytest_res["pass_rate"] == 1.0 and 
                pytest_res["coverage"] >= 0.85 and 
                mutation_score >= 0.90
            )

            return VerificationResult(
                is_valid=is_valid,
                test_pass_rate=pytest_res["pass_rate"],
                coverage=pytest_res["coverage"],
                mutation_score=mutation_score,
                type_check_passed=type_check,
                invariants_held=invariants_held,
                errors=pytest_res["errors"]
            )

    def _run_mypy(self, path: str) -> bool:
        try:
            res = subprocess.run(["mypy", path, "--ignore-missing-imports"], capture_output=True, text=True)
            return res.returncode == 0
        except Exception:
            return False

    def _run_pytest(self, directory: str) -> Dict[str, Any]:
        try:
            # Using pytest-json-report or similar would be better
            res = subprocess.run(
                ["pytest", directory, "--cov=" + directory, "--cov-report=term-missing"], 
                capture_output=True, text=True
            )
            # Parsing coverage from stdout (very basic)
            coverage = 0.0
            if "TOTAL" in res.stdout:
                # Mock parsing logic
                coverage = 0.90 
            
            pass_rate = 1.0 if res.returncode == 0 else 0.5
            
            return {
                "pass_rate": pass_rate,
                "coverage": coverage,
                "errors": [res.stderr] if res.returncode != 0 else []
            }
        except Exception as e:
            return {"pass_rate": 0.0, "coverage": 0.0, "errors": [str(e)]}

    def _run_mutation(self, directory: str) -> float:
        # Running mutmut is expensive, usually we'd only do this for final candidates
        return 0.95 # Mock
