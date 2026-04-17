import logging
import re
from typing import List, Dict, Any, Optional
from backend.intelligence.reasoning import reasoning_expert

logger = logging.getLogger(__name__)

class QueryPlanner:
    """
    Decomposes complex, multi-step queries into a sequential plan of sub-queries.
    Enables better specialized retrieval and reasoning per step.
    """
    async def plan(self, query: str) -> List[str]:
        """
        Decomposes a query into sub-steps.
        """
        logger.info(f"query_planning_start: query_len={len(query)}")
        
        # In a real system, we'd use a small LLM (Task Planner) to generate these
        # Here we simulate the decomposition based on complex query markers
        if " vs " in query.lower() or " compared to " in query.lower():
            # Comparative query decomposition
            parts = re.split(r' vs | compared to ', query, flags=re.IGNORECASE)
            return [
                f"What is {parts[0].strip()}?",
                f"What is {parts[1].strip()}?",
                f"Compare {parts[0].strip()} and {parts[1].strip()} based on advantages and disadvantages."
            ]
        
        # Fallback: single step
        return [query]

    async def execute_plan(self, query: str) -> Optional[str]:
        """
        Orchestrates the execution of the plan.
        """
        steps = await self.plan(query)
        if len(steps) == 1:
            return None # Fallback to standard flow
            
        logger.info(f"executing_planned_steps: count={len(steps)}")
        results = []
        for step in steps:
            # We assume reasoning_expert can solve each sub-step
            res = await reasoning_expert.solve(step)
            results.append(res["answer"])
            
        # Final aggregation (Simplified)
        return "\n\n".join(results)


global_query_planner = QueryPlanner()
