import logging
from typing import Any, Dict

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
            import ast
            import operator
            operators = {
                ast.Add: operator.add, ast.Sub: operator.sub,
                ast.Mult: operator.mul, ast.Div: operator.truediv,
                ast.Pow: operator.pow, ast.USub: operator.neg,
            }
            def eval_node(node):
                if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                    return node.value
                elif isinstance(node, ast.BinOp) and type(node.op) in operators:
                    return operators[type(node.op)](eval_node(node.left), eval_node(node.right))
                elif isinstance(node, ast.UnaryOp) and type(node.op) in operators:
                    return operators[type(node.op)](eval_node(node.operand))
                raise ValueError("Unsupported expression")
            tree = ast.parse(expression, mode='eval')
            return str(eval_node(tree.body))
        except Exception:
            logger.error("Safe calculation failed", exc_info=True)
            return "Math Error: Invalid or unsupported mathematical expression"

    def _rule_engine(self, rule: str, data: Any) -> str:
        # Simple boolean logic gate
        if rule == "is_authorized":
            return "ACCESS_GRANTED" if data == "ALPHA" else "ACCESS_DENIED"
        return "Rule not found."
