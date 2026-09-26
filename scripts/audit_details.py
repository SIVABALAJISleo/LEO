import os
import json

def inspect_dir(path):
    if not os.path.exists(path):
        return []
    items = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in ('node_modules', '.git', '__pycache__', '.venv')]
        for f in files:
            items.append(os.path.relpath(os.path.join(root, f), path))
    return items

backend_files = inspect_dir('backend')
tests_files = inspect_dir('tests')
github_files = inspect_dir('.github')

print("Backend count:", len(backend_files))
print("Backend sample:", backend_files[:20])
print("\nTests count:", len(tests_files))
print("Tests sample:", tests_files[:20])
print("\nGithub count:", len(github_files))
print("Github files:", github_files)
