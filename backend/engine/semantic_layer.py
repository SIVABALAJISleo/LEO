import re

class SemanticInterpreter:
    def __init__(self):
        # Pillar: Synonym Collapsing (Deterministic mapping)
        self.synonyms = {
            "purchase": "buy",
            "purchased": "bought",
            "purchasing": "buying",
            "vehicle": "car",
            "exhausted": "tired",
            "postponed": "delayed",
            "essential": "important",
            "growth": "grew",
            "hlp": "help",
            "pls": "please",
            "finsh": "finish",
            "wen": "when",
            "iz": "is",
            "dere": "there",
            "spd": "speed",
            "proc": "process",
            "thx": "thanks",
            "nxt": "next",
            "wt": "what",
            "dis": "this",
            "costs": "cost",
            "login": "sign in"
        }
        
    def normalize(self, text):
        """Simplifies vocabulary and handles noisy language while preserving math."""
        text = text.lower()
        # Remove punctuation EXCEPT math operators
        text = re.sub(r'[^a-zA-Z0-9\s\+\-\*/\(\)\.\=]', '', text)
        words = text.split()
        normalized = [self.synonyms.get(w, w) for w in words]
        return " ".join(normalized)
        
    def extract_intent(self, text):
        """
        Converts text into a structured intent representation.
        Format: (Subject, Relation, Object/Value)
        """
        norm_text = self.normalize(text)
        
        # Heuristic Intent Patterns
        intent = {
            "raw": text,
            "normalized": norm_text,
            "subject": None,
            "relation": None,
            "object": None,
            "action": None,
            "category": None
        }
        
        # Pattern 1: Taller/Shorter relations (Comparison)
        if "taller than" in norm_text:
            intent["category"] = "comparison"
            match = re.search(r'(\w+)\s+is\s+taller\s+than\s+(\w+)', norm_text)
            if match:
                intent["subject"] = match.group(1)
                intent["relation"] = "taller_than"
                intent["object"] = match.group(2)
        
        # Pattern 2: Mathematical simple intent
        if re.search(r'[\+\-\*/\(\)]', norm_text):
            intent["category"] = "math"
            intent["action"] = "calculate"

        # Pattern 3: Noisy language cleanup markers
        if any(kw in norm_text for kw in ["please", "help", "fix", "error", "login"]):
            intent["category"] = "system_interaction"
            
        return intent

    def simplify_logic(self, text):
        """Splits compound queries into atomic steps."""
        if " and " in text:
            return [s.strip() for s in text.split(" and ")]
        return [text]

interpreter = SemanticInterpreter()
