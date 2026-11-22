#!/usr/bin/env python3
"""
PaperOrchestra Generation CLI for Project LEO / HYPER.
Transforms empirical audit ledgers into submission-ready conference papers (ICLR, CVPR, IEEE).

Usage:
  python scripts/generate_paper_orchestra.py --template iclr2025 --dry-run
  python scripts/generate_paper_orchestra.py --template cvpr2025 --output-dir reports/paper_cvpr
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Setup paths
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.paper_orchestra_bridge import PaperOrchestraBridge  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("GeneratePaperOrchestra")


def main():
    parser = argparse.ArgumentParser(
        description="HYPER PaperOrchestra: Automated Research Paper Generation Pipeline."
    )
    parser.add_argument(
        "--template",
        default="iclr2025",
        choices=["iclr2025", "cvpr2025"],
        help="LaTeX conference template to target (default: iclr2025).",
    )
    parser.add_argument(
        "--output-dir",
        default="reports/generated_paper",
        help="Directory to output the generated paper workspace (default: reports/generated_paper).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Synthesize raw materials, outline, and LaTeX writeup skeleton without invoking remote LLM APIs.",
    )
    parser.add_argument(
        "--writer-model",
        default="gemini-3.1-pro-preview",
        help="LLM model name for drafting and literature review.",
    )
    parser.add_argument(
        "--reflection-model",
        default="gemini-3.1-pro-preview",
        help="LLM model name for reflection and critique.",
    )
    parser.add_argument(
        "--research-cutoff",
        default=None,
        help="Year-Month cutoff date for literature review (e.g. 2024-11).",
    )
    parser.add_argument(
        "--audit-file",
        default=None,
        help="Custom path to FUNCTIONAL_REPLACEMENT_AUDIT.json.",
    )
    parser.add_argument(
        "--benchmark-file",
        default=None,
        help="Custom path to UNIVERSAL_FABRIC_BENCHMARKS.json.",
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    audit_path = Path(args.audit_file) if args.audit_file else None
    benchmark_path = Path(args.benchmark_file) if args.benchmark_file else None

    print("\n" + "=" * 70)
    print("  PROJECT LEO / HYPER -- PAPER ORCHESTRA GENERATOR")
    print("  Multi-Agent Research Paper Pipeline (Google Cloud AI Research)")
    print("=" * 70)
    print(f"Target Template : {args.template}")
    print(f"Output Directory: {output_dir.resolve()}")
    print(f"Mode            : {'DRY-RUN (Offline Skeleton)' if args.dry_run else 'FULL MULTI-AGENT SYNTHESIS'}")
    if not args.dry_run:
        print(f"Writer Model    : {args.writer_model}")
        print(f"Reflection Model: {args.reflection_model}")
    print("=" * 70 + "\n")

    bridge = PaperOrchestraBridge(repo_root=_REPO_ROOT)

    try:
        result = bridge.run_generation(
            output_dir=output_dir,
            template_name=args.template,
            dry_run=args.dry_run,
            writer_model=args.writer_model,
            reflection_model=args.reflection_model,
            research_cutoff=args.research_cutoff,
        )

        print("\n" + "=" * 70)
        print(" [SUCCESS] PaperOrchestra Pipeline Finished Successfully")
        print("=" * 70)
        print(f"Status           : {result.get('status')}")
        print(f"Mode             : {result.get('mode')}")
        print(f"Output Directory : {result.get('output_dir')}")
        print(f"LaTeX Writeup Dir: {result.get('latex_writeup_dir')}")
        if "outline_file" in result:
            print(f"Outline Artifact : {result.get('outline_file')}")
        if "final_pdf" in result:
            print(f"Compiled PDF     : {result.get('final_pdf')}")
        print("=" * 70 + "\n")
        return 0

    except Exception as exc:
        logger.error("PaperOrchestra execution failed: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
