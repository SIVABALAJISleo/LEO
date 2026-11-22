"""
Integration tests for PaperOrchestra framework within Project LEO / HYPER.
Verifies:
1. Package imports and agent loading.
2. Conference templates (ICLR 2025, CVPR 2025).
3. HYPER <-> PaperOrchestra bridge synthesis of raw materials from audit ledgers.
4. End-to-end dry-run generation pipeline and CLI entry points.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_paper_orchestra_imports():
    """Verify PaperOrchestra package and core agent classes import cleanly."""
    import paper_orchestra
    assert hasattr(paper_orchestra, "__version__")
    assert paper_orchestra.__version__ == "1.0.0"

    from paper_orchestra import (
        OutlineAgent,
        HybridLiteratureAgent,
        SectionWritingAgent,
        ContentRefinementAgent,
        PlottingAgent,
        write_single_paper,
    )

    assert OutlineAgent is not None
    assert HybridLiteratureAgent is not None
    assert SectionWritingAgent is not None
    assert ContentRefinementAgent is not None
    assert PlottingAgent is not None
    assert callable(write_single_paper)


def test_conference_templates_exist():
    """Verify that required conference LaTeX templates are bundled and valid."""
    templates_dir = REPO_ROOT / "paper_orchestra" / "templates"
    assert templates_dir.exists(), "Templates directory must exist"

    for conf in ["iclr2025", "cvpr2025"]:
        conf_dir = templates_dir / conf
        assert conf_dir.exists(), f"Template directory for {conf} must exist"
        assert (conf_dir / "guidelines.md").exists(), f"guidelines.md must exist in {conf}"
        assert (conf_dir / "template.tex").exists(), f"template.tex must exist in {conf}"
        assert (conf_dir / "references.bib").exists(), f"references.bib must exist in {conf}"


def test_bridge_audit_loading():
    """Verify that PaperOrchestraBridge loads live or default audit ledgers."""
    from backend.paper_orchestra_bridge import PaperOrchestraBridge

    bridge = PaperOrchestraBridge(repo_root=REPO_ROOT)
    audit = bridge.load_audit_data()

    assert isinstance(audit, dict)
    assert "hardware_profile" in audit
    assert "subsystems" in audit
    hw = audit["hardware_profile"]
    assert "cpu" in hw
    assert "ram_gb" in hw


def test_bridge_synthesizes_valid_materials():
    """Verify synthesis of idea_sparse.md and experimental_log.md."""
    from backend.paper_orchestra_bridge import PaperOrchestraBridge

    bridge = PaperOrchestraBridge(repo_root=REPO_ROOT)
    audit = bridge.load_audit_data()
    bench = bridge.load_benchmark_data()

    idea = bridge.synthesize_idea_sparse(audit, bench)
    assert "Algorithmic Hardware Substitution" in idea
    assert "RAW_HARDWARE_PARITY = False" in idea
    assert "CONTRACT_PARITY = True" in idea
    assert "EXACT_COMPUTATIONAL_PARITY = True" in idea
    assert "Subsystem A" in idea
    assert "Subsystem B" in idea
    assert "Subsystem C" in idea
    assert "Subsystem D" in idea

    exp_log = bridge.synthesize_experimental_log(audit, bench)
    assert "Empirical Experimental Log" in exp_log
    assert "Hardware Environment" in exp_log
    assert "Subsystem Verification & Accuracy Audits" in exp_log
    assert "PASS" in exp_log


def test_bridge_dry_run_generation():
    """Verify end-to-end generation in dry-run mode."""
    from backend.paper_orchestra_bridge import PaperOrchestraBridge

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        bridge = PaperOrchestraBridge(repo_root=REPO_ROOT)

        result = bridge.run_generation(
            output_dir=tmp_path,
            template_name="iclr2025",
            dry_run=True,
        )

        assert result["status"] == "SUCCESS"
        assert result["mode"] == "DRY_RUN"

        # Check raw_materials
        raw_mat = tmp_path / "raw_materials"
        assert (raw_mat / "idea_sparse.md").exists()
        assert (raw_mat / "experimental_log.md").exists()
        assert (raw_mat / "figures").exists()

        # Check latex_writeup
        latex_dir = tmp_path / "latex_writeup"
        assert (latex_dir / "template.tex").exists()
        assert (latex_dir / "guidelines.md").exists()
        assert (latex_dir / "references.bib").exists()

        # Check outline
        outline_file = tmp_path / "outline.json"
        assert outline_file.exists()
        with open(outline_file, "r", encoding="utf-8") as f:
            outline_data = json.load(f)
        assert "sections" in outline_data
        assert len(outline_data["sections"]) >= 4


def test_cli_dry_run():
    """Verify that scripts/generate_paper_orchestra.py CLI executes cleanly in dry-run mode."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cli_path = REPO_ROOT / "scripts" / "generate_paper_orchestra.py"
        cmd = [
            sys.executable,
            str(cli_path),
            "--template",
            "iclr2025",
            "--output-dir",
            tmp_dir,
            "--dry-run",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
        assert proc.returncode == 0, f"CLI dry run failed: {proc.stderr}"
        assert "[SUCCESS] PaperOrchestra Pipeline Finished Successfully" in proc.stdout
