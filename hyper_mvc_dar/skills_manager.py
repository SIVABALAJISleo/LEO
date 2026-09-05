"""
HYPER Agentic Skills Manager
============================
Integrates the 2,017+ local Agentic Awesome Skills (AAS) catalog into HYPER's
development workflows, Antigravity IDE (.agents/skills), and command-line interfaces.

Provides instant sub-millisecond search, bundle management, and on-demand skill
injection without polluting Git or context windows.
"""

import os
import json
import shutil
from typing import List, Dict, Any, Optional
from pathlib import Path

# Paths relative to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
AAS_ROOT = PROJECT_ROOT / "agentic-awesome-skills-main"
AAS_DATA_DIR = AAS_ROOT / "data"
AAS_SKILLS_DIR = AAS_ROOT / "skills"
AAS_CATALOG_FILE = AAS_DATA_DIR / "catalog.json"
AAS_BUNDLES_FILE = AAS_DATA_DIR / "bundles.json"

DEFAULT_ACTIVE_DIR = PROJECT_ROOT / ".agents" / "skills"

# High-impact core foundational skills specifically curated for HYPER:
# (High-performance AI, VolumeShader 60FPS WebGL/WebGPU, FastAPI, React/Vite, Architecture & Testing)
FOUNDATIONAL_SKILLS = [
    "systematic-debugging",
    "test-driven-development",
    "verification-before-completion",
    "software-architecture",
    "senior-architect",
    "react-best-practices",
    "web-design-guidelines",
    "frontend-dev-guidelines",
    "webapp-testing",
    "planning-with-files",
    "concise-planning",
    "kaizen",
    "mcp-builder",
    "fastapi-pro",
    "python-performance-optimization",
    "ui-ux-pro-max",
]


class SkillsManager:
    """Manages AAS skill discovery, search, installation, and inspection."""

    def __init__(self, active_dir: Optional[Path] = None):
        self.active_dir = active_dir or DEFAULT_ACTIVE_DIR
        self._catalog_cache: Optional[List[Dict[str, Any]]] = None
        self._bundles_cache: Optional[Dict[str, Any]] = None

    def _load_catalog(self) -> List[Dict[str, Any]]:
        """Loads and caches the 2,000+ skills catalog."""
        if self._catalog_cache is not None:
            return self._catalog_cache

        if not AAS_CATALOG_FILE.exists():
            return []

        try:
            with open(AAS_CATALOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self._catalog_cache = data.get("skills", [])
                elif isinstance(data, list):
                    self._catalog_cache = data
                else:
                    self._catalog_cache = []
        except Exception as e:
            print(f"[SkillsManager] Error loading catalog: {e}")
            self._catalog_cache = []

        return self._catalog_cache

    def _load_bundles(self) -> Dict[str, Any]:
        """Loads and caches the bundle definitions."""
        if self._bundles_cache is not None:
            return self._bundles_cache

        if not AAS_BUNDLES_FILE.exists():
            return {}

        try:
            with open(AAS_BUNDLES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "bundles" in data:
                    self._bundles_cache = data["bundles"]
                elif isinstance(data, dict):
                    self._bundles_cache = data
                else:
                    self._bundles_cache = {}
        except Exception as e:
            print(f"[SkillsManager] Error loading bundles: {e}")
            self._bundles_cache = {}

        return self._bundles_cache

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Sub-millisecond keyword search across 2,000+ skills by ID, name, description, tags.
        """
        catalog = self._load_catalog()
        if not query and not category:
            return catalog[:limit]

        query_tokens = [t.lower() for t in query.split()] if query else []
        results = []

        for skill in catalog:
            # Check category filter
            skill_cat = skill.get("category", "").lower()
            if category and category.lower() not in skill_cat:
                continue

            # Compute match score
            score = 0
            skill_id = skill.get("id", "").lower()
            skill_name = skill.get("name", "").lower()
            skill_desc = skill.get("description", "").lower()
            skill_tags = [t.lower() for t in skill.get("tags", [])]

            for token in query_tokens:
                if token == skill_id:
                    score += 100
                elif token in skill_id:
                    score += 40
                elif token in skill_name:
                    score += 30
                elif any(token in tag for tag in skill_tags):
                    score += 25
                elif token in skill_desc:
                    score += 10

            if not query_tokens or score > 0:
                results.append((score, skill))

        results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in results[:limit]]

    def get_skill_info(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves metadata and full SKILL.md for a given skill ID."""
        catalog = self._load_catalog()
        skill_meta = next((s for s in catalog if s.get("id") == skill_id), None)

        skill_folder = AAS_SKILLS_DIR / skill_id
        skill_file = skill_folder / "SKILL.md"

        content = ""
        if skill_file.exists():
            try:
                with open(skill_file, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                pass

        if not skill_meta and not skill_file.exists():
            return None

        res = dict(skill_meta) if skill_meta else {"id": skill_id}
        res["path"] = str(skill_folder)
        res["skill_md_content"] = content
        res["is_installed"] = (self.active_dir / skill_id).exists()
        return res

    def install(self, skill_id: str) -> bool:
        """
        Installs a skill from the AAS library directly into the workspace active skills
        directory (.agents/skills/<skill_id>) for Antigravity discovery.
        """
        parts = skill_id.replace("\\", "/").split("/")
        src = AAS_SKILLS_DIR / skill_id
        if not src.exists():
            src = AAS_SKILLS_DIR.joinpath(*parts)
            if not src.exists():
                return False

        self.active_dir.mkdir(parents=True, exist_ok=True)
        dst = self.active_dir / parts[-1]

        if dst.exists():
            shutil.rmtree(dst)

        shutil.copytree(src, dst)
        return True

    def uninstall(self, skill_id: str) -> bool:
        """Removes a skill from the active workspace directory."""
        parts = skill_id.replace("\\", "/").split("/")
        dst = self.active_dir / parts[-1]
        if dst.exists():
            shutil.rmtree(dst)
            return True
        return False


    def list_active(self) -> List[Dict[str, Any]]:
        """Lists all skills currently active in the workspace (.agents/skills)."""
        if not self.active_dir.exists():
            return []

        active = []
        for item in sorted(os.listdir(self.active_dir)):
            skill_folder = self.active_dir / item
            skill_file = skill_folder / "SKILL.md"
            if skill_folder.is_dir() and skill_file.exists():
                # Extract frontmatter summary if available
                desc = ""
                risk = "normal"
                try:
                    with open(skill_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        in_fm = False
                        for l in lines:
                            if l.strip() == "---":
                                if not in_fm:
                                    in_fm = True
                                    continue
                                else:
                                    break
                            if in_fm:
                                if l.startswith("description:"):
                                    desc = l.split("description:", 1)[1].strip().strip('"\'')
                                elif l.startswith("risk:"):
                                    risk = l.split("risk:", 1)[1].strip()
                except Exception:
                    pass

                active.append({
                    "id": item,
                    "description": desc or "Active skill playbook",
                    "risk": risk,
                    "path": str(skill_folder)
                })

        return active

    def list_bundles(self) -> List[Dict[str, Any]]:
        """Lists all pre-configured domain bundles."""
        bundles = self._load_bundles()
        result = []
        for name, data in bundles.items():
            if isinstance(data, dict):
                skills = data.get("skills", [])
                desc = data.get("description", "")
            elif isinstance(data, list):
                skills = data
                desc = ""
            else:
                continue

            result.append({
                "id": name,
                "name": name.replace("-", " ").title(),
                "description": desc,
                "skill_count": len(skills),
                "sample_skills": skills[:5]
            })
        return result

    def install_bundle(self, bundle_id: str) -> List[str]:
        """Installs all skills belonging to a specified bundle."""
        bundles = self._load_bundles()
        if bundle_id not in bundles:
            return []

        data = bundles[bundle_id]
        if isinstance(data, dict):
            skill_list = data.get("skills", [])
        elif isinstance(data, list):
            skill_list = data
        else:
            return []

        installed = []
        for s in skill_list:
            if self.install(s):
                installed.append(s)

        return installed


    def bootstrap_foundational(self) -> List[str]:
        """
        Activates the essential high-impact core skills for HYPER.
        """
        activated = []
        for s in FOUNDATIONAL_SKILLS:
            if self.install(s):
                activated.append(s)
        return activated


# Singleton instance
skills_manager = SkillsManager()
