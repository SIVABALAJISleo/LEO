"""
backend/intelligence/intent_trajectory.py

Intent Trajectory Engine (AIS++ Module 1)
==========================================
Predicts the FULL SEQUENCE of user queries (multi-step intent chain),
not just the next query. Precomputes the entire trajectory so every
subsequent question is already answered before it is asked.

Example trajectory for "What is RAG?":
  Step 1  → What is RAG?
  Step 2  → How does RAG work?
  Step 3  → When should I use RAG?
  Step 4  → RAG vs fine-tuning?
  Step 5  → How to implement RAG in Python?
  Step 6  → RAG performance benchmarks
  Step 7  → Scaling RAG in production

Rules:
  - Trajectory computed once per intent (zero-repeat)
  - All steps enqueued for background precompute
  - Session context drives trajectory personalization
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict

logger = logging.getLogger(__name__)

# ── Intent chain templates (intent → ordered progression) ─────────────────────
TRAJECTORY_CHAINS: Dict[str, List[str]] = {
    "definition": [
        "definition",
        "how_it_works",
        "when_to_use",
        "comparison",
        "implementation",
        "advanced_usage",
        "production_tips",
    ],
    "how_to": [
        "prerequisites",
        "step_by_step",
        "common_errors",
        "optimization",
        "production_tips",
        "alternatives",
    ],
    "comparison": [
        "individual_a",
        "individual_b",
        "use_case_a",
        "use_case_b",
        "performance_benchmark",
        "recommendation",
    ],
    "troubleshoot": [
        "root_cause",
        "diagnosis",
        "fix",
        "prevention",
        "monitoring",
    ],
    "benefit": [
        "core_benefits",
        "quantitative_gains",
        "case_studies",
        "trade_offs",
        "recommendation",
    ],
    "calculation": [
        "formula",
        "worked_example",
        "edge_cases",
        "optimization",
    ],
    "general": [
        "overview",
        "deeper_dive",
        "practical_application",
        "related_topics",
    ],
}

# Templates for generating step queries from entity + step_type
STEP_TEMPLATES: Dict[str, str] = {
    "definition":         "What is {entity}?",
    "how_it_works":       "How does {entity} work?",
    "when_to_use":        "When should I use {entity}?",
    "comparison":         "{entity} vs alternatives — which to choose?",
    "implementation":     "How to implement {entity} step by step?",
    "advanced_usage":     "Advanced {entity} techniques and patterns",
    "production_tips":    "How to run {entity} in production?",
    "prerequisites":      "What do I need to know before using {entity}?",
    "step_by_step":       "Step-by-step guide to {entity}",
    "common_errors":      "Common errors with {entity} and how to fix them",
    "optimization":       "How to optimize {entity} performance?",
    "alternatives":       "What are the alternatives to {entity}?",
    "individual_a":       "Detailed overview of {entity}",
    "individual_b":       "How {entity} compares to similar tools",
    "use_case_a":         "Best use cases for {entity}",
    "use_case_b":         "When NOT to use {entity}",
    "performance_benchmark": "{entity} performance benchmarks and metrics",
    "recommendation":     "Should I use {entity}? Final recommendation",
    "root_cause":         "Why does {entity} fail or cause errors?",
    "diagnosis":          "How to diagnose {entity} problems?",
    "fix":                "How to fix {entity} issues?",
    "prevention":         "How to prevent {entity} problems?",
    "monitoring":         "How to monitor {entity} in production?",
    "core_benefits":      "Key benefits of using {entity}",
    "quantitative_gains": "Measurable improvements from {entity}",
    "case_studies":       "Real-world {entity} success stories",
    "trade_offs":         "Trade-offs and limitations of {entity}",
    "formula":            "{entity} formula and calculation method",
    "worked_example":     "{entity} worked example with numbers",
    "edge_cases":         "{entity} edge cases and corner cases",
    "overview":           "Overview of {entity}",
    "deeper_dive":        "Deep dive into {entity} internals",
    "practical_application": "Practical applications of {entity}",
    "related_topics":     "Topics related to {entity}",
    "prerequisites":      "Prerequisites for {entity}",
}


class IntentTrajectoryEngine:
    """
    Predicts and precomputes full multi-step intent chains.
    Ensures the entire expected session is resolved before the user asks.
    """

    def __init__(self):
        # Track which (family_id) trajectories have been launched
        self._launched: Set[str] = set()
        # session_id → list of predicted trajectory steps
        self._session_trajectories: Dict[str, List[str]] = defaultdict(list)
        self._trajectories_computed: int = 0

    # ── Trajectory Generation ──────────────────────────────────────────────── #

    def generate_trajectory(
        self,
        entity: str,
        intent: str,
        session_id: str,
        family_id: str,
    ) -> Dict[str, Any]:
        """
        Generates a full intent chain for the given entity+intent combination.
        Returns ordered list of queries representing the predicted session flow.
        """
        chain_steps = TRAJECTORY_CHAINS.get(intent, TRAJECTORY_CHAINS["general"])
        entity_clean = entity.lower().replace("_", " ")

        trajectory: List[str] = []
        for step in chain_steps:
            template = STEP_TEMPLATES.get(step, "Tell me more about {entity}")
            query = template.format(entity=entity_clean)
            trajectory.append(query)

        # Personalize using session history
        history = self._session_trajectories.get(session_id, [])
        if history:
            # Skip steps the user already asked
            seen = {q.lower() for q in history}
            trajectory = [q for q in trajectory if q.lower() not in seen]

        # Store predicted trajectory for this session
        self._session_trajectories[session_id].extend(trajectory)

        logger.debug(
            f"trajectory.generated: family={family_id} "
            f"intent={intent} entity={entity} steps={len(trajectory)}"
        )
        return {
            "family_id": family_id,
            "entity": entity,
            "intent": intent,
            "steps": trajectory,
            "total_steps": len(trajectory),
        }

    # ── Background Precompute ─────────────────────────────────────────────── #

    async def precompute_trajectory(
        self,
        entity: str,
        intent: str,
        session_id: str,
        family_id: str,
        tenant_id: str,
        bg_compute,
    ) -> None:
        """
        Enqueues ALL trajectory steps for background precompute.
        Skips if already launched for this family (zero-repeat guarantee).
        """
        if family_id in self._launched:
            logger.debug(f"trajectory.skip: family={family_id} already launched")
            return

        self._launched.add(family_id)
        traj = self.generate_trajectory(entity, intent, session_id, family_id)

        for step_query in traj["steps"]:
            try:
                asyncio.create_task(
                    bg_compute.enqueue(
                        step_query,
                        tenant_id,
                        "TRAJECTORY_ENGINE",
                        session_id,
                        priority="trajectory",
                    )
                )
            except Exception as exc:
                logger.warning(f"trajectory.enqueue_error: step='{step_query}' err={exc}")

        self._trajectories_computed += 1
        logger.info(
            f"trajectory.launched: family={family_id} "
            f"steps={traj['total_steps']} total_launched={self._trajectories_computed}"
        )

    def log_query(self, session_id: str, query: str) -> None:
        """Records that this query was asked in this session."""
        self._session_trajectories[session_id].append(query)

    def get_next_predicted(self, session_id: str) -> Optional[str]:
        """Returns the next predicted query in the session trajectory, if any."""
        history = self._session_trajectories.get(session_id, [])
        return history[-1] if history else None

    def stats(self) -> Dict[str, Any]:
        return {
            "launched_trajectories": len(self._launched),
            "active_sessions": len(self._session_trajectories),
            "total_trajectories_computed": self._trajectories_computed,
        }


global_intent_trajectory = IntentTrajectoryEngine()
