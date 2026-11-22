"""
PaperOrchestra: Multi-Agent Automated AI Research Paper Writing Framework.
Developed by Google Cloud AI Research (arXiv:2604.05018).
Integrated into Project LEO / HYPER for scientific paper orchestration.
"""

import sys
from pathlib import Path

# Ensure paper_orchestra root is in sys.path so nested references resolve cleanly
_PKG_DIR = Path(__file__).resolve().parent
if str(_PKG_DIR) not in sys.path:
    sys.path.insert(0, str(_PKG_DIR))

__version__ = "1.0.0"

__all__ = [
    "OutlineAgent",
    "HybridLiteratureAgent",
    "SectionWritingAgent",
    "ContentRefinementAgent",
    "PlottingAgent",
    "write_single_paper",
]


def __getattr__(name: str):
    if name == "OutlineAgent":
        from methods.agents.outline_agent import OutlineAgent
        return OutlineAgent
    if name == "HybridLiteratureAgent":
        from methods.agents.literature_review_agent import HybridLiteratureAgent
        return HybridLiteratureAgent
    if name == "SectionWritingAgent":
        from methods.agents.section_writing_agent import SectionWritingAgent
        return SectionWritingAgent
    if name == "ContentRefinementAgent":
        from methods.agents.content_refinement_agent import ContentRefinementAgent
        return ContentRefinementAgent
    if name == "PlottingAgent":
        from methods.agents.plotting_agent import PlottingAgent
        return PlottingAgent
    if name == "write_single_paper":
        from methods.paper_writer import write_single_paper
        return write_single_paper
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
