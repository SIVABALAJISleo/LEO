from typing import List, Dict, Any, Optional
import copy

class Candidate:
    def __init__(self, entities: List[str] = None, relations: List[str] = None, quantities: Dict[str, Any] = None, assumptions: List[str] = None):
        self.entities = entities or []
        self.relations = relations or []
        self.quantities = quantities or {}
        self.assumptions = assumptions or []
        self.score = 0
        self.interpretation_type = "base"

    def to_dict(self):
        return {
            "entities": self.entities,
            "relations": self.relations,
            "quantities": self.quantities,
            "assumptions": self.assumptions,
            "score": self.score,
            "type": self.interpretation_type
        }

class HypothesisGenerator:
    """Generates 3-7 candidate interpretations per query."""
    
    def __init__(self, extractor):
        self.extractor = extractor

    def generate(self, text: str) -> List[Candidate]:
        candidates = []
        
        # 1. Base Extraction — use real WorldModelWorkspace
        from backend.engine.world_model import WorldModelWorkspace
        base_workspace = WorldModelWorkspace()
        self.extractor.extract(text, base_workspace)
        
        base_candidate = Candidate(
            entities=list(base_workspace.entities),
            relations=list(base_workspace.relations),
            quantities=dict(base_workspace.quantities)
        )
        base_candidate.interpretation_type = "base"
        candidates.append(base_candidate)

        # 2. Relation Direction Variance
        if "gt_height" in base_candidate.relations:
            inv = copy.deepcopy(base_candidate)
            inv.relations = ["lt_height" if r == "gt_height" else r for r in inv.relations]
            inv.interpretation_type = "inverse_relation"
            inv.assumptions.append("Reverse comparative direction")
            candidates.append(inv)

        # 3. Implicit Causality Expansion (postponed/delayed)
        if "delayed" in base_candidate.relations or "postponed" in text.lower():
            causal = copy.deepcopy(base_candidate)
            causal.relations.append("future_event")
            causal.assumptions.append("Postponed implies future scheduling")
            causal.interpretation_type = "causal_expansion"
            candidates.append(causal)

        # 4. Temporal Ordering Expansion
        if "yesterday" in text.lower() or "yestdy" in text.lower():
            temp = copy.deepcopy(base_candidate)
            temp.assumptions.append("Reference to past state")
            temp.interpretation_type = "temporal_shift"
            candidates.append(temp)

        # 5. Comparative/Efficiency Meanings
        if "faster" in text.lower() or "speed up" in text.lower():
            comp = copy.deepcopy(base_candidate)
            comp.relations.append("efficiency_intent")
            comp.assumptions.append("Faster means less time required")
            comp.interpretation_type = "comparative_meaning"
            candidates.append(comp)

        # 6. Synonym Mapping (vehicle -> car, purchase -> buy)
        if "vehicle" in text.lower():
            syn = copy.deepcopy(base_candidate)
            if "car" not in syn.entities:
                syn.entities.append("car")
            syn.relations.append("buy_intent")
            syn.interpretation_type = "synonym_mapping"
            candidates.append(syn)

        # 7. Normative/Essential expansion (essential -> is_required)
        if "essential" in text.lower() and "is_required" not in base_candidate.relations:
            norm = copy.deepcopy(base_candidate)
            norm.relations.append("is_required")
            norm.assumptions.append("Essential implies normative constraint")
            norm.interpretation_type = "normative_expand"
            candidates.append(norm)

        return candidates

class SemanticValidator:
    """Uses SymbolicSolver as a truth validator for candidates."""
    
    def __init__(self, solver):
        self.solver = solver

    def validate(self, candidates: List[Candidate], query: str):
        for c in candidates:
            # Create a real workspace for the solver
            from backend.engine.world_model import WorldModelWorkspace
            workspace = WorldModelWorkspace()
            workspace.entities = c.entities
            workspace.relations = c.relations
            workspace.quantities = c.quantities
            workspace.raw_query = query
            
            # Use solver to check consistency
            try:
                result = self.solver.solve(workspace)
                if result["type"] != "unknown" and result["value"] is not None:
                    c.score += 2 # Solvable without contradiction
                    c.score += 1 # Meaningful answer
                else:
                    c.score -= 1 # PRODUCES NO MEANING
            except Exception:
                c.score -= 2 # LOGICAL CONFLICT / ERROR
            
            # Impossible state detection (heuristic)
            if len(c.entities) < 1 and len(c.relations) > 0:
                c.score -= 3 # Impossible state

class InterpreterRanker:
    """Selects the best interpretation."""
    
    def select_best(self, candidates: List[Candidate]) -> Candidate:
        # Sort by score (desc), then by fewest assumptions (asc)
        sorted_c = sorted(candidates, key=lambda x: (-x.score, len(x.assumptions)))
        return sorted_c[0] if sorted_c else None

class SemanticExplorer:
    """The Orchestrator for Hypothesis-Based Interpretation."""
    
    # Ordered list of (noisy, clean) replacements
    _corrections = [
        ("wen ", "when "), ("r u", "are you"), ("gonna", "going to"),
        ("finsh", "finish"), ("thx", "thanks"), ("hlp", "help"),
        ("iz ", "is "), ("spd up", "speed up"), ("nxt", "next"),
        ("yestdy", "yesterday"), ("agin", "again"),
        ("dis ", "this "), ("wt ", "what "), ("pls ", "please "),
        (" u ", " you "), ("dere", "there"), (" d ", " the "),
        ("4 ", "for "),
    ]

    def __init__(self, extractor, solver):
        self.generator = HypothesisGenerator(extractor)
        self.validator = SemanticValidator(solver)
        self.ranker = InterpreterRanker()

    def _normalise(self, text: str) -> str:
        """Apply lightweight noisy-text normalisation before hypothesis generation."""
        t = text.lower()
        for noisy, clean in self._corrections:
            t = t.replace(noisy, clean)
        return t

    def interpret(self, text: str) -> Candidate:
        normalised = self._normalise(text)
        candidates = self.generator.generate(normalised)
        self.validator.validate(candidates, normalised)
        return self.ranker.select_best(candidates)

# Global Instance
from backend.engine.world_model import engine as wm_engine
semantic_explorer = SemanticExplorer(wm_engine.extractor, wm_engine.solver)
