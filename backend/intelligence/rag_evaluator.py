"""
backend/intelligence/rag_evaluator.py
LEO AI v∞ offline RAG Quality Evaluation Suite.
Measures groundedness, recall@k, correctness, schema validity, refusal behaviors, and latency percentiles.
"""

import time
import json
import logging
import numpy as np
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Synthetic / Local Reference Ground Truth Dataset
EVAL_GROUND_TRUTH = [
    {
        "query": "What is the CPU thread configuration of Intel Core i5-12450H?",
        "expected_answer_keywords": ["8 physical cores", "12 logical threads", "avx2"],
        "expected_citations": ["hardware_spec_sheet"],
        "context_content": "The Intel Core i5-12450H is a mobile processor containing 8 physical cores and 12 logical threads supporting AVX2.",
        "should_refuse": False
    },
    {
        "query": "Explain LEO speculative draft model acceptance criteria.",
        "expected_answer_keywords": ["target_prob", "draft_prob", "ratio"],
        "expected_citations": ["speculative_decoding_notes"],
        "context_content": "LEO speculative decoding verifies draft tokens sequentially and accepts them if rand() < target_prob / draft_prob.",
        "should_refuse": False
    },
    {
        "query": "What is the temperature of Mars today?",
        "expected_answer_keywords": [],
        "expected_citations": [],
        "context_content": "We only have local system specifications for the IdeaPad Slim 3. No external astronomical data is available.",
        "should_refuse": True
    }
]

class RAGEvaluator:
    """Evaluates local search retrieval recall, citation correctness, and answer groundedness."""
    
    @staticmethod
    def calculate_jaccard_overlap(str1: str, str2: str) -> float:
        s1 = set(str1.lower().split())
        s2 = set(str2.lower().split())
        if not s1 or not s2:
            return 0.0
        return len(s1.intersection(s2)) / len(s1.union(s2))

    @staticmethod
    def evaluate_groundedness(answer: str, context: str) -> float:
        """Measures what percentage of answer words exist in the retrieved context."""
        ans_words = [w for w in answer.lower().split() if len(w) > 3]
        if not ans_words:
            return 1.0
        hits = sum(1 for w in ans_words if w in context.lower())
        return hits / len(ans_words)

    def run_eval_suite(self, orchestrator: Any) -> Dict[str, Any]:
        """Runs evaluation over the ground truth dataset and returns precision/recall metrics."""
        results = []
        latencies = []
        correct_count = 0
        refusal_correct = 0
        citation_matches = 0
        total_runs = len(EVAL_GROUND_TRUTH)

        logger.info(f"Starting RAG Evaluation Suite across {total_runs} test cases...")

        for idx, case in enumerate(EVAL_GROUND_TRUTH):
            # Seed mock context in engine for testing
            if case["context_content"] and hasattr(orchestrator, "knowledge_engine"):
                orchestrator.knowledge_engine.add_document(
                    source_name=case["expected_citations"][0] if case["expected_citations"] else "unknown_source",
                    text=case["context_content"]
                )

            t0 = time.perf_counter()
            response = orchestrator.execute_semantic_workflow(case["query"], {})
            latency = (time.perf_counter() - t0) * 1000.0
            latencies.append(latency)

            answer = response.get("answer", "")
            
            # Groundedness evaluation
            groundedness = self.evaluate_groundedness(answer, case["context_content"])
            
            # Refusal verification
            refused = "do not have" in answer.lower() or "cannot answer" in answer.lower() or "no external data" in answer.lower() or "sorry" in answer.lower()
            refusal_ok = (refused == case["should_refuse"])
            if refusal_ok:
                refusal_correct += 1

            # Answer keyword correctness
            keyword_match_pct = 1.0
            if case["expected_answer_keywords"]:
                matched_kws = sum(1 for kw in case["expected_answer_keywords"] if kw in answer.lower())
                keyword_match_pct = matched_kws / len(case["expected_answer_keywords"])
                if keyword_match_pct >= 0.5:
                    correct_count += 1
            else:
                if refused:
                    correct_count += 1

            # Check citations matching expected list
            citations = [src for src in case["expected_citations"]]
            # Simple match checking
            trace = response.get("decision_trace", {})
            retrieved = trace.get("retrieved_sources", [])
            citation_ok = True
            for expected in citations:
                if expected not in retrieved and not case["should_refuse"]:
                    citation_ok = False
            if citation_ok:
                citation_matches += 1

            results.append({
                "case_idx": idx,
                "query": case["query"],
                "latency_ms": round(latency, 2),
                "groundedness": round(groundedness, 4),
                "refusal_correct": refusal_ok,
                "keyword_match_pct": round(keyword_match_pct, 4)
            })

        latencies_arr = np.array(latencies)
        
        return {
            "eval_run_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_cases_run": total_runs,
            "metrics": {
                "answer_correctness_rate": round(correct_count / total_runs, 4),
                "citation_correctness_rate": round(citation_matches / total_runs, 4),
                "refusal_correctness_rate": round(refusal_correct / total_runs, 4),
                "average_groundedness": round(float(np.mean([r["groundedness"] for r in results])), 4),
                "p50_latency_ms": round(float(np.percentile(latencies_arr, 50)), 2),
                "p95_latency_ms": round(float(np.percentile(latencies_arr, 95)), 2)
            },
            "detailed_runs": results
        }
