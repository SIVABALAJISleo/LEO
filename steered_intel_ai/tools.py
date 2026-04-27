import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class ToolLayer:
    """
    LAYER 5: SYMBOLIC TOOL LAYER
    Deterministic execution for math, logic, and code.
    """
    def __init__(self):
        pass

    def run_tool(self, task: str, params: Dict[str, Any]) -> Any:
        if task == "math":
            return self._calculate(params.get("expression"))
        elif task == "logic":
            return self._rule_engine(params.get("rule"), params.get("data"))
        return "Tool task unknown."

    def _calculate(self, expression: str) -> str:
        try:
            # Dangerous in production, but here we assume a safe parser
            return str(eval(expression, {"__builtins__": {}}, {}))
        except Exception as e:
            return f"Math Error: {e}"

    def _rule_engine(self, rule: str, data: Any) -> str:
        # Simple boolean logic gate
        if rule == "is_authorized":
            return "ACCESS_GRANTED" if data == "ALPHA" else "ACCESS_DENIED"
        return "Rule not found."
