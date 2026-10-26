#!/usr/bin/env python3
"""
scripts/lint_hardcoded_metrics.py
==================================
Word-Boundary Two-Tier AST Linter for Project LEO.

Scans Python source files in target directories (backend/, algorithm_discovery/, scripts/)
to detect fabricated, pre-determined, or hardcoded benchmark metrics, mock fallbacks,
and legacy literals while strictly avoiding false positives on configurations, thresholds,
and substring collisions.

Violation Patterns Caught:
  1. ast.Assign (e.g., confidence = 0.97)
  2. ast.AnnAssign (e.g., speedup: float = 8.2)
  3. ast.Dict literals (e.g., {"accuracy": 0.91})
  4. ast.Return dicts (e.g., return {"byte_vs_fp32_ratio": 15.75})
  5. ast.Call keyword arguments (e.g., Report(confidence=0.94))
  6. Legacy hardcoded literals (0.95, 0.99, 7.3, 14.0, 15.96, 100.0)
  7. ast.ExceptHandler blocks returning non-empty fabricated dicts or mock objects.

Exemptions & Zero-False-Positive Rules:
  - Tokenization: split on camelCase and snake_case via re.findall(r"[a-z0-9]+", ...)
  - No substring collisions: "https_port = 8443" is NOT flagged.
  - Modifier exemption: variables containing limit, max, min, cap, threshold, target,
    tol, tolerance, config, default, seed (e.g. tps_limit = 15, min_confidence = 0.80).
  - Sentinels: 0, 0.0, -1, -1.0 are benign.
  - Benign except returns: return None, return False, return {}, return [].
"""

import ast
import os
import re
import sys
from typing import List, NamedTuple, Optional, Set, Tuple

METRIC_WORDS: Set[str] = {
    "confidence",
    "accuracy",
    "speedup",
    "parity",
    "tps",
    "ratio",
    "reduction",
}

MULTI_WORD_PHRASES: List[Tuple[str, ...]] = [
    ("pass", "rate"),
    ("hit", "rate"),
    ("tokens", "per", "sec"),
]

MODIFIER_WORDS: Set[str] = {
    "limit",
    "max",
    "min",
    "cap",
    "threshold",
    "target",
    "tol",
    "tolerance",
    "config",
    "default",
    "seed",
    "bound",
    "bounds",
    "step",
    "alpha",
    "beta",
    "floor",
    "ceiling",
    "window",
    "size",
    "dim",
    "dimension",
    "layers",
    "count",
    "id",
    "port",
    "iters",
    "epochs",
    "steps",
    "rate_limit",
    "interval",
    "timeout",
    "top_k",
}

BENIGN_SENTINELS: Set[float] = {0.0, -1.0}

LEGACY_LITERALS: Set[float] = {0.95, 0.99, 7.3, 14.0, 15.96, 100.0}


class Violation(NamedTuple):
    filepath: str
    line: int
    col: int
    pattern_id: int
    pattern_name: str
    identifier: str
    detail: str


def tokenize_identifier(name: str) -> List[str]:
    """
    Split snake_case and camelCase identifiers into lowercase alphanumeric tokens.
    e.g. 'minConfidenceScore' -> ['min', 'confidence', 'score']
    e.g. 'byte_vs_fp32_ratio' -> ['byte', 'vs', 'fp32', 'ratio']
    """
    # First split on camelCase transitions: e.g. minConfidence -> min_Confidence
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    tokens = re.findall(r"[a-z0-9]+", s2.lower())
    return tokens


def is_metric_identifier(name: str) -> bool:
    """
    Check if identifier represents a metric name without any config/modifier words.
    """
    tokens = tokenize_identifier(name)
    if not tokens:
        return False

    # Check for modifier/config words - if any are present, this is a config bound, exempt!
    if any(m in tokens for m in MODIFIER_WORDS):
        return False

    # Check single metric words
    if any(w in tokens for w in METRIC_WORDS):
        return True

    # Check multi-word phrases
    token_str = "_".join(tokens)
    for phrase in MULTI_WORD_PHRASES:
        phrase_str = "_".join(phrase)
        if phrase_str in token_str:
            return True

    return False


def is_benign_number(val: object) -> bool:
    """Return True if value is a sentinel like 0, 0.0, -1, -1.0 or non-numeric."""
    if isinstance(val, (int, float)):
        if float(val) in BENIGN_SENTINELS:
            return True
        return False
    return True


class HardcodedMetricLinter(ast.NodeVisitor):
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.violations: List[Violation] = []
        self._current_except_handler = False

    def _get_target_name(self, node: ast.AST) -> Optional[str]:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None

    def _get_constant_val(self, node: ast.AST) -> Optional[object]:
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            if isinstance(node.operand, ast.Constant) and isinstance(node.operand.value, (int, float)):
                return -node.operand.value
        return None

    def visit_Assign(self, node: ast.Assign):
        # Pattern 1: ast.Assign (confidence = 0.97)
        for target in node.targets:
            target_name = self._get_target_name(target)
            if target_name:
                tokens = tokenize_identifier(target_name)
                # Check legacy literals assignment
                val = self._get_constant_val(node.value)
                if val is not None and isinstance(val, (int, float)):
                    fval = float(val)
                    if not any(m in tokens for m in MODIFIER_WORDS):
                        if is_metric_identifier(target_name) and not is_benign_number(fval):
                            self.violations.append(
                                Violation(
                                    self.filepath,
                                    node.lineno,
                                    node.col_offset,
                                    1,
                                    "ast.Assign",
                                    target_name,
                                    f"Hardcoded metric assignment '{target_name} = {val}'",
                                )
                            )
                        elif isinstance(val, float) and round(fval, 4) in LEGACY_LITERALS:
                            self.violations.append(
                                Violation(
                                    self.filepath,
                                    node.lineno,
                                    node.col_offset,
                                    6,
                                    "LegacyLiteral",
                                    target_name,
                                    f"Legacy suspicious literal assigned '{target_name} = {val}'",
                                )
                            )
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign):
        # Pattern 2: ast.AnnAssign (speedup: float = 8.2)
        target_name = self._get_target_name(node.target)
        if target_name and node.value:
            tokens = tokenize_identifier(target_name)
            val = self._get_constant_val(node.value)
            if val is not None and isinstance(val, (int, float)):
                fval = float(val)
                if not any(m in tokens for m in MODIFIER_WORDS):
                    if is_metric_identifier(target_name) and not is_benign_number(fval):
                        self.violations.append(
                            Violation(
                                self.filepath,
                                node.lineno,
                                node.col_offset,
                                2,
                                "ast.AnnAssign",
                                target_name,
                                f"Annotated hardcoded metric assignment '{target_name} = {val}'",
                            )
                        )
                    elif isinstance(val, float) and round(fval, 4) in LEGACY_LITERALS:
                        self.violations.append(
                            Violation(
                                self.filepath,
                                node.lineno,
                                node.col_offset,
                                6,
                                "LegacyLiteral",
                                target_name,
                                f"Legacy suspicious literal annotated '{target_name} = {val}'",
                            )
                        )
        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict):
        # Pattern 3: ast.Dict literals ({"accuracy": 0.91})
        for key_node, val_node in zip(node.keys, node.values):
            if key_node is not None:
                key_val = self._get_constant_val(key_node)
                if isinstance(key_val, str):
                    val = self._get_constant_val(val_node)
                    if val is not None and isinstance(val, (int, float)):
                        fval = float(val)
                        tokens = tokenize_identifier(key_val)
                        if not any(m in tokens for m in MODIFIER_WORDS):
                            if is_metric_identifier(key_val) and not is_benign_number(fval):
                                self.violations.append(
                                    Violation(
                                        self.filepath,
                                        key_node.lineno if hasattr(key_node, "lineno") else node.lineno,
                                        key_node.col_offset if hasattr(key_node, "col_offset") else node.col_offset,
                                        3,
                                        "ast.Dict",
                                        key_val,
                                        f"Hardcoded metric key in dict literal '{key_val}: {val}'",
                                    )
                                )
                            elif isinstance(val, float) and round(fval, 4) in LEGACY_LITERALS:
                                self.violations.append(
                                    Violation(
                                        self.filepath,
                                        key_node.lineno if hasattr(key_node, "lineno") else node.lineno,
                                        key_node.col_offset if hasattr(key_node, "col_offset") else node.col_offset,
                                        6,
                                        "LegacyLiteral",
                                        key_val,
                                        f"Legacy suspicious literal in dict '{key_val}: {val}'",
                                    )
                                )
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return):
        # Pattern 4: ast.Return dicts (return {"byte_vs_fp32_ratio": 15.75})
        if node.value and isinstance(node.value, ast.Dict):
            for key_node, val_node in zip(node.value.keys, node.value.values):
                if key_node is not None:
                    key_val = self._get_constant_val(key_node)
                    if isinstance(key_val, str) and is_metric_identifier(key_val):
                        val = self._get_constant_val(val_node)
                        if val is not None and isinstance(val, (int, float)) and not is_benign_number(float(val)):
                            tokens = tokenize_identifier(key_val)
                            if not any(m in tokens for m in MODIFIER_WORDS):
                                self.violations.append(
                                    Violation(
                                        self.filepath,
                                        node.lineno,
                                        node.col_offset,
                                        4,
                                        "ast.ReturnDict",
                                        key_val,
                                        f"Return dict containing hardcoded metric '{key_val}: {val}'",
                                    )
                                )
        # Check Pattern 7 inside ExceptHandler
        if self._current_except_handler and node.value:
            # Check if returning non-empty fabricated dict or mock
            if isinstance(node.value, ast.Dict) and len(node.value.keys) > 0:
                self.violations.append(
                    Violation(
                        self.filepath,
                        node.lineno,
                        node.col_offset,
                        7,
                        "ast.ExceptHandlerReturnMock",
                        "except_handler_return_dict",
                        "ExceptHandler returns non-empty fabricated dict fallback",
                    )
                )
            elif isinstance(node.value, ast.Call):
                func_name = self._get_target_name(node.value.func)
                if func_name and "mock" in func_name.lower():
                    self.violations.append(
                        Violation(
                            self.filepath,
                            node.lineno,
                            node.col_offset,
                            7,
                            "ast.ExceptHandlerReturnMock",
                            func_name,
                            f"ExceptHandler returns mock object '{func_name}()'",
                        )
                    )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # Pattern 5: ast.Call keyword arguments (Report(confidence=0.94))
        for kw in node.keywords:
            if kw.arg and is_metric_identifier(kw.arg):
                tokens = tokenize_identifier(kw.arg)
                if not any(m in tokens for m in MODIFIER_WORDS):
                    val = self._get_constant_val(kw.value)
                    if val is not None and isinstance(val, (int, float)):
                        fval = float(val)
                        if not is_benign_number(fval):
                            self.violations.append(
                                Violation(
                                    self.filepath,
                                    node.lineno,
                                    node.col_offset,
                                    5,
                                    "ast.CallKwarg",
                                    kw.arg,
                                    f"Hardcoded metric keyword argument '{kw.arg}={val}' in call",
                                )
                            )
                        elif isinstance(val, float) and round(fval, 4) in LEGACY_LITERALS:
                            self.violations.append(
                                Violation(
                                    self.filepath,
                                    node.lineno,
                                    node.col_offset,
                                    6,
                                    "LegacyLiteral",
                                    kw.arg,
                                    f"Legacy suspicious literal in call kwarg '{kw.arg}={val}'",
                                )
                            )
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        # Pattern 7: Catch except blocks returning non-empty fabricated dicts or mock objects
        prev = self._current_except_handler
        self._current_except_handler = True
        self.generic_visit(node)
        self._current_except_handler = prev


def lint_file(filepath: str) -> List[Violation]:
    """Parse and lint a single Python file."""
    # Never lint the linter itself
    norm_path = os.path.normpath(filepath)
    if norm_path.endswith(os.path.normpath("scripts/lint_hardcoded_metrics.py")):
        return []

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return []

    try:
        tree = ast.parse(code, filename=filepath)
    except SyntaxError as e:
        print(f"Syntax error in {filepath}:{e.lineno}: {e}", file=sys.stderr)
        return []

    linter = HardcodedMetricLinter(filepath)
    linter.visit(tree)
    return linter.violations


def lint_directories(dirs: List[str], exclude_dirs: Optional[Set[str]] = None) -> List[Violation]:
    """Scan all Python files in the specified directories."""
    all_violations: List[Violation] = []
    excludes = exclude_dirs or {".git", ".system_generated", "node_modules", "__pycache__", "venv", ".venv"}

    for d in dirs:
        if not os.path.exists(d):
            continue
        if os.path.isfile(d):
            if d.endswith(".py"):
                all_violations.extend(lint_file(d))
            continue

        for root, dirnames, filenames in os.walk(d):
            # Prune excluded directories in-place
            dirnames[:] = [dn for dn in dirnames if dn not in excludes and not dn.startswith(".")]

            for fn in filenames:
                if fn.endswith(".py"):
                    full_path = os.path.join(root, fn)
                    all_violations.extend(lint_file(full_path))

    return all_violations


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Word-boundary AST linter for hardcoded metrics in Project LEO."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["backend", "algorithm_discovery", "scripts"],
        help="Directories or files to scan (default: backend, algorithm_discovery, scripts)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Exit with status code 1 if any violations are found",
    )
    args = parser.parse_args()

    print(f"Running Word-Boundary AST Metric Linter across: {args.paths}")
    violations = lint_directories(args.paths)

    if not violations:
        print(f"\n[PASS] AST Linter clean: 0 violations detected across {len(args.paths)} paths.")
        sys.exit(0)

    print(f"\n[VIOLATIONS DETECTED] Found {len(violations)} hardcoded metric violations:")
    print("=" * 80)
    for v in violations:
        rel_path = os.path.relpath(v.filepath, os.getcwd())
        print(f"  {rel_path}:{v.line}:{v.col} [Pattern {v.pattern_id}: {v.pattern_name}] {v.detail}")
    print("=" * 80)
    print(f"Total: {len(violations)} violations.")

    if args.strict:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
