"""
Project-Wide End-to-End Integration & Syntax Verifier
Checks AST validity, syntax integrity, and import loadability across all Python files in the workspace.
"""

import os
import sys
import ast
import importlib
from pathlib import Path

EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "node_modules", ".pytest_cache", 
    "__pycache__", ".hyper_cache", "dist", "build", ".tanstack", ".output"
}

def verify_all_modules():
    root = Path(os.getcwd()).resolve()
    print("=" * 70)
    print(f"  FULL PROJECT END-TO-END CODE INTEGRITY & SYNTAX SCANNER")
    print(f"  Root: {root}")
    print("=" * 70)

    all_py_files = []
    for root_dir, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for file in files:
            if file.endswith(".py") and not file.startswith("."):
                all_py_files.append(Path(root_dir) / file)

    print(f"Found {len(all_py_files)} Python files to verify across all subsystems.\n")

    syntax_passed = 0
    syntax_failed = 0
    syntax_errors = []

    # Phase 1: AST Syntax Validation on 100% of files
    for py_file in all_py_files:
        try:
            with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()
            ast.parse(code, filename=str(py_file))
            syntax_passed += 1
        except SyntaxError as e:
            syntax_failed += 1
            syntax_errors.append((str(py_file.relative_to(root)), str(e)))

    print(f"Phase 1 (AST Syntax Integrity): {syntax_passed} PASSED, {syntax_failed} FAILED.")
    if syntax_errors:
        print("\nSyntax Errors Found:")
        for f, err in syntax_errors:
            print(f" [X] {f}: {err}")

    # Phase 2: Core Subsystem Import Integrity Check
    print("\nPhase 2 (Subsystem Component Verification):")
    core_packages = [
        "HYPER_v6_BREAKTHROUGH.hyper_engine",
        "HYPER_v6_BREAKTHROUGH.contract_analyzer",
        "HYPER_v6_BREAKTHROUGH.cache_engine",
        "backend.cache.semantic_cache",
        "backend.core.metrics",
        "backend.intelligence.router",
        "backend.hardware.detector",
        "backend.middleware.csrf",
        "core.inference",
        "universal_compute_router.router_logic"
    ]

    import_passed = 0
    import_failed = 0
    for pkg in core_packages:
        try:
            importlib.import_module(pkg)
            import_passed += 1
            print(f" [OK] {pkg}")
        except Exception as e:
            import_failed += 1
            print(f" [X]  {pkg}: {e}")

    print("-" * 70)
    print(f"SUMMARY: {syntax_passed}/{len(all_py_files)} Files Valid, {import_passed}/{len(core_packages)} Core Engines Active.")
    print("=" * 70)
    return syntax_failed + import_failed

if __name__ == "__main__":
    sys.exit(verify_all_modules())
