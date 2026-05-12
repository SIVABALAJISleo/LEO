import re
from typing import Optional

class ErrorAnalyzer:
    """
    Error Analysis Layer.
    Converts raw stderr into compact, actionable signals for the LLM.
    """
    
    def analyze(self, stderr: str) -> str:
        if not stderr:
            return "Unknown execution error."

        # 1. Capture Python Exception lines
        # Look for lines like "NameError: name 'x' is not defined"
        exception_match = re.search(r"([a-zA-Z]+Error: .+)", stderr)
        if exception_match:
            return exception_match.group(1)

        # 2. Capture Pytest failures
        if "AssertionError" in stderr:
            # Try to find the line where assertion failed
            assertion_match = re.search(r"E\s+assert .+", stderr)
            if assertion_match:
                return assertion_match.group(0)
            return "Assertion failed during testing."

        # 3. Capture Mypy errors
        if "error:" in stderr:
            # Summarize first few mypy errors
            mypy_errors = re.findall(r"solution\.py:\d+: error: (.+)", stderr)
            if mypy_errors:
                return f"Type Check Errors: {'; '.join(mypy_errors[:2])}"

        # 4. Fallback: Take the last 3 lines
        lines = [l.strip() for l in stderr.split('\n') if l.strip()]
        return " ".join(lines[-3:]) if lines else "Execution failed with non-zero exit code."

    def summarize_failures(self, failure_logs: list) -> str:
        """
        Takes a list of stderr logs and creates a combined signal.
        """
        signals = [self.analyze(log) for log in failure_logs]
        unique_signals = list(set(signals))
        return " | ".join(unique_signals)
