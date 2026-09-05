"""
HYPER Agentic Skills Manager
============================
Integrates the 2,017+ local Agentic Awesome Skills (AAS) catalog into HYPER's
development workflows, Antigravity IDE (.agents/skills), and command-line interfaces.

Provides instant sub-millisecond search, bundle management, and on-demand skill
injection without polluting Git or context windows.
"""

import os
import re
import json
import shutil
from typing import List, Dict, Any, Optional
from pathlib import Path

# Security patterns for path traversal prevention (CWE-22 / CWE-73)
SKILL_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+(?:/[a-zA-Z0-9_-]+)*$")
SAFE_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")

# Paths relative to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
AAS_ROOT = PROJECT_ROOT / "agentic-awesome-skills-main"
AAS_DATA_DIR = AAS_ROOT / "data"
AAS_SKILLS_DIR = AAS_ROOT / "skills"
AAS_CATALOG_FILE = AAS_DATA_DIR / "catalog.json"
AAS_BUNDLES_FILE = AAS_DATA_DIR / "bundles.json"

STRIX_ROOT = PROJECT_ROOT / "strix-main"
STRIX_SKILLS_DIR = STRIX_ROOT / "skills"

DEFAULT_ACTIVE_DIR = PROJECT_ROOT / ".agents" / "skills"

# High-impact core foundational skills specifically curated for HYPER:
# (High-performance AI, VolumeShader 60FPS WebGL/WebGPU, FastAPI, React/Vite, Architecture & Security)
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
    "owasp-top-10-testing",
    "api-security-testing",
    "find-security-vulnerabilities-in-code",
    "fix-security-vulnerabilities-with-strix",
]


class SkillsManager:
    """Manages AAS skill discovery, search, installation, and inspection."""

    def __init__(self, active_dir: Optional[Path] = None):
        self.active_dir = active_dir or DEFAULT_ACTIVE_DIR
        self._catalog_cache: Optional[List[Dict[str, Any]]] = None
        self._bundles_cache: Optional[Dict[str, Any]] = None

    def _load_catalog(self) -> List[Dict[str, Any]]:
        """Loads and caches the 2,000+ skills catalog, augmented with Strix security skills."""
        if self._catalog_cache is not None:
            return self._catalog_cache

        skills_list: List[Dict[str, Any]] = []

        if AAS_CATALOG_FILE.exists():
            try:
                with open(AAS_CATALOG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        skills_list = list(data.get("skills", []))
                    elif isinstance(data, list):
                        skills_list = list(data)
            except Exception as e:
                print(f"[SkillsManager] Error loading catalog: {e}")

        # Seamlessly integrate Strix Autonomous Security skills into the catalog
        if STRIX_SKILLS_DIR.exists():
            existing_ids = {s.get("id") for s in skills_list}
            for d in sorted(os.listdir(STRIX_SKILLS_DIR)):
                if d in existing_ids or not SAFE_NAME_PATTERN.match(d):
                    continue
                skill_md = STRIX_SKILLS_DIR / d / "SKILL.md"
                if skill_md.is_file():
                    desc = ""
                    try:
                        with open(skill_md, "r", encoding="utf-8") as f:
                            for line in f:
                                if line.startswith("description:"):
                                    desc = line.split("description:", 1)[1].strip().strip('"\'')
                                    break
                    except Exception:
                        pass
                    skills_list.append({
                        "id": d,
                        "name": d.replace("-", " ").title(),
                        "category": "security",
                        "description": desc or f"Strix autonomous AppSec playbook for {d}",
                        "tags": ["security", "audit", "pentest", "strix", "owasp", "vulnerability"],
                        "source": "strix"
                    })

        self._catalog_cache = skills_list
        return self._catalog_cache

    def _load_bundles(self) -> Dict[str, Any]:
        """Loads and caches bundle definitions, augmented with Strix security bundle."""
        if self._bundles_cache is not None:
            return self._bundles_cache

        bundles: Dict[str, Any] = {}
        if AAS_BUNDLES_FILE.exists():
            try:
                with open(AAS_BUNDLES_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "bundles" in data:
                        bundles = dict(data["bundles"])
                    elif isinstance(data, dict):
                        bundles = dict(data)
            except Exception as e:
                print(f"[SkillsManager] Error loading bundles: {e}")

        # Add Strix Security bundle if Strix skills exist
        if STRIX_SKILLS_DIR.exists():
            strix_ids = [
                d for d in sorted(os.listdir(STRIX_SKILLS_DIR))
                if (STRIX_SKILLS_DIR / d / "SKILL.md").is_file() and SAFE_NAME_PATTERN.match(d)
            ]
            if strix_ids:
                bundles["strix-security"] = {
                    "name": "Strix Autonomous Security & Pentesting",
                    "description": "Autonomous AI penetration testing, OWASP Top 10 auditing, API security, and vulnerability remediation playbooks.",
                    "skills": strix_ids
                }

        self._bundles_cache = bundles
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

    @staticmethod
    def _is_valid_skill_id(skill_id: Any) -> bool:
        """
        Validates that skill_id is a safe relative identifier without traversal elements.
        Blocks path traversal (CWE-22 / CWE-73).
        """
        if not isinstance(skill_id, str):
            return False
        normalized = skill_id.replace("\\", "/").strip()
        if not normalized or not SKILL_ID_PATTERN.match(normalized):
            return False
        parts = normalized.split("/")
        if any(p in ("", ".", "..") for p in parts):
            return False
        return True

    def _resolve_safe_src_path(self, skill_id: str) -> Optional[Path]:
        """
        Securely resolves a skill's source directory within STRIX_SKILLS_DIR or AAS_SKILLS_DIR.
        Enforces strict path containment to prevent path traversal attacks (CWE-22/CWE-73).
        """
        if not self._is_valid_skill_id(skill_id):
            return None

        normalized = skill_id.replace("\\", "/").strip()
        parts = normalized.split("/")

        # 1. Check STRIX_SKILLS_DIR first
        if STRIX_SKILLS_DIR.exists():
            strix_base = STRIX_SKILLS_DIR.resolve()
            target_strix = strix_base.joinpath(*parts).resolve()
            try:
                target_strix.relative_to(strix_base)
                if os.path.commonpath([str(strix_base), str(target_strix)]) == str(strix_base):
                    if target_strix.exists():
                        return target_strix
            except (ValueError, TypeError):
                pass

        # 2. Check AAS_SKILLS_DIR
        if AAS_SKILLS_DIR.exists():
            base_resolved = AAS_SKILLS_DIR.resolve()
            target_path = base_resolved.joinpath(*parts).resolve()
            try:
                target_path.relative_to(base_resolved)
                if os.path.commonpath([str(base_resolved), str(target_path)]) == str(base_resolved):
                    if target_path.exists():
                        return target_path
            except (ValueError, TypeError):
                pass

        return None

    def _resolve_safe_dst_path(self, skill_id: str) -> Optional[Path]:
        """
        Securely resolves the target destination folder inside self.active_dir.
        Enforces that the destination is strictly an immediate subdirectory of active_dir.
        """
        if not self._is_valid_skill_id(skill_id):
            return None

        normalized = skill_id.replace("\\", "/").strip()
        parts = [p for p in normalized.split("/") if p and p not in (".", "..")]
        if not parts:
            return None

        leaf_name = parts[-1]
        if not SAFE_NAME_PATTERN.match(leaf_name):
            return None

        base_resolved = self.active_dir.resolve()
        target_path = (base_resolved / leaf_name).resolve()

        # Must be strictly an immediate child of active_dir (cannot be active_dir or parent)
        if target_path.parent != base_resolved or target_path == base_resolved:
            return None

        try:
            target_path.relative_to(base_resolved)
        except ValueError:
            return None

        try:
            if os.path.commonpath([str(base_resolved), str(target_path)]) != str(base_resolved):
                return None
        except (ValueError, TypeError):
            return None

        return target_path

    def get_skill_info(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves metadata and full SKILL.md for a given skill ID."""
        src_folder = self._resolve_safe_src_path(skill_id)
        if src_folder is None:
            return None

        catalog = self._load_catalog()
        skill_meta = next((s for s in catalog if s.get("id") == skill_id), None)

        skill_file = (src_folder / "SKILL.md").resolve()
        # Verify skill_file is strictly inside src_folder
        try:
            skill_file.relative_to(src_folder)
        except ValueError:
            return None

        content = ""
        if skill_file.is_file():
            try:
                with open(skill_file, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                pass

        if not skill_meta and not skill_file.exists():
            return None

        dst_folder = self._resolve_safe_dst_path(skill_id)
        is_installed = False
        if dst_folder is not None and dst_folder.exists() and dst_folder.is_dir():
            is_installed = True

        res = dict(skill_meta) if skill_meta else {"id": skill_id}
        res["path"] = str(src_folder)
        res["skill_md_content"] = content
        res["is_installed"] = is_installed
        return res

    def install(self, skill_id: str) -> bool:
        """
        Installs a skill from the AAS library directly into the workspace active skills
        directory (.agents/skills/<skill_id>) for Antigravity discovery.
        """
        src = self._resolve_safe_src_path(skill_id)
        if src is None or not src.is_dir():
            return False

        dst = self._resolve_safe_dst_path(skill_id)
        if dst is None:
            return False

        self.active_dir.mkdir(parents=True, exist_ok=True)

        if dst.exists():
            # Strict safety guard: never rmtree active_dir or anything outside it
            base_resolved = self.active_dir.resolve()
            if dst == base_resolved or dst.parent != base_resolved:
                return False
            shutil.rmtree(dst)

        shutil.copytree(src, dst)
        return True

    def uninstall(self, skill_id: str) -> bool:
        """Removes a skill from the active workspace directory."""
        dst = self._resolve_safe_dst_path(skill_id)
        if dst is None:
            return False

        if dst.exists():
            # Strict safety guard: never rmtree active_dir or anything outside it
            base_resolved = self.active_dir.resolve()
            if dst == base_resolved or dst.parent != base_resolved:
                return False
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
