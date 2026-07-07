import json
import logging
from typing import Dict, Any
from intel_core_ai.inference import IntelInferenceEngine
from archive_engines.hyper_core_ai.memory import HyperMemory

logger = logging.getLogger(__name__)

class HyperKernel:
    """
    LAYER 3 & 6: MULTI-PASS REASONING & INTENT COLLAPSE
    Decomposes problems and runs the iterative solver loop.
    """
    def __init__(self, inference: IntelInferenceEngine, memory: HyperMemory):
        self.inference = inference
        self.memory = memory

    def collapse_intent(self, query: str) -> Dict[str, Any]:
        """
        LAYER 6: INTENT COLLAPSE
        Parses query into structured goal and subtasks.
        """
        system_prompt = (
            "Analyze the query. Decompose into a single GOAL and a list of SUBTASKS.\n"
            "Output ONLY valid JSON: {\"goal\": \"...\", \"subtasks\": [\"...\", \"...\"], \"need_math\": bool}"
        )
        gen = self.inference.generate_stream(query, system_prompt)
        res = "".join(list(gen))
        try:
            start = res.find("{")
            end = res.rfind("}") + 1
            return json.loads(res[start:end])
        except:
            return {"goal": query, "subtasks": ["Answer directly"], "need_math": False}

    async def solve_subtask(self, subtask: str, query: str) -> str:
        """
        Executes a single reasoning pass for a subtask.
        """
        scratchpad = self.memory.get_scratchpad_string()
        system_prompt = (
            f"Solve the subtask: {subtask}\n"
            f"Current Context:\n{scratchpad}"
        )
        gen = self.inference.generate_stream(query, system_prompt)
        return "".join(list(gen)).strip()

    def synthesize(self, query: str) -> str:
        """
        Final synthesis pass.
        """
        scratchpad = self.memory.get_scratchpad_string()
        system_prompt = (
            "Synthesize the intermediate results into a final, polished answer.\n"
            f"Reasoning Steps:\n{scratchpad}"
        )
        return "".join(list(self.inference.generate_stream(query, system_prompt))).strip()
