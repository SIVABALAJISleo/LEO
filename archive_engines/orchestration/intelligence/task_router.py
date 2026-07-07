import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class TaskRouter:
    """
    Decomposes complex orchestrator inputs into sub-tasks and 
    routes them to specialized experts or pipelines.
    """
    def __init__(self):
        # Mapping of keywords to expert types
        self.expert_map = {
            "render": "vision",
            "draw": "vision",
            "image": "vision",
            "calculate": "logic",
            "math": "logic",
            "solve": "logic",
            "search": "rag",
            "find": "rag",
            "know": "rag",
            "explain": "rag"
        }

    def decompose(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Splits a prompt into task chunks. 
        Example: "Render a 4K scene and explain the math" -> 
        [Task(Vision, Render), Task(Logic, Explain Math)]
        """
        prompt_lower = prompt.lower()
        tasks = []
        
        # Simple rule-based decomposition for now
        # In a full-scale system, this would use a tiny local LLM (e.g. Phi-2/3)
        parts = prompt.split(" and ") if " and " in prompt_lower else [prompt]
        
        for part in parts:
            assigned_expert = "general"
            for keyword, expert in self.expert_map.items():
                if keyword in part.lower():
                    assigned_expert = expert
                    break
            
            tasks.append({
                "task": part.strip(),
                "expert": assigned_expert,
                "priority": "medium"
            })
            
        logger.info(f"Decomposed prompt into {len(tasks)} tasks.")
        return tasks

    async def compose_results(self, task_results: List[Dict[str, Any]]) -> str:
        """
        Unifies multiple expert outputs into a coherent final answer.
        """
        logger.info("Composing final result from expert outputs.")
        # Simulating composition logic
        composed = "\n\n".join([f"[{r['expert'].upper()}] {r['output']}" for r in task_results])
        return composed

if __name__ == "__main__":
    router = TaskRouter()
    prompt = "Render a forest and explain the photosynthesis math"
    tasks = router.decompose(prompt)
    print(f"Tasks: {tasks}")
