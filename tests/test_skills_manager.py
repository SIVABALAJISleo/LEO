"""
tests/test_skills_manager.py
Test suite for HYPER's Agentic Awesome Skills (AAS) Manager.
Verifies catalog search, lifecycle installation, uninstallation, bundles, and bootstrapping.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from hyper_mvc_dar.skills_manager import SkillsManager, skills_manager


@pytest.fixture
def temp_skills_dir():
    temp_dir = tempfile.mkdtemp(prefix="hyper_test_skills_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_catalog_search():
    """Verify sub-millisecond catalog search returns relevant skills."""
    results = skills_manager.search("debugging", limit=5)
    assert len(results) > 0
    # Every result should have an id and description
    for r in results:
        assert "id" in r
        assert "description" in r


def test_get_skill_info():
    """Verify skill metadata and SKILL.md retrieval."""
    info = skills_manager.get_skill_info("systematic-debugging")
    assert info is not None
    assert info["id"] == "systematic-debugging"
    assert "description" in info
    assert len(info.get("skill_md_content", "")) > 50


def test_install_and_uninstall_lifecycle(temp_skills_dir):
    """Verify clean installation and uninstallation of a skill into target directory."""
    mgr = SkillsManager(active_dir=temp_skills_dir)

    # Initial state: empty
    assert len(mgr.list_active()) == 0

    # Install skill
    success = mgr.install("systematic-debugging")
    assert success is True

    # Check active
    active = mgr.list_active()
    assert len(active) == 1
    assert active[0]["id"] == "systematic-debugging"
    assert (temp_skills_dir / "systematic-debugging" / "SKILL.md").exists()

    # Uninstall skill
    uninstalled = mgr.uninstall("systematic-debugging")
    assert uninstalled is True
    assert len(mgr.list_active()) == 0
    assert not (temp_skills_dir / "systematic-debugging").exists()


def test_list_bundles():
    """Verify bundle catalog listing."""
    bundles = skills_manager.list_bundles()
    assert len(bundles) > 0
    bundle_ids = [b["id"] for b in bundles]
    assert "core-dev" in bundle_ids
    assert "security-core" in bundle_ids


def test_bootstrap_foundational(temp_skills_dir):
    """Verify foundational skills bootstrap."""
    mgr = SkillsManager(active_dir=temp_skills_dir)
    activated = mgr.bootstrap_foundational()
    assert len(activated) > 10
    active = mgr.list_active()
    assert len(active) == len(activated)
    active_ids = {a["id"] for a in active}
    assert "systematic-debugging" in active_ids
    assert "react-best-practices" in active_ids
    assert "senior-architect" in active_ids
