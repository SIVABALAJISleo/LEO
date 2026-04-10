import logging
import datetime
import math
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ToolFramework:
    def __init__(self):
        self.tools = {
            "calculator": self._calculator,
            "time_service": self._time_service,
            "system_info": self._system_info
        }

    async def execute(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Executes a registered tool with provided arguments."""
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found."
        
        try:
            logger.info(f"executing_tool: name={tool_name}")
            return await self.tools[tool_name](args)
        except Exception as e:
            logger.error(f"tool_execution_failed: name={tool_name} error={e}")
            return f"Error: {e}"

    async def _calculator(self, args: Dict[str, Any]) -> str:
        expression = args.get("expression", "")
        if not expression:
            return "Error: No expression provided."
        
        # Use AST to safely evaluate basic math without eval()
        import ast
        import operator as op

        operators = {
            ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
            ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
            ast.USub: op.neg
        }

        def eval_expr(node):
            if isinstance(node, ast.Num): # <3.8
                return node.n
            elif isinstance(node, ast.Constant): # 3.8+
                return node.value
            elif isinstance(node, ast.BinOp):
                return operators[type(node.op)](eval_expr(node.left), eval_expr(node.right))
            elif isinstance(node, ast.UnaryOp):
                return operators[type(node.op)](eval_expr(node.operand))
            else:
                raise TypeError(node)

        try:
            # Basic sanitization of the expression string
            clean_expr = expression.replace(" ", "")
            tree = ast.parse(clean_expr, mode='eval')
            result = eval_expr(tree.body)
            return f"Result: {result}"
        except Exception as e:
            return f"Math Security Error: {e}"

    async def _time_service(self, args: Dict[str, Any]) -> str:
        now = datetime.datetime.now()
        return f"Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')}"

    async def _system_info(self, args: Dict[str, Any]) -> str:
        import psutil
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        return f"System Status: CPU={cpu}%, Memory={mem}%"

# Global instance
global_tools = ToolFramework()
