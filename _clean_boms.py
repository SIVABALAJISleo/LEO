"""
Strip UTF-8 BOM (U+FEFF) from all Python files in the workspace.
"""

import os
from pathlib import Path

EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "node_modules", ".pytest_cache", 
    "__pycache__", ".hyper_cache", "dist", "build", ".tanstack", ".output"
}

def clean_boms():
    root = Path(os.getcwd()).resolve()
    cleaned = 0
    total = 0

    for root_dir, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for file in files:
            if file.endswith(".py"):
                total += 1
                file_path = Path(root_dir) / file
                try:
                    with open(file_path, "rb") as f:
                        content = f.read()
                    if content.startswith(b"\xef\xbb\xbf"): # UTF-8 BOM
                        clean_content = content[3:]
                        with open(file_path, "wb") as f:
                            f.write(clean_content)
                        cleaned += 1
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    print(f"BOM Cleaning Complete: Cleaned {cleaned} files out of {total} Python files.")

if __name__ == "__main__":
    clean_boms()
