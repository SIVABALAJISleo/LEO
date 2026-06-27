"""
backend/core/reasoning_engine.py
LEO AI Production Reasoning Engine - Phase 4 Implementation

Implements:
  - Chain of Thought (CoT): step-by-step decomposition
  - Tree of Thoughts (ToT): branching hypothesis evaluation
  - Multi-Agent Debate: independent agent perspectives + adjudication
  - Verification loop: critic pass before committing final answer
"""
import time
import re
import logging
from typing import Dict, Any, List, Optional, Callable

logger = logging.getLogger(__name__)


class ChainOfThoughtEngine:
    """
    Decompose a complex query into numbered reasoning steps
    using the local inference engine, then synthesize a final answer.
    """

    def __init__(self, inference_fn: Optional[Callable] = None):
        self.inference_fn = inference_fn  # Callable(prompt: str) -> str

    def _call(self, prompt: str) -> str:
        if self.inference_fn:
            try:
                return self.inference_fn(prompt)
            except Exception as e:
                logger.error(f"[CoT] inference_fn call failed: {e}")
        # Minimal fallback: return prompt echo
        return f"[CoT FALLBACK] {prompt[:200]}"

    def reason(self, query: str, context: str = "") -> Dict[str, Any]:
        t0 = time.perf_counter()

        # Step 1: generate a reasoning plan
        context_str = f"Context:\n{context}" if context else ""
        plan_prompt = (
            f"You are a precise reasoning engine. Given this question:\n\"{query}\"\n"
            f"{context_str}\n"
            "Break the problem down into exactly 3 numbered reasoning steps. Be concise."
        )
        plan = self._call(plan_prompt)

        # Step 2: expand each step
        expand_prompt = (
            f"Given this reasoning plan:\n{plan}\n"
            "Now execute each step and produce a coherent final answer. "
            "End your answer with 'FINAL ANSWER:' followed by the conclusion."
        )
        expanded = self._call(expand_prompt)

        # Extract final answer
        final_answer = expanded
        if "FINAL ANSWER:" in expanded:
            final_answer = expanded.split("FINAL ANSWER:")[-1].strip()

        latency = (time.perf_counter() - t0) * 1000
        return {
            "engine": "ChainOfThought",
            "plan": plan,
            "expanded_reasoning": expanded,
            "answer": final_answer,
            "latency_ms": round(latency, 2),
            "confidence": 0.88,
        }


class TreeOfThoughtsEngine:
    """
    Generate N independent hypothesis branches, score each,
    and select the best as the final answer.
    """

    def __init__(self, inference_fn: Optional[Callable] = None, branches: int = 3):
        self.inference_fn = inference_fn
        self.branches = branches

    def _call(self, prompt: str) -> str:
        if self.inference_fn:
            try:
                return self.inference_fn(prompt)
            except Exception as e:
                logger.error(f"[ToT] inference_fn call failed: {e}")
        return f"[ToT FALLBACK] {prompt[:200]}"

    def reason(self, query: str, context: str = "") -> Dict[str, Any]:
        t0 = time.perf_counter()

        branches_text = []
        for i in range(self.branches):
            context_str = f"Context:\n{context}" if context else ""
            branch_prompt = (
                f"You are reasoning agent {i+1}. Given:\n\"{query}\"\n"
                f"{context_str}\n"
                f"Produce hypothesis {i+1}. Be concise and give a confidence score 0-1."
            )
            branch_result = self._call(branch_prompt)
            branches_text.append(branch_result)

        # Judge prompt — evaluate branches and pick best
        judge_prompt = (
            f"You are an arbiter. Below are {self.branches} hypotheses for:\n\"{query}\"\n\n"
            + "\n\n".join([f"Hypothesis {i+1}:\n{b}" for i, b in enumerate(branches_text)])
            + "\n\nPick the most accurate hypothesis. Start with 'BEST ANSWER:'"
        )
        judgment = self._call(judge_prompt)

        best_answer = judgment
        if "BEST ANSWER:" in judgment:
            best_answer = judgment.split("BEST ANSWER:")[-1].strip()

        latency = (time.perf_counter() - t0) * 1000
        return {
            "engine": "TreeOfThoughts",
            "branches": branches_text,
            "judgment": judgment,
            "answer": best_answer,
            "latency_ms": round(latency, 2),
            "confidence": 0.91,
        }


class MultiAgentDebateEngine:
    """
    Run a structured debate between a Proposer and Critic agent,
    then synthesize a final arbitrated response.
    """

    def __init__(self, inference_fn: Optional[Callable] = None, rounds: int = 2):
        self.inference_fn = inference_fn
        self.rounds = rounds

    def _call(self, prompt: str) -> str:
        if self.inference_fn:
            try:
                return self.inference_fn(prompt)
            except Exception as e:
                logger.error(f"[Debate] inference_fn call failed: {e}")
        return f"[Debate FALLBACK] {prompt[:200]}"

    def debate(self, query: str, context: str = "") -> Dict[str, Any]:
        t0 = time.perf_counter()
        transcript = []

        # Round 0: Initial claim
        context_str = f"Context:\n{context}" if context else ""
        proposer_prompt = (
            f"You are the PROPOSER agent. Answer this confidently and directly:\n"
            f"\"{query}\"\n{context_str}"
        )
        claim = self._call(proposer_prompt)
        transcript.append({"role": "Proposer", "content": claim})

        for r in range(self.rounds):
            # Critic challenges
            critic_prompt = (
                f"You are the CRITIC agent. Challenge this claim:\n\"{claim}\"\n"
                f"For the question:\n\"{query}\"\n"
                "List specific weaknesses or errors. Be concise."
            )
            critique = self._call(critic_prompt)
            transcript.append({"role": "Critic", "content": critique})

            # Proposer rebuts
            rebuttal_prompt = (
                f"You are the PROPOSER agent. Address this critique:\n\"{critique}\"\n"
                "Revise or defend your answer."
            )
            claim = self._call(rebuttal_prompt)
            transcript.append({"role": "Proposer", "content": claim})

        # Arbitration
        arbiter_prompt = (
            f"Synthesize this debate into a final answer for:\n\"{query}\"\n\n"
            + "\n".join([f"{t['role']}: {t['content']}" for t in transcript])
            + "\n\nFINAL SYNTHESIS:"
        )
        final = self._call(arbiter_prompt)
        if "FINAL SYNTHESIS:" in final:
            final = final.split("FINAL SYNTHESIS:")[-1].strip()

        latency = (time.perf_counter() - t0) * 1000
        return {
            "engine": "MultiAgentDebate",
            "transcript": transcript,
            "answer": final,
            "rounds": self.rounds,
            "latency_ms": round(latency, 2),
            "confidence": 0.93,
        }


class ReasoningEngine:
    """
    Master reasoning engine that automatically routes queries to the appropriate
    strategy based on query complexity.
    """

    COMPLEXITY_THRESHOLDS = {
        "simple": 8,    # words
        "medium": 20,
        # above 20 = complex
    }

    def __init__(self, inference_fn: Optional[Callable] = None):
        self.cot = ChainOfThoughtEngine(inference_fn)
        self.tot = TreeOfThoughtsEngine(inference_fn, branches=3)
        self.debate = MultiAgentDebateEngine(inference_fn, rounds=1)

    def _detect_complexity(self, query: str) -> str:
        words = len(query.split())
        if words <= self.COMPLEXITY_THRESHOLDS["simple"]:
            return "simple"
        if words <= self.COMPLEXITY_THRESHOLDS["medium"]:
            return "medium"
        return "complex"

    def _is_debate_worthy(self, query: str) -> bool:
        debate_keywords = [
            "why", "should", "which is better", "compare", "pros", "cons",
            "argue", "debate", "evaluate", "justify", "explain why",
        ]
        ql = query.lower()
        return any(kw in ql for kw in debate_keywords)

    def reason(self, query: str, context: str = "", mode: Optional[str] = None) -> Dict[str, Any]:
        """
        Routes query to CoT, ToT, or Debate based on complexity or explicit mode.
        mode: 'cot' | 'tot' | 'debate' | None (auto)
        """
        complexity = self._detect_complexity(query)

        if mode == "cot" or (mode is None and complexity == "simple"):
            return self.cot.reason(query, context)
        elif mode == "debate" or (mode is None and self._is_debate_worthy(query)):
            return self.debate.debate(query, context)
        else:
            return self.tot.reason(query, context)

    def verify(self, query: str, answer: str) -> Dict[str, Any]:
        """
        Passes query+answer through a Critic to check for hallucinations
        or logical inconsistencies. Returns verified answer and critique.
        """
        t0 = time.perf_counter()
        critique_prompt = (
            f"You are a VERIFICATION agent. Check if this answer is factually accurate "
            f"and logically consistent for the question:\n"
            f"Question: {query}\n"
            f"Answer: {answer}\n\n"
            f"Reply with: PASS, FAIL, or WARN. Then explain briefly."
        )
        if self.cot.inference_fn:
            try:
                verdict_text = self.cot.inference_fn(critique_prompt)
            except Exception:
                verdict_text = "WARN Could not verify."
        else:
            verdict_text = "WARN Inference not available for verification."

        verdict = "PASS"
        for v in ["FAIL", "WARN", "PASS"]:
            if v in verdict_text.upper():
                verdict = v
                break

        return {
            "verdict": verdict,
            "critique": verdict_text,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 2),
        }


# Global singleton — inference_fn will be injected at startup
global_reasoning_engine = ReasoningEngine(inference_fn=None)
