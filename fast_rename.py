import os
import re

root_dir = r"C:\Users\sivab\OneDrive\Documents\HYPER\HYPER-main"
exclude_dirs = {"node_modules", "venv", "venv_old", "venv_py311", "dist", ".git", "test_venv", "__pycache__", ".vite", "scratch"}
include_exts = {".py", ".yml", ".yaml", ".json", ".md", ".txt", ".toml", ".ts", ".tsx", ".js", ".html", ".css", ".sh", ".ps1", ".bat", ".cfg", ".ini", ".env", ".example"}

print("=== STEP 1: Replacing HYPER in file CONTENTS ===")
content_count = 0

for dirpath, dirnames, filenames in os.walk(root_dir):
    dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
    for file in filenames:
        ext = os.path.splitext(file)[1].lower()
        if ext in include_exts or file.endswith(".example") or file == ".env":
            filepath = os.path.join(dirpath, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue

            original = content
            content = content.replace('Project HYPER', 'Project HYPER')
            content = content.replace('project_hyper', 'project_hyper')
            content = content.replace('project-hyper', 'project-hyper')
            content = content.replace('SIVABALAJISleo/HYPER', 'SIVABALAJISleo/HYPER')
            content = content.replace('/HYPER.git', '/HYPER.git')
            content = content.replace('work/HYPER/HYPER', 'work/HYPER/HYPER')
            content = content.replace('"HYPER"', '"HYPER"')
            content = content.replace("'HYPER'", "'HYPER'")
            content = re.sub(r'\bLEO\b', 'HYPER', content)

            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  [CONTENT] {file}")
                content_count += 1

print(f"  -> {content_count} file(s) updated")

print("\n=== STEP 2: Renaming FILES with 'leo' in name ===")
file_rename_count = 0
for dirpath, dirnames, filenames in os.walk(root_dir):
    dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
    for file in filenames:
        if 'leo' in file.lower() and file != "rename_leo_to_hyper.ps1" and file != "fast_rename.py":
            new_name = file.replace('project_hyper', 'project_hyper').replace('leo_', 'hyper_').replace('_leo', '_hyper').replace('HYPER', 'HYPER').replace('leo', 'hyper')
            if new_name != file:
                os.rename(os.path.join(dirpath, file), os.path.join(dirpath, new_name))
                print(f"  [FILE] {file} -> {new_name}")
                file_rename_count += 1

print(f"  -> {file_rename_count} file(s) renamed")

print("\n=== STEP 3: Renaming DIRECTORIES with 'leo' in name ===")
dir_rename_count = 0
dirs_to_rename = []

for dirpath, dirnames, filenames in os.walk(root_dir):
    dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
    for dirname in dirnames:
        if 'leo' in dirname.lower():
            dirs_to_rename.append(os.path.join(dirpath, dirname))

# Rename deepest first
dirs_to_rename.sort(key=len, reverse=True)

for dirpath in dirs_to_rename:
    if not os.path.exists(dirpath): continue
    dirname = os.path.basename(dirpath)
    new_name = dirname.replace('project_hyper', 'project_hyper').replace('leo_', 'hyper_').replace('_leo', '_hyper').replace('HYPER', 'HYPER').replace('leo', 'hyper')
    if new_name != dirname:
        new_path = os.path.join(os.path.dirname(dirpath), new_name)
        os.rename(dirpath, new_path)
        print(f"  [DIR] {dirname} -> {new_name}")
        dir_rename_count += 1

print(f"  -> {dir_rename_count} director(ies) renamed")
print("\n=== DONE ===")
