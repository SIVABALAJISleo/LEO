"""
Answer Enhancement Engine (DLSS-style)
Orchestrates the full enhancement pipeline:
rough answer → quality check → expand → refine → return

CRITICAL: Enhancement must NOT call any large models.
All improvements are lightweight, deterministic, and sub-millisecond.
"""
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class AnswerEnhancer:
    """
    Master enhancer that orchestrates quality estimation, expansion, and refinement.
    Analogous to GPU DLSS: takes a "low-res" answer and upscales it without re-rendering.
    """

    def __init__(self):
        from backend.enhancement.quality_estimator import global_quality_estimator
        from backend.enhancement.expander import global_expander
        from backend.enhancement.refiner import global_refiner
        self.quality = global_quality_estimator
        self.expander = global_expander
        self.refiner = global_refiner

    def enhance(
        self,
        answer: str,
        query: str = "",
        context_docs: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Full enhancement pipeline. Returns enhanced answer and quality metadata.
        """
        # Step 1: Estimate quality
        quality_report = self.quality.estimate(answer, query)

        if not quality_report["needs_enhancement"]:
            logger.debug("enhancement_skipped: quality sufficient")
            return {
                "answer": answer,
                "enhanced": False,
                "quality_score": quality_report["score"],
            }

        issues = quality_report["issues"]
        enhanced = answer

        # Step 2: Expand if too short or vague
        if context_docs and ("too_short" in issues or "vague" in issues):
            enhanced = self.expander.expand(enhanced, context_docs, issues)

        # Step 3: Refine for grammar and clarity
        enhanced = self.refiner.refine(enhanced, issues)

        # Step 4: Re-estimate quality post-enhancement
        final_quality = self.quality.estimate(enhanced, query)

        logger.info(
            f"enhancement_complete: "
            f"score_before={quality_report['score']} "
            f"score_after={final_quality['score']} "
            f"issues={issues}"
        )

        return {
            "answer": enhanced,
            "enhanced": True,
            "quality_score": final_quality["score"],
            "issues_fixed": issues,
        }


global_enhancer = AnswerEnhancer()
