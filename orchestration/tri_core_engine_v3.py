import json
import os
import re
import hashlib
import time

"""
TRI-CORE SEMANTIC ENGINE (V3)
1. INPUT: Clean/Translate
2. INTENT: Rules + Naive Bayes
3. ROUTE: Minimal Perfect Hash (MPHF) -> CDN Fetch
"""

class TriCoreEngineV3:
    def __init__(self, cdn_root="./cdn_tricore"):
        self.cdn_root = cdn_root
        self.config = {}
        self.nb_model = {}
        self.load_config()
        
        # Domain Rules
        self.rules = {
            "CONTROL": {"reboot", "restart", "shutdown", "stop", "start", "initialize", "reset"},
            "INFO": {"status", "health", "report", "stats", "metrics", "telemetry"},
            "SYSTEM": {"update", "synchronize", "backup", "restore", "patch", "verify", "audit"}
        }

    def load_config(self):
        config_path = os.path.join(self.cdn_root, "engine_config.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.config = json.load(f)
        
        nb_path = "msr_nb_model.json"
        if os.path.exists(nb_path):
            with open(nb_path, "r") as f:
                self.nb_model = json.load(f)

    def _clean(self, text):
        return re.sub(r'[^a-zA-Z0-9\s]', '', text.lower()).strip()

    def _msr_intent(self, text):
        tokens = set(text.split())
        
        # 1. Rule Engine
        for domain, keywords in self.rules.items():
            if tokens.intersection(keywords):
                return domain
        
        # 2. Naive Bayes Fallback
        if not self.nb_model: return "GENERAL"
        
        best_domain = "GENERAL"
        max_prob = -1.0
        
        for dom, prior in self.nb_model["priors"].items():
            prob = prior
            for t in tokens:
                t_probs = self.nb_model["token_probs"].get(t)
                if t_probs:
                    prob *= t_probs.get(dom, 0.0001) # Smoothing
            
            if prob > max_prob:
                max_prob = prob
                best_domain = dom
        
        return best_domain

    def _mphf_route(self, query):
        if not self.config: return None
        
        g = self.config["mphf"]["g"]
        n = self.config["mphf"]["n"]
        
        # h1 and h2 must match compiler
        h1_idx = int(hashlib.md5(query.encode()).hexdigest(), 16) % len(g)
        h2_val = int(hashlib.sha1(query.encode()).hexdigest(), 16) % n
        
        d = g[h1_idx]
        idx = (h2_val + d) % n
        return idx

    def execute(self, text):
        start_time = time.perf_counter()
        
        # 1. INPUT LAYER
        clean_text = self._clean(text)
        
        # 2. INTENT LAYER (MSR)
        domain = self._msr_intent(clean_text)
        
        # 3. ROUTING LAYER (MPHF)
        # We attempt a perfect hash lookup
        resolved_id = self._mphf_route(clean_text)
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        # 4. OUTPUT LAYER (CDN Fetch O(1))
        # Validation is mandatory to handle OOB (Out-of-Bounds) queries 
        # since MPHF will always return SOME index for ANY string.
        res_path = os.path.join(self.cdn_root, f"{resolved_id}.json")
        
        if os.path.exists(res_path):
            with open(res_path, "r") as f:
                blob = json.load(f)
            
            # Strict Correctness Guard
            signature = set(blob["signature"])
            input_tokens = set(clean_text.split())
            intersection = input_tokens.intersection(signature)
            score = len(intersection) / max(len(signature), len(input_tokens), 1)
            
            if score >= 0.5:
                # SUCCESS: Return Deterministic Result
                return {
                    "id": resolved_id,
                    "domain": domain,
                    "response": blob["response"],
                    "latency": f"{latency_ms:.3f}ms",
                    "path": "TRI_CORE_DETERMINISTIC"
                }

        # 5. FALLBACK (OOB / Mismatch)
        return {
            "domain": domain,
            "response": "ERROR: Query out of operational bounds. Routing to RAG...",
            "latency": f"{latency_ms:.3f}ms",
            "path": "FALLBACK_RAG"
        }

if __name__ == "__main__":
    engine = TriCoreEngineV3()
    
    test_queries = [
        "reboot alpha node immediately", # Known
        "Status of memory results",       # Known
        "restore registry",              # Known
        "Tell me a story about space",   # Unknown (OOB)
        "reboot the beta node"           # Known phrasing variation
    ]
    
    for q in test_queries:
        res = engine.execute(q)
        print(f"\n[QUERY] '{q}'")
        print(f"  Domain: {res['domain']}")
        print(f"  Response: {res['response']}")
        print(f"  Path: {res['path']} | Latency: {res['latency']}")
