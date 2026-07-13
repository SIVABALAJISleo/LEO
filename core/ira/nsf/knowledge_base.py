"""
Symbolic Knowledge Base for Neuro-Symbolic Fusion.
Manages facts, templates, and patterns.
"""
import os
import json
import re
from typing import Optional, Dict, List, Any, Set, Tuple
from core.ira.shared.text import TextNormalizer
from core.ira.nsf.safe_calculator import SafeCalculator

class SymbolicKnowledgeBase:
    def __init__(self, kb_path: str):
        self.kb_path = kb_path
        self.facts_file = os.path.join(kb_path, "facts.json")
        self.templates_file = os.path.join(kb_path, "templates.json")
        self.patterns_file = os.path.join(kb_path, "patterns.json")
        
        os.makedirs(kb_path, exist_ok=True)
        
        self.facts: Dict[str, str] = {}
        self.templates: List[Dict[str, Any]] = []
        self.patterns: List[Dict[str, Any]] = []
        
        self.reverse_index: Dict[str, Set[str]] = {}
        self.regex_cache: List[Tuple[re.Pattern, Dict[str, Any]]] = []
        
        self._load_all()
        self._build_reverse_index()
        self._compile_regex_cache()
        self.calculator = SafeCalculator()

    def _load_all(self) -> None:
        if os.path.exists(self.facts_file):
            try:
                with open(self.facts_file, 'r', encoding='utf-8') as f:
                    self.facts = json.load(f)
            except Exception:
                self.facts = {}
                
        if os.path.exists(self.templates_file):
            try:
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    self.templates = json.load(f)
            except Exception:
                self.templates = []
                
        if os.path.exists(self.patterns_file):
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    self.patterns = json.load(f)
            except Exception:
                self.patterns = []

    def _build_reverse_index(self) -> None:
        self.reverse_index.clear()
        for key in self.facts.keys():
            words = TextNormalizer.normalize_for_hash(key).split()
            for word in words:
                if word not in self.reverse_index:
                    self.reverse_index[word] = set()
                self.reverse_index[word].add(key)

    def _compile_regex_cache(self) -> None:
        self.regex_cache.clear()
        for template in self.templates:
            pattern_str = template.get("pattern")
            if pattern_str:
                try:
                    # Ignore case for general matches
                    compiled = re.compile(pattern_str, re.IGNORECASE)
                    self.regex_cache.append((compiled, template))
                except Exception:
                    pass

    def lookup_fact(self, query: str) -> Optional[str]:
        # 1. Normalize query
        norm_query = TextNormalizer.normalize(query)
        
        # 2. Try exact match
        if query in self.facts:
            return self.facts[query]
            
        # 3. Try normalized exact match
        for key, val in self.facts.items():
            if TextNormalizer.normalize(key) == norm_query:
                return val
                
        # 4. Try key-intersection match (Jaccard similarity > 0.7)
        query_words = set(TextNormalizer.normalize_for_hash(query).split())
        if not query_words:
            return None
            
        best_match = None
        best_score = 0.0
        
        # Candidate generation via reverse index
        candidates = set()
        for word in query_words:
            if word in self.reverse_index:
                candidates.update(self.reverse_index[word])
                
        for cand in candidates:
            cand_words = set(TextNormalizer.normalize_for_hash(cand).split())
            score = self._jaccard_similarity(query_words, cand_words)
            if score > best_score:
                best_score = score
                best_match = cand
                
        if best_score > 0.7:
            return self.facts[best_match]
            
        return None

    def _jaccard_similarity(self, set_a: set, set_b: set) -> float:
        union = len(set_a.union(set_b))
        if union == 0:
            return 0.0
        return len(set_a.intersection(set_b)) / union

    def match_template(self, query: str) -> Optional[str]:
        for pattern, template in self.regex_cache:
            match = pattern.match(query)
            if not match:
                # Try search if match doesn't work at start
                match = pattern.search(query)
                
            if match:
                response = template.get("response", "")
                compute_str = template.get("compute")
                
                if compute_str:
                    try:
                        # Safely parse and substitute the compute expression
                        # The compute format is like: "lambda m: float(m.group(1)) * 9/5 + 32"
                        # We extract the expression part of the lambda
                        expr_part = compute_str
                        if "lambda" in compute_str:
                            expr_part = compute_str.split(":", 1)[1].strip()
                            
                        # Replace m.group(X) with the matched group value
                        def replacer(m_obj):
                            group_idx = int(m_obj.group(1))
                            return str(match.group(group_idx))
                            
                        # Pattern to match m.group(X) or float(m.group(X)) or int(m.group(X))
                        clean_expr = re.sub(r'(?:float|int)?\(?m\.group\((\d+)\)\)?', replacer, expr_part)
                        
                        # Evaluate using SafeCalculator
                        calc_result = self.calculator.evaluate(clean_expr)
                        
                        # Populate template response
                        # e.g. "{1}°C = {result}°F"
                        formatted = response
                        # Replace match groups in the response
                        for i in range(1, len(match.groups()) + 1):
                            formatted = formatted.replace(f"{{{i}}}", str(match.group(i)))
                        formatted = formatted.replace("{result}", f"{calc_result:.2f}".rstrip('0').rstrip('.'))
                        return formatted
                    except Exception:
                        # Fallback: if dynamic compute fails, return static template
                        pass
                        
                # Substitute matches directly for static templates
                formatted = response
                for i in range(1, len(match.groups()) + 1):
                    formatted = formatted.replace(f"{{{i}}}", str(match.group(i)))
                return formatted
                
        return None

    def add_fact(self, key: str, value: str) -> None:
        self.facts[key] = value
        self._build_reverse_index()

    def add_template(self, pattern: str, response: str, compute: str = None) -> None:
        self.templates.append({
            "pattern": pattern,
            "response": response,
            "compute": compute
        })
        self._compile_regex_cache()

    def save(self) -> None:
        with open(self.facts_file, 'w', encoding='utf-8') as f:
            json.dump(self.facts, f, indent=4, ensure_ascii=False)
        with open(self.templates_file, 'w', encoding='utf-8') as f:
            json.dump(self.templates, f, indent=4, ensure_ascii=False)
        with open(self.patterns_file, 'w', encoding='utf-8') as f:
            json.dump(self.patterns, f, indent=4, ensure_ascii=False)

    def get_stats(self) -> dict:
        return {
            "facts_count": len(self.facts),
            "templates_count": len(self.templates),
            "patterns_count": len(self.patterns)
        }
