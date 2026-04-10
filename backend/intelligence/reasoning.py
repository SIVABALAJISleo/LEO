import re
import asyncio
import logging
from typing import Dict, Any, List, Optional
from backend.core.tools import global_tools
from backend.core.memory import global_memory
from backend.data_efficiency.graph import global_graph

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
        
        # 1b. KNOWLEDGE GRAPH LOOKUP (Layer 6)
        # Attempt to find entities in the query and lookup relations
        graph_context = []
        words = re.findall(r'\b[A-Z][a-z]+\b', query) # Simple entity heuristic
        for word in words:
            relations = global_graph.query_relations(word, tenant_id)
            if relations:
                graph_context.extend([f"{word} {r['relation']} {r.get('target', r.get('source'))}" for r in relations])
        
        if graph_context:
            logger.info("knowledge_graph_hit", count=len(graph_context))
            # If we found a direct answer in the graph, we could potentially bypass here.
            # For now, we add it to context.
            context = (context or []) + graph_context

        # 1c. DIGITAL TWIN REASONING (Layer 9: Cheap Simulation)
        from backend.twin.twin_engine import global_twin_engine
        twin_result = await global_twin_engine.reason(query, context=context, tenant_id=tenant_id)
        if twin_result and twin_result["confidence"] > 0.85:
            logger.info("digital_twin_bypass_active")
            from backend.core.metrics import TWIN_HITS
            TWIN_HITS.inc()
            answer = twin_result["answer"]
            confidence = twin_result["confidence"]
        
        # 2. PLANNING (If no twin bypass)
        else:
            steps = await self.planner.plan(query)
            logger.info(f"reasoning_steps_planned: count={len(steps)}")
            
            # 3. EXECUTION WITH MODEL LADDER (tiny -> small -> large)
            if "Execute mathematical tool" in steps:
                nums = re.findall(r'\d+', query)
                if len(nums) >= 2:
                    tool_result = await global_tools.execute("calculator", {"expression": f"{nums[0]} + {nums[1]}"})
                    answer = f"Based on calculation: {tool_result}"
                    confidence = 1.0 # Tool results are deterministic
                else:
                    answer = "Required operands for calculation not found."
                    confidence = 0.5
            else:
                full_prompt = f"History:\n{history_str}\n\nContext:\n{context_str}\n\nQuestion: {query}\nAnswer:"
                
                # Tier 1: Tiny (Ultra fast)
                answer = await self.model_manager.generate_safe(full_prompt, tier="tiny")
                confidence = self.evaluator.evaluate(answer, query)
                
                # Tier 2: Small (Escalate if needed)
                if confidence < 0.7:
                    logger.info(f"escalating_to_small_model: confidence={confidence}")
                    answer = await self.model_manager.generate_safe(full_prompt, tier="small")
                    confidence = self.evaluator.evaluate(answer, query)
                
                # Tier 3: Large (Last resort)
                if confidence < 0.8:
                    logger.info(f"escalating_to_large_model: confidence={confidence}")
                    answer = await self.model_manager.generate_safe(full_prompt, tier="large")
                    confidence = self.evaluator.evaluate(answer, query)

        # 4. UPDATE MEMORY
        global_memory.add_message(session_id, tenant_id, "user", query)
        global_memory.add_message(session_id, tenant_id, "assistant", answer)
        
        return {
            "answer": answer,
            "confidence": confidence,
            "steps": steps,
            "strategy": "multi_step_reasoning"
        }

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
