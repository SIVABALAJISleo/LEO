import re
import asyncio
import logging
from typing import Dict, Any, List, Optional
from backend.core.tools import global_tools
from backend.core.memory import global_memory

logger = logging.getLogger(__name__)

class SelfEvaluationLayer:
    """Performs quality checks on generated answers."""
    def evaluate(self, answer: str, query: str) -> float:
        if not answer or len(answer) < 5:
            return 0.0
        
        # Heuristic quality check: Does it address the query?
        query_words = set(re.findall(r'\w+', query.lower()))
        answer_words = set(re.findall(r'\w+', answer.lower()))
        overlap = len(query_words.intersection(answer_words)) / max(len(query_words), 1)
        
        # Length and structure check
        score = 0.5 + (overlap * 0.5)
        if len(answer) > 20: score += 0.1
        return min(1.0, score)

class MultiStepReasoningEngine:
    """Decomposes complex queries into logical steps."""
    def __init__(self, model_manager=None):
        self.model_manager = model_manager

    async def plan(self, query: str) -> List[str]:
        # In a real system, this would use an LLM to generate a plan.
        # Here we use a heuristic based on keywords.
        if any(w in query.lower() for w in ["calculate", "math", "add", "sum"]):
            return ["Identify numbers and operation", "Execute mathematical tool", "Summarize result"]
        if any(w in query.lower() for w in ["status", "how", "why"]):
            return ["Analyze system context", "Isolate key variables", "Synthesize explanation"]
        return ["Process query directly"]

class ReasoningExpert:
    """
    Advanced Reasoning Engine v3.
    Integrates Multi-Step Planning, Tool Execution, and Memory.
    """
    def __init__(self):
        from backend.core.model_manager import model_manager
        self.model_manager = model_manager
        self.planner = MultiStepReasoningEngine(model_manager)
        self.evaluator = SelfEvaluationLayer()

    async def solve(self, query: str, context: List[str] = None, session_id: str = "default", tenant_id: str = "default") -> Dict[str, Any]:
        logger.info(f"reasoning_expert_active: query={query}")
        
        # 1. RETRIEVE MEMORY
        history = global_memory.get_history(session_id, tenant_id)
        context_str = " ".join(context) if context else ""
        history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history])
        
        # 2. PLANNING
        steps = await self.planner.plan(query)
        logger.info(f"reasoning_steps_planned: count={len(steps)}")
        
        # 3. EXECUTION (Simplified Multi-Step)
        if "Execute mathematical tool" in steps:
            # Heuristic tool extraction
            nums = re.findall(r'\d+', query)
            if len(nums) >= 2:
                # Mock tool call for demonstration
                tool_result = await global_tools.execute("calculator", {"expression": f"{nums[0]} + {nums[1]}"})
                answer = f"Based on calculation: {tool_result}"
            else:
                answer = "Required operands for calculation not found."
        else:
            # Direct Model Inference with context and history
            full_prompt = f"History:\n{history_str}\n\nContext:\n{context_str}\n\nQuestion: {query}\nAnswer:"
            answer = await self.model_manager.generate_safe(full_prompt)

        # 4. SELF-EVALUATION
        confidence = self.evaluator.evaluate(answer, query)
        
        # 5. UPDATE MEMORY
        global_memory.add_message(session_id, tenant_id, "user", query)
        global_memory.add_message(session_id, tenant_id, "assistant", answer)

    async def solve_stream(self, query: str, context: List[str] = None, session_id: str = "default", tenant_id: str = "default"):
        """Streaming version of solve."""
        logger.info(f"reasoning_expert_stream_active: query={query}")
        
        # 1. RETRIEVE MEMORY
        history = global_memory.get_history(session_id, tenant_id)
        context_str = " ".join(context) if context else ""
        history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history])
        
        # 2. PLANNING (Sync/Fast enough to not stream)
        steps = await self.planner.plan(query)
        
        # 3. YIELD INITIAL METADATA (Optional but helpful for UI)
        yield f"__PLAN__: {','.join(steps)}\n"

        # 4. EXECUTION
        if "Execute mathematical tool" in steps:
            nums = re.findall(r'\d+', query)
            if len(nums) >= 2:
                tool_result = await global_tools.execute("calculator", {"expression": f"{nums[0]} + {nums[1]}"})
                answer = f"Based on calculation: {tool_result}"
                yield answer
            else:
                answer = "Required operands for calculation not found."
                yield answer
        else:
            # Direct Streaming Model Inference
            full_prompt = f"History:\n{history_str}\n\nContext:\n{context_str}\n\nQuestion: {query}\nAnswer:"
            full_answer = ""
            async for chunk in self.model_manager.generate_stream(full_prompt):
                full_answer += chunk
                yield chunk
            answer = full_answer

        # 5. UPDATE MEMORY (After streaming complete)
        global_memory.add_message(session_id, tenant_id, "user", query)
        global_memory.add_message(session_id, tenant_id, "assistant", answer)

reasoning_expert = ReasoningExpert()
