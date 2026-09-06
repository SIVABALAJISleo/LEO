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
        self._allowed_ids_cache: Optional[set] = None
        self._allowed_leaves_cache: Optional[set] = None
        self._src_map_cache: Optional[Dict[str, Path]] = None
        self._dst_name_map_cache: Optional[Dict[str, str]] = None

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

    def _build_index(self) -> None:
        """
        Builds a strict whitelist index of all valid skill IDs, source paths,
        and safe destination folder names from catalog and filesystem.
        Eliminates uncontrolled data from path expressions (CWE-22 / CWE-73).
        """
        if self._allowed_ids_cache is not None:
            return

        allowed_ids: set[str] = set()
        allowed_leaves: set[str] = set()
        src_map: Dict[str, Path] = {}
        dst_name_map: Dict[str, str] = {}

        # 1. Index AAS catalog
        if AAS_CATALOG_FILE.exists():
            try:
                with open(AAS_CATALOG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    skills = data.get("skills", []) if isinstance(data, dict) else data
                    for s in skills:
                        if not isinstance(s, dict):
                            continue
                        sid = s.get("id")
                        spath = s.get("path")
                        if not sid or not isinstance(sid, str):
                            continue
                        leaf = sid.split("/")[-1]
                        if not SAFE_NAME_PATTERN.match(leaf) or os.path.basename(leaf) != leaf:
                            continue

                        folder = None
                        if spath and isinstance(spath, str):
                            candidate = (AAS_ROOT / spath).resolve().parent
                            if candidate.is_dir():
                                folder = candidate
                        if folder is None and AAS_SKILLS_DIR.exists():
                            parts = sid.split("/")
                            candidate = AAS_SKILLS_DIR.joinpath(*parts).resolve()
                            if candidate.is_dir():
                                folder = candidate

                        if folder is not None and folder.is_dir():
                            src_map[sid] = folder
                            src_map[leaf] = folder
                            dst_name_map[sid] = leaf
                            dst_name_map[leaf] = leaf
                            allowed_ids.add(sid)
                            allowed_ids.add(leaf)
                            allowed_leaves.add(leaf)
            except Exception as e:
                print(f"[SkillsManager] Error indexing catalog: {e}")

        # 2. Index Strix Skills
        if STRIX_SKILLS_DIR.exists():
            for d in STRIX_SKILLS_DIR.iterdir():
                if d.is_dir() and (d / "SKILL.md").is_file():
                    name = d.name
                    if SAFE_NAME_PATTERN.match(name) and os.path.basename(name) == name:
                        src_map[name] = d.resolve()
                        dst_name_map[name] = name
                        allowed_ids.add(name)
                        allowed_leaves.add(name)

        # 3. Index Active Directory (so already installed skills can be queried/uninstalled)
        if self.active_dir.exists():
            for d in self.active_dir.iterdir():
                if d.is_dir() and SAFE_NAME_PATTERN.match(d.name) and os.path.basename(d.name) == d.name:
                    dst_name_map[d.name] = d.name
                    allowed_ids.add(d.name)
                    allowed_leaves.add(d.name)

        # 4. Foundational skills
        for fs in FOUNDATIONAL_SKILLS:
            allowed_ids.add(fs)
            allowed_leaves.add(fs)

        self._allowed_ids_cache = allowed_ids
        self._allowed_leaves_cache = allowed_leaves
        self._src_map_cache = src_map
        self._dst_name_map_cache = dst_name_map

    def _get_allowed_skill_ids(self) -> set[str]:
        if self._allowed_ids_cache is None:
            self._build_index()
        return self._allowed_ids_cache or set()

    def _get_allowed_leaf_names(self) -> set[str]:
        if self._allowed_leaves_cache is None:
            self._build_index()
        return self._allowed_leaves_cache or set()

    def _get_src_skills_map(self) -> Dict[str, Path]:
        if self._src_map_cache is None:
            self._build_index()
        return self._src_map_cache or {}

    def _get_dst_names_map(self) -> Dict[str, str]:
        if self._dst_name_map_cache is None:
            self._build_index()
        if self.active_dir.exists() and self._dst_name_map_cache is not None and self._allowed_ids_cache is not None:
            for d in self.active_dir.iterdir():
                if d.is_dir() and SAFE_NAME_PATTERN.match(d.name):
                    self._dst_name_map_cache[d.name] = d.name
                    self._allowed_ids_cache.add(d.name)
                    if self._allowed_leaves_cache is not None:
                        self._allowed_leaves_cache.add(d.name)
        return self._dst_name_map_cache or {}

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
        Securely resolves a skill's source directory from the pre-indexed whitelist map.
        Guarantees zero uncontrolled data propagation (CWE-22 / CWE-73).
        """
        if not self._is_valid_skill_id(skill_id):
            return None

        # Whitelist barrier (CodeQL WhitelistSanitizer)
        allowed_ids = self._get_allowed_skill_ids()
        if skill_id not in allowed_ids:
            return None

        src_map = self._get_src_skills_map()
        if skill_id not in src_map:
            return None

        src_folder = src_map[skill_id]
        if not src_folder.is_dir():
            return None

        return src_folder

    def _resolve_safe_dst_path(self, skill_id: str) -> Optional[Path]:
        """
        Securely resolves the target destination folder inside self.active_dir.
        Guarantees that destination is strictly an immediate subdirectory of active_dir
        with a pre-validated whitelisted leaf name (CWE-22 / CWE-73).
        """
        if not self._is_valid_skill_id(skill_id):
            return None

        # Whitelist barrier for skill_id (CodeQL WhitelistSanitizer)
        allowed_ids = self._get_allowed_skill_ids()
        if skill_id not in allowed_ids:
            return None

        dst_map = self._get_dst_names_map()
        if skill_id not in dst_map:
            return None

        leaf_name = dst_map[skill_id]

        # Whitelist barrier for leaf_name (CodeQL WhitelistSanitizer)
        allowed_leaves = self._get_allowed_leaf_names()
        if leaf_name not in allowed_leaves:
            return None

        # Strict single-component name verification
        if not SAFE_NAME_PATTERN.match(leaf_name) or os.path.basename(leaf_name) != leaf_name:
            return None

        base_resolved = self.active_dir.resolve()
        target_path = (base_resolved / leaf_name).resolve()

        # Strict containment verification
        try:
            target_path.relative_to(base_resolved)
            if target_path.parent != base_resolved or target_path == base_resolved:
                return None
            if os.path.commonpath([str(base_resolved), str(target_path)]) != str(base_resolved):
                return None
        except (ValueError, TypeError):
            return None

        return target_path

    def get_skill_info(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves metadata and full SKILL.md for a given skill ID."""
        if not self._is_valid_skill_id(skill_id):
            return None

        allowed_ids = self._get_allowed_skill_ids()
        if skill_id not in allowed_ids:
            return None

        src_folder = self._resolve_safe_src_path(skill_id)
        if src_folder is None:
            return None

        catalog = self._load_catalog()
        skill_meta = next((s for s in catalog if s.get("id") == skill_id), None)

        skill_file = (src_folder / "SKILL.md").resolve()
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

        # Safe installation check: verify if skill directory exists in active_dir via directory enumeration
        is_installed = False
        if self.active_dir.exists():
            active_names = {d.name for d in self.active_dir.iterdir() if d.is_dir()}
            dst_folder = self._resolve_safe_dst_path(skill_id)
            if dst_folder is not None and dst_folder.name in active_names:
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
        if not self._is_valid_skill_id(skill_id):
            return False

        allowed_ids = self._get_allowed_skill_ids()
        if skill_id not in allowed_ids:
            return False

        src = self._resolve_safe_src_path(skill_id)
        if src is None or not src.is_dir():
            return False

        dst = self._resolve_safe_dst_path(skill_id)
        if dst is None:
            return False

        base_resolved = self.active_dir.resolve()
        if dst == base_resolved or dst.parent != base_resolved:
            return False

        try:
            dst.relative_to(base_resolved)
            if os.path.commonpath([str(base_resolved), str(dst)]) != str(base_resolved):
                return False
        except (ValueError, TypeError):
            return False

        self.active_dir.mkdir(parents=True, exist_ok=True)

        # If already installed, remove pre-existing directory via enumerated directory object
        active_map = {d.name: d for d in self.active_dir.iterdir() if d.is_dir()}
        if dst.name in active_map:
            existing_dir = active_map[dst.name]
            if existing_dir.resolve().parent == base_resolved:
                shutil.rmtree(existing_dir)

        shutil.copytree(src, dst)
        return True

    def uninstall(self, skill_id: str) -> bool:
        """Removes a skill from the active workspace directory."""
        if not self._is_valid_skill_id(skill_id):
            return False

        allowed_ids = self._get_allowed_skill_ids()
        if skill_id not in allowed_ids:
            return False

        dst = self._resolve_safe_dst_path(skill_id)
        if dst is None:
            return False

        if not self.active_dir.exists():
            return False

        base_resolved = self.active_dir.resolve()
        active_map = {d.name: d for d in self.active_dir.iterdir() if d.is_dir()}
        if dst.name not in active_map:
            return False

        target_dir = active_map[dst.name]
        if target_dir.resolve().parent != base_resolved or target_dir.resolve() == base_resolved:
            return False

        shutil.rmtree(target_dir)
        return True



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
