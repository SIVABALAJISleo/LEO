import os
import sys
import importlib.util
from pathlib import Path

def scan_imports(directory):
    print(f"Scanning {directory} for import errors...")
    py_files = list(Path(directory).rglob("*.py"))
    
    success_count = 0
    failure_count = 0
    
    for py_file in py_files:
        if py_file.name == "__init__.py":
            continue
            
        module_name = py_file.stem
        spec = importlib.util.spec_from_file_location(module_name, str(py_file))
        if spec is None:
            print(f"Could not load spec for {py_file}")
            continue
            
        module = importlib.util.module_from_spec(spec)
        try:
            # Add current directory to path for relative imports
            sys.path.append(os.getcwd())
            spec.loader.exec_module(module)
            success_count += 1
            print(f"✅ Successfully imported: {py_file}")
        except Exception as e:
            failure_count += 1
            print(f"❌ Failed to import {py_file}: {e}")
            
    print(f"\nScan complete: {success_count} passed, {failure_count} failed.")
    return failure_count

if __name__ == "__main__":
    sys.exit(scan_imports("backend"))
