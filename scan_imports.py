import os
import sys
import importlib
from pathlib import Path

def scan_imports(directory):
    print(f"Scanning {directory} for import errors...")
    root = Path(os.getcwd()).resolve()
    py_files = list(Path(directory).resolve().rglob("*.py"))
    
    success_count = 0
    failure_count = 0
    failures = []
    
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
        
    for py_file in py_files:
        if py_file.name == "__init__.py":
            continue
            
        try:
            rel_path = py_file.relative_to(root)
            module_name = str(rel_path.with_suffix("")).replace(os.sep, ".").replace("/", ".")
            importlib.import_module(module_name)
            success_count += 1
        except Exception as e:
            failure_count += 1
            failures.append((str(py_file), str(e)))
            
    print(f"\nScan complete: {success_count} passed, {failure_count} failed.")
    if failures:
        print("\nFailed Imports:")
        for f, err in failures[:20]:
            print(f" - {f}: {err}")
    return failure_count

if __name__ == "__main__":
    sys.exit(scan_imports("backend"))
