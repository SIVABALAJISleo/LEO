"""
Adaptive Depth Router (ADR).
Classifies queries into complexity levels and dynamically determines the number
of transformer layers required, bypassing heavy compute for simpler requests.
"""
import os
import re
import json
from enum import IntEnum
from typing import Tuple, Dict, Any, List
import numpy as np

from core.ira.shared.config import ADRConfig
from core.ira.shared.logging import IRALogger
from core.ira.shared.metrics import get_metric_collector

class QueryComplexity(IntEnum):
    TRIVIAL = 1
    SIMPLE = 2
    MODERATE = 3
    COMPLEX = 4
    EXTREME = 5

class AdaptiveDepthRouter:
    def __init__(self, config: ADRConfig = None):
        self.config = config or ADRConfig()
        self.adjustments_file = "data/ira/patterns/adr_adjustments.json"
        
        # Regex compile for fast matching
        self.rx_trivial_math = re.compile(r'\b\d+(?:\.\d+)?\s*[+\-*/^%]\s*\d+(?:\.\d+)?\b')
        self.rx_fact_prefix = re.compile(
            r'^(?:what is|who is|when was|where is|define|meaning of|full form of)\b', 
            re.IGNORECASE
        )
        self.rx_yes_no_prefix = re.compile(r'^(?:is|are|can|will|does|do|did)\b', re.IGNORECASE)
        self.rx_list_prefix = re.compile(r'^(?:list|name|enumerate|give me|tell me)\b', re.IGNORECASE)
        
        self.rx_simple_how = re.compile(r'^(?:how to|how do i|how can i|steps to)\b', re.IGNORECASE)
        self.rx_simple_what = re.compile(r'^(?:what does|what do|what are the|what is the meaning)\b', re.IGNORECASE)
        self.rx_simple_compare = re.compile(r'\b(?:difference between|vs|compared to|versus)\b', re.IGNORECASE)
        self.rx_simple_step = re.compile(r'^(?:explain|describe|summarize|define|what is a|what is an)\b', re.IGNORECASE)
        self.rx_simple_translate = re.compile(r'\b(?:translate|how do you say)\b', re.IGNORECASE)
        
        # Complexity signals
        self.complexity_signals = [
            "step by step", "analyze", "reason", "prove", "derive",
            "algorithm", "implement", "optimize", "debug", "refactor",
            "compare and contrast", "evaluate", "critique", "synthesize",
            "architect", "design", "strategy", "trade-off", "tradeoff",
            "comprehensive", "detailed", "in-depth", "deep dive",
            "write code", "create a", "build a", "develop"
        ]
        
        self.logger = IRALogger.get_logger("adr")
        self.metrics = get_metric_collector().system.get_or_create_pillar("adr")
        
        self.adjustments: Dict[str, int] = {}
        self._load_adjustments()

    def _load_adjustments(self) -> None:
        if os.path.exists(self.adjustments_file):
            try:
                with open(self.adjustments_file, 'r', encoding='utf-8') as f:
                    self.adjustments = json.load(f)
            except Exception:
                self.adjustments = {}

    def _save_adjustments(self) -> None:
        os.makedirs(os.path.dirname(self.adjustments_file), exist_ok=True)
        try:
            with open(self.adjustments_file, 'w', encoding='utf-8') as f:
                json.dump(self.adjustments, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def classify(self, query: str) -> Tuple[QueryComplexity, int, str]:
        # RULE 1: Empty or whitespace-only
        cleaned = query.strip()
        if not cleaned:
            return QueryComplexity.TRIVIAL, 0, "empty_query"
            
        words = cleaned.split()
        word_count = len(words)
        
        # RULE 2: Length <= 3 words
        if word_count <= 3:
            complexity = QueryComplexity.TRIVIAL
            layers = self.config.trivial_layer_count
            reason = "short_query"
            return self._apply_tuning(cleaned, complexity, layers, reason)
            
        # RULE 3: Match trivial patterns
        if (self.rx_trivial_math.search(cleaned) or
            self.rx_fact_prefix.match(cleaned) or
            self.rx_yes_no_prefix.match(cleaned) or
            self.rx_list_prefix.match(cleaned) or
            ' ' not in cleaned):
            
            complexity = QueryComplexity.TRIVIAL
            layers = self.config.trivial_layer_count
            reason = "pattern:trivial"
            return self._apply_tuning(cleaned, complexity, layers, reason)
            
        # RULE 4: Match simple patterns
        if (self.rx_simple_how.match(cleaned) or
            self.rx_simple_what.match(cleaned) or
            self.rx_simple_compare.search(cleaned) or
            self.rx_simple_step.match(cleaned) or
            self.rx_simple_translate.search(cleaned)):
            
            complexity = QueryComplexity.SIMPLE
            layers = self.config.simple_layer_count
            reason = "pattern:simple"
            return self._apply_tuning(cleaned, complexity, layers, reason)
            
        # RULE 5: Length-based heuristic
        if 4 <= word_count <= 10:
            complexity = QueryComplexity.SIMPLE
            layers = self.config.simple_layer_count
            reason = "length_short"
            return self._apply_tuning(cleaned, complexity, layers, reason)
        elif 11 <= word_count <= 25:
            complexity = QueryComplexity.MODERATE
            layers = self.config.moderate_layer_count
            reason = "length_medium"
            return self._apply_tuning(cleaned, complexity, layers, reason)
            
        # RULE 6: Complexity signal counting
        signal_count = sum(1 for sig in self.complexity_signals if sig in cleaned.lower())
        
        if signal_count >= 3:
            complexity = QueryComplexity.EXTREME
            layers = self.config.complex_layer_count
            reason = "multi_signal"
        elif signal_count == 2:
            complexity = QueryComplexity.COMPLEX
            layers = self.config.complex_layer_count
            reason = "dual_signal"
        elif signal_count == 1:
            complexity = QueryComplexity.COMPLEX
            layers = self.config.complex_layer_count
            reason = "single_signal"
        else:
            complexity = QueryComplexity.MODERATE
            layers = self.config.moderate_layer_count
            reason = "no_signal_long"
            
        # RULE 7: Question mark count
        q_count = cleaned.count('?')
        if q_count >= 3:
            complexity = QueryComplexity.EXTREME
            layers = self.config.complex_layer_count
            reason = "extreme_questions"
        elif q_count == 2:
            complexity = QueryComplexity.COMPLEX
            layers = self.config.complex_layer_count
            reason = "complex_questions"
            
        # RULE 8: Code detection
        if ("```" in cleaned or 
            "def " in cleaned or 
            "class " in cleaned or 
            "function " in cleaned or 
            "import " in cleaned or 
            "public class" in cleaned):
            complexity = QueryComplexity.COMPLEX
            layers = self.config.complex_layer_count
            reason = "code_detected"
            
        # RULE 9: Multi-part query detection (bump up complexity)
        if any(x in cleaned.lower() for x in (" and also ", " additionally ", " furthermore ", " moreover ", " plus ")):
            if complexity < QueryComplexity.EXTREME:
                complexity = QueryComplexity(complexity + 1)
                # Map new complexity to layers
                layer_map = {
                    QueryComplexity.SIMPLE: self.config.simple_layer_count,
                    QueryComplexity.MODERATE: self.config.moderate_layer_count,
                    QueryComplexity.COMPLEX: self.config.complex_layer_count,
                    QueryComplexity.EXTREME: self.config.complex_layer_count
                }
                layers = layer_map[complexity]
                reason += "_multipart_bump"
                
        return self._apply_tuning(cleaned, complexity, layers, reason)

    def _apply_tuning(self, query: str, complexity: QueryComplexity, 
                      layers: int, reason: str) -> Tuple[QueryComplexity, int, str]:
        # If we have tracked a feedback override for this query pattern
        query_key = query.lower()
        if query_key in self.adjustments:
            adjusted_complexity = QueryComplexity(self.adjustments[query_key])
            if adjusted_complexity != complexity:
                layer_map = {
                    QueryComplexity.TRIVIAL: self.config.trivial_layer_count,
                    QueryComplexity.SIMPLE: self.config.simple_layer_count,
                    QueryComplexity.MODERATE: self.config.moderate_layer_count,
                    QueryComplexity.COMPLEX: self.config.complex_layer_count,
                    QueryComplexity.EXTREME: self.config.complex_layer_count
                }
                self.logger.info(f"Applying adaptive ADR adjustment for query: {query[:30]} -> {adjusted_complexity.name}")
                return adjusted_complexity, layer_map[adjusted_complexity], reason + "_adaptive"
        return complexity, layers, reason

    def record_feedback(self, query: str, actual_needed_complexity: QueryComplexity) -> None:
        """If user rephrases or downvotes, record the true needed complexity level."""
        self.adjustments[query.lower()] = int(actual_needed_complexity)
        self._save_adjustments()

    def get_speedup_factor(self, query: str) -> float:
        _, layers_used, _ = self.classify(query)
        if layers_used == 0:
            return float(self.config.total_layers)
        return self.config.total_layers / layers_used

    def get_layer_mask(self, query: str) -> np.ndarray:
        complexity, _, _ = self.classify(query)
        mask = np.zeros(self.config.total_layers, dtype=bool)
        
        if complexity == QueryComplexity.TRIVIAL:
            mask[:self.config.trivial_layer_count] = True
        elif complexity == QueryComplexity.SIMPLE:
            mask[:self.config.simple_layer_count] = True
        elif complexity == QueryComplexity.MODERATE:
            mask[:self.config.moderate_layer_count] = True
        else: # COMPLEX or EXTREME
            mask[:] = True
            
        return mask

    def get_stats(self) -> dict:
        return {
            "adjustments_count": len(self.adjustments),
            "config": self.config.__dict__
        }
