"""
scripts/generate_sot_map.py
===========================
Generates SOURCE_OF_TRUTH_MAP.md documenting all duplicated modules across the repository,
their purpose, imports, status, and recommended action.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def generate():
    manifest_path = ROOT / "repository_manifest.json"
    with open(manifest_path, encoding="utf-8") as f:
        data = json.load(f)

    dups = data["summary"]["duplicate_module_names"]
    
    file_map = {f["path"]: f for f in data["files"]}

    md_lines = [
        "# LEO/HYPER Source of Truth Map",
        "",
        "## Executive Architectural Decision",
        "",
        "The repository contains historical prototypes across `archive_engines/`, `core_ai/`, `backend/`, `HYPER_v6_BREAKTHROUGH/`, and `hyper_x/`.",
        "Under the **Verified Computation-Elimination Runtime Architecture**, the unified and authoritative package is **`hyper/`**.",
        "All older and experimental implementations are classified as `DEPRECATED` or `EXPERIMENTAL` and preserved for reference without compromising scientific integrity.",
        "",
        "## Authoritative Source of Truth Matrix",
        "",
        "| Subsystem | Authoritative Module (`hyper/`) | Legacy / Prototype Locations | Status | Recommended Action |",
        "| :--- | :--- | :--- | :--- | :--- |",
        "| **Contracts & Constraints** | `hyper.contracts.contract` | `contracts/`, `core_ai/contracts.py` | ACTIVE_SOURCE | Enforce formal `Contract` dataclass with fail-closed validation |",
        "| **Hardware Profiler** | `hyper.cli` / `hyper.hardware` | `benchmarks/hardware_check.py`, `scripts/bench_hardware.py` | ACTIVE_SOURCE | Dynamic profiling via `python -m hyper.cli hardware-profile` |",
        "| **Candidate Execution Model** | `hyper.candidate` | `core_ai/router.py`, `universal_compute_router/` | ACTIVE_SOURCE | Explicit `CandidateResult` with paths (`EXACT`, `CACHED`, etc.) |",
        "| **Exact Cache** | `hyper.cache` | `archive_engines/.../cache.py`, `cache/` | ACTIVE_SOURCE | Multi-state cryptographic hash; separate hit/miss reporting |",
        "| **Incremental & Delta** | `hyper.incremental` | `archive_engines/temporal_engine.py` | ACTIVE_SOURCE | Linear delta reuse with exact fallback on nonlinear/unknown |",
        "| **Sparsity Engine** | `hyper.sparsity` | `core_ai/sparsity.py`, `optimization/sparsity.py` | ACTIVE_SOURCE | Measure threshold overhead; only run if cheaper than dense |",
        "| **Low-Rank Factorization** | `hyper.low_rank` | `math_engine/svd.py`, `backend/compression/` | ACTIVE_SOURCE | SVD with break-even reuse count tracking |",
        "| **Precision Engine** | `hyper.precision` | `core_ai/quantization.py`, `scripts/compress_to_ternary.py` | ACTIVE_SOURCE | Explicit multi-precision (FP64 down to ternary) with error bounds |",
        "| **Prediction & Residual** | `hyper.prediction` / `hyper.residual` | `core_ai/speculative_engine.py`, `predictors/` | ACTIVE_SOURCE | Contract-verified $\\hat{y} + r$ with exact fallback |",
        "| **CPU + iGPU Scheduler** | `hyper.scheduler` | `universal_compute_router/orchestrator.py`, `hyper_ares/` | ACTIVE_SOURCE | Real benchmark-driven dispatch between CPU and Intel UHD iGPU |",
        "| **Verification Engine** | `hyper.verification` | `archive_engines/.../verifier.py`, `qa_security_team/` | ACTIVE_SOURCE | Multi-domain (Freivalds, PSNR/SSIM, retrieval, exact numerical) |",
        "| **Benchmarking Suite** | `hyper.benchmark` | `scripts/benchmark.py`, `benchmarks/` | ACTIVE_SOURCE | High-resolution `perf_counter_ns()`, warmups, p95, zero fake timings |",
        "| **Parity Calculations** | `hyper.parity` | `scripts/verify_100_percent.py` | ACTIVE_SOURCE | Disjoint tiers (`RAW_HARDWARE`, `CONTRACT`, `APPLICATION`) |",
        "",
        "## Detailed Duplicate Module Inventory",
        "",
    ]

    for base, paths in sorted(dups.items()):
        md_lines.append(f"### Module `{base}` ({len(paths)} occurrences)")
        md_lines.append("")
        md_lines.append("| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |")
        md_lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for p in sorted(paths):
            info = file_map.get(p, {})
            cat = info.get("category", "UNKNOWN")
            sz = info.get("size_bytes", 0)
            imp = ", ".join(info.get("imports", [])[:4]) or "none"
            if p.startswith("hyper/"):
                rec = "**Retain as Authoritative Source of Truth**"
            elif p.startswith("archive_engines/"):
                rec = "Preserve as historical reference (Deprecated)"
            elif p.startswith("tests/"):
                rec = "Update imports to reference `hyper.*`"
            else:
                rec = "Preserve for compatibility / migrate to `hyper.*`"
            md_lines.append(f"| `{p}` | `{cat}` | {sz} | `{imp}` | {rec} |")
        md_lines.append("")

    out_file = ROOT / "SOURCE_OF_TRUTH_MAP.md"
    out_file.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Written {out_file}")

if __name__ == "__main__":
    generate()
