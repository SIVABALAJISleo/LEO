"""
hyper_universal/sandbox/security.py
===================================
AST Security Inspector & Static Policy Enforcer.

Implements Section 23 of the Master Specification:
- Inspects candidate source code for forbidden imports, system calls, network access,
  process creation, and filesystem access.
"""

from __future__ import annotations
import ast
from typing import List, Tuple, Set


FORBIDDEN_MODULES: Set[str] = {
    "os", "sys", "subprocess", "socket", "urllib", "requests", "http",
    "shutil", "builtins", "importlib", "pickle", "ctypes", "pty", "commands",
    "winreg", "posix", "nt", "_thread", "threading", "multiprocessing"
}

FORBIDDEN_CALLS: Set[str] = {
    "eval", "exec", "open", "__import__", "compile", "breakpoint",
    "getattr", "setattr", "delattr", "globals", "locals"
}


class ASTSecurityInspector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.violations: List[str] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            base_mod = alias.name.split('.')[0]
            if base_mod in FORBIDDEN_MODULES:
                self.violations.append(f"Forbidden module import: '{alias.name}' at line {node.lineno}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            base_mod = node.module.split('.')[0]
            if base_mod in FORBIDDEN_MODULES:
                self.violations.append(f"Forbidden from-import: '{node.module}' at line {node.lineno}")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            if node.func.id in FORBIDDEN_CALLS:
                self.violations.append(f"Forbidden dangerous call: '{node.func.id}()' at line {node.lineno}")
        self.generic_visit(node)


def inspect_source_code(source: str) -> Tuple[bool, List[str]]:
    """Inspects generated code. Returns (is_secure, violations)."""
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return False, [f"Syntax error in generated candidate: {str(e)}"]

    inspector = ASTSecurityInspector()
    inspector.visit(tree)
    return len(inspector.violations) == 0, inspector.violations
