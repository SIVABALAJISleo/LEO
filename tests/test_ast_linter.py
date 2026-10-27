"""
tests/test_ast_linter.py
========================
Verification suite for the Word-Boundary Two-Tier AST Linter.

Tests:
  - 7/7 Positive Patterns (all must trigger violation):
      1. Pattern 1: ast.Assign (confidence = 0.97)
      2. Pattern 2: ast.AnnAssign (speedup: float = 8.2)
      3. Pattern 3: ast.Dict literals ({"accuracy": 0.91})
      4. Pattern 4: ast.Return dicts (return {"byte_vs_fp32_ratio": 15.75})
      5. Pattern 5: ast.Call keyword arguments (Report(confidence=0.94))
      6. Pattern 6: Legacy hardcoded literals (suspicious literals like 0.95, 100.0)
      7. Pattern 7: ast.ExceptHandler returning fabricated dict
  - 0/7 Negative Controls (benign patterns that must NOT trigger):
      1. Benign sentinel (confidence = 0.0)
      2. Modifier exemption (min_confidence = 0.80)
      3. Substring collision avoidance (https_port = 8443)
      4. Benign except handler return (except: return None)
      5. Dynamic computed metric (speedup = a / b)
      6. Benign dictionary keys ({"batch_size": 32})
      7. Tolerance/threshold variable (epsilon_tol = 1e-4)
  - Full codebase validation: backend/canonical, backend/caoe, backend/hardware have 0 violations.
"""

import ast
import os
import pytest
from scripts.lint_hardcoded_metrics import HardcodedMetricLinter, lint_directories


def _lint_code(code: str) -> list:
    tree = ast.parse(code)
    linter = HardcodedMetricLinter("<test_snippet>")
    linter.visit(tree)
    return linter.violations


# ── 7/7 Positive Pattern Unit Tests ──────────────────────────────────────────

def test_pattern_1_assign():
    violations = _lint_code("confidence = 0.97")
    assert len(violations) >= 1
    assert any(v.pattern_id == 1 for v in violations)


def test_pattern_2_ann_assign():
    violations = _lint_code("speedup: float = 8.2")
    assert len(violations) >= 1
    assert any(v.pattern_id == 2 for v in violations)


def test_pattern_3_dict():
    violations = _lint_code('data = {"accuracy": 0.91}')
    assert len(violations) >= 1
    assert any(v.pattern_id == 3 for v in violations)


def test_pattern_4_return_dict():
    violations = _lint_code('def f(): return {"byte_vs_fp32_ratio": 15.75}')
    assert len(violations) >= 1
    assert any(v.pattern_id == 4 for v in violations)


def test_pattern_5_call_kwarg():
    violations = _lint_code("Report(confidence=0.94)")
    assert len(violations) >= 1
    assert any(v.pattern_id == 5 for v in violations)


def test_pattern_6_legacy_literal():
    violations = _lint_code("measured_gain = 15.96")
    assert len(violations) >= 1
    assert any(v.pattern_id == 6 for v in violations)


def test_pattern_7_except_handler():
    code = """
try:
    compute()
except Exception:
    return {"speedup": 4.5}
"""
    violations = _lint_code(code)
    assert len(violations) >= 1
    assert any(v.pattern_id == 7 for v in violations)


# ── 0/7 Negative Control Unit Tests (Must produce ZERO violations) ───────────

def test_neg_1_benign_sentinel():
    violations = _lint_code("confidence = 0.0\nspeedup = -1.0")
    assert len(violations) == 0


def test_neg_2_modifier_exemption():
    violations = _lint_code("min_confidence = 0.80\ntps_limit = 15\nmax_ratio = 4.0")
    assert len(violations) == 0


def test_neg_3_substring_collision():
    violations = _lint_code("https_port = 8443\ntarget_ip = '127.0.0.1'")
    assert len(violations) == 0


def test_neg_4_benign_except_return():
    code = """
try:
    do_something()
except Exception:
    return None
"""
    violations = _lint_code(code)
    assert len(violations) == 0


def test_neg_5_dynamic_computed_metric():
    violations = _lint_code("speedup = float(t_base / max(t_cand, 1e-6))")
    assert len(violations) == 0


def test_neg_6_benign_dict_keys():
    violations = _lint_code('config = {"batch_size": 32, "dim": 2048, "threads": 8}')
    assert len(violations) == 0


def test_neg_7_tolerance_threshold():
    violations = _lint_code("epsilon_tol = 1e-4\nsvd_energy_threshold = 0.95")
    assert len(violations) == 0


# ── Full Canonical/CAOE/Hardware Tree Audit (0 Violations) ──────────────────

def test_active_backend_trees_zero_violations():
    target_dirs = [
        os.path.join("backend", "canonical"),
        os.path.join("backend", "caoe"),
        os.path.join("backend", "hardware"),
    ]
    violations = lint_directories(target_dirs)
    assert len(violations) == 0, f"Found {len(violations)} unexpected AST violations: {violations}"
