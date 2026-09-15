"""
scripts/generate_manifest.py
============================
Scans repository to produce a comprehensive repository_manifest.json
fulfilling Phase 1.1 of the Master Architectural Specification.
"""

import os
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS = {
    ".git", "node_modules", ".tanstack", ".output", ".vercel", "__pycache__",
    ".pytest_cache", "dist", ".gemini", "agentic-awesome-skills-main", "strix-main"
}

def classify_file(rel_path: str, size: int) -> str:
    norm = rel_path.replace("\\", "/").lower()
    
    if norm.endswith(".md") or norm.endswith(".txt") or norm.startswith("docs/"):
        return "DOCUMENTATION"
    if "/tests/" in norm or norm.startswith("tests/") or norm.startswith("e2e/") or "test_" in norm or norm.endswith(".spec.ts"):
        return "TEST"
    if "benchmark" in norm or norm.startswith("benchmarks/") or norm.startswith("benchmark_results/"):
        return "BENCHMARK"
    if norm.endswith(".json") and ("artifact" in norm or "cache" in norm or "ledger" in norm or "report" in norm or "result" in norm):
        return "GENERATED_ARTIFACT"
    if norm.startswith(".hyper_cache") or norm.startswith(".hyper_proxies") or norm.startswith("chroma_db"):
        return "GENERATED_ARTIFACT"
    if any(k in norm for k in ["hyper100", "hyper_ares", "cosmic_singularity", "chimera", "HYPER_v6_BREAKTHROUGH", "hyper_v2", "hyper_v3", "phoenix", "kimi-k3"]):
        return "EXPERIMENTAL"
    if any(k in norm for k in ["archive", "deprecated", "old_"]):
        return "DEPRECATED"
    if norm.startswith("hyper/") or norm.startswith("src/") or norm.startswith("universal_compute_router/"):
        return "ACTIVE_SOURCE"
    if norm.endswith((".py", ".ts", ".tsx", ".js", ".mjs", ".cjs", ".cpp", ".h", ".c")):
        return "ACTIVE_SOURCE"
    return "UNUSED_OR_UNVERIFIED"

def analyze_python_file(path: Path):
    imports = []
    has_main = False
    model_refs = []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        if "__main__" in content:
            has_main = True
        for m in re.findall(r"(?:llama|mistral|qwen|phi|openvino|onnx|vit|resnet|whisper|bert)", content, re.IGNORECASE):
            if m.lower() not in model_refs:
                model_refs.append(m.lower())
        tree = ast.parse(content, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.append(n.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except Exception:
        pass
    return sorted(set(imports)), has_main, model_refs

def scan_repo():
    manifest = {
        "metadata": {
            "root": str(ROOT),
            "engine": "LEO/HYPER Verified Computation-Elimination Engine",
            "version": "10.0.0",
        },
        "summary": {
            "total_files": 0,
            "categories": {},
            "duplicate_module_names": {},
        },
        "files": [],
        "entry_points": [],
        "external_dependencies": set(),
        "platform_specific_modules": [],
    }

    seen_basenames = {}

    for root, dirs, files in os.walk(ROOT):
        # Prune excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        
        for file in files:
            file_path = Path(root) / file
            rel_path = file_path.relative_to(ROOT).as_posix()
            size = file_path.stat().st_size
            ext = file_path.suffix.lower()
            
            category = classify_file(rel_path, size)
            manifest["summary"]["categories"][category] = manifest["summary"]["categories"].get(category, 0) + 1
            manifest["summary"]["total_files"] += 1

            info = {
                "path": rel_path,
                "file_type": ext or "no_extension",
                "size_bytes": size,
                "category": category,
            }

            if ext == ".py":
                base = file_path.name
                seen_basenames.setdefault(base, []).append(rel_path)
                imports, is_entry, models = analyze_python_file(file_path)
                info["imports"] = imports
                info["is_entry_point"] = is_entry
                info["model_references"] = models
                if is_entry:
                    manifest["entry_points"].append(rel_path)
                for imp in imports:
                    top = imp.split(".")[0]
                    if top not in ["os", "sys", "math", "time", "json", "typing", "pathlib", "dataclasses", "enum", "re", "ast", "subprocess", "hashlib", "unittest", "logging"]:
                        manifest["external_dependencies"].add(top)
                
                # Check platform specific
                try:
                    txt = file_path.read_text(encoding="utf-8", errors="ignore")
                    if "winreg" in txt or "ctypes.windll" in txt or "WMI" in txt:
                        manifest["platform_specific_modules"].append({"file": rel_path, "platform": "Windows"})
                    elif "posix" in txt or "/proc/" in txt:
                        manifest["platform_specific_modules"].append({"file": rel_path, "platform": "Linux"})
                except Exception:
                    pass

            manifest["files"].append(info)

    # Record duplicates
    for base, paths in seen_basenames.items():
        if len(paths) > 1 and base != "__init__.py":
            manifest["summary"]["duplicate_module_names"][base] = paths

    manifest["external_dependencies"] = sorted(manifest["external_dependencies"])
    return manifest

def main():
    print("Scanning repository...")
    manifest = scan_repo()
    out_path = ROOT / "repository_manifest.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest written to {out_path} (Total files: {manifest['summary']['total_files']})")
    print(f"Categories summary: {json.dumps(manifest['summary']['categories'], indent=2)}")

if __name__ == "__main__":
    main()
