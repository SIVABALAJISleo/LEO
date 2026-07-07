import logging
from intel_core_ai.inference import IntelInferenceEngine
from archive_engines.llm_os_intel.memory import LLMOSMemory

logger = logging.getLogger(__name__)

class IterativeReasoningEngine:
    """
    LAYER 4: ITERATIVE REASONING LOOP (CORE ENGINE)
    Executes a multi-pass pipeline to expand intelligence across time.
    """
    def __init__(self, inference: IntelInferenceEngine, memory: LLMOSMemory):
        self.inference = inference
        self.memory = memory
        self.passes = [
            ("concepts", "Extract key concepts and entities from the query."),
            ("domain_a", "Analyze the first major domain identified in the concepts."),
            ("domain_b", "Analyze the second major domain identified in the concepts."),
            ("relationships", "Identify hidden relationships and contradictions between Domain A and Domain B."),
            ("synthesis", "Synthesize all insights into a unified, high-level perspective."),
            ("refinement", "Refine the synthesis into a polished, concise final response.")
        ]

    async def run_pass(self, pass_key: str, instruction: str, query: str) -> str:
        """
        Executes a single pass, reading from memory and writing back.
        """
        working_memory = self.memory.get_full_context()
        system_prompt = (
            f"You are part of an Iterative Reasoning Engine (Pass: {pass_key}).\n"
            f"Instruction: {instruction}\n"
            f"Current Working Memory:\n{working_memory}"
        )
        
        # We collect the full response for each internal pass
        response_gen = self.inference.generate_stream(query, system_prompt)
        content = "".join(list(response_gen))
        
        # Write back to scratchpad
        self.memory.scratchpad[pass_key] = content.strip()
        return content.strip()
