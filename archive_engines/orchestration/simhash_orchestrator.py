import json
import os
import re

"""
SIMHASH RUNTIME ORCHESTRATOR
Approximate routing + Strict validation.
"""

class SimHashOrchestrator:
    def __init__(self, cdn_dir="./cdn_simhash"):
        self.cdn_dir = cdn_dir
        self.noise = {"the", "a", "an", "is", "are", "do", "how", "what", "of", "in", "on", "for", "check", "i"}
        # Current operational context
        self.context_state = None

    def set_context(self, context_str):
        self.context_state = context_str
        print(f"[CONTEXT] Operational state set to: {context_str or 'DEFAULT'}")

    def _get_input_tokens(self, text):
        return set(re.findall(r'\w+', text.lower())) - self.noise

    def validate(self, input_text, blob):
        # ... validation logic (remains same)
        """
        LIGHTWEIGHT VALIDATION LAYER (MANDATORY)
        Ensures the fetched SimHash result actually relates to the input.
        """
        input_tokens = self._get_input_tokens(input_text)
        signature_tokens = set(blob["signature"])
        
        if not signature_tokens:
            return 0.0
            
        intersection = input_tokens.intersection(signature_tokens)
        score = len(intersection) / len(signature_tokens)
        
        # Threshold: At least 50% of the keywords in the stored answer 
        # must be present in the user query.
        return score

    def route(self, query_text):
        print(f"\n[QUERY] '{query_text}'")
        
        # 1. Simulate Client Hashing
        try:
            import archive_engines.orchestration.simhash_compiler as sc
        except ImportError:
            try:
                import simhash_compiler as sc
            except ImportError:
                # Fallback for IDE linter
                class Dummy: 
                    def compute_simhash(self, *args): return 0
                sc = Dummy()
            
        compiler = sc.SimHashCompiler()
        sh = compiler.compute_simhash(query_text, self.context_state)
        
        # 2. CDN Fetch (Prefix Bucketed Access)
        prefix = (sh >> 60) & 0xF
        folder = os.path.join(self.cdn_dir, f"{prefix:x}")
        
        candidates = []

        if os.path.exists(folder):
            # 3. GET TOP CANDIDATES (By Hamming Distance)
            for filename in os.listdir(folder):
                if not filename.endswith(".json"): continue
                try:
                    file_sh = int(filename.split(".")[0], 16)
                except ValueError: continue
                
                dist = self.hamming_distance(sh, file_sh)
                if dist <= 24: # Broader search for MSR
                    with open(os.path.join(folder, filename), "r") as f:
                        blob = json.load(f)
                    
                    score = self.validate(query_text, blob)
                    if score >= 0.3: # Candidate entry threshold
                        candidates.append({"blob": blob, "dist": dist, "score": score})
        
        # Sort by distance, then score
        candidates.sort(key=lambda x: (x["dist"], -x["score"]))
        top_candidates = candidates[:3]

        if not top_candidates:
            print(f"[MISS] No precomputed anchor in bucket {prefix:x}")
            return self._fallback(query_text, sh)

        # 4. MICRO SEMANTIC RESOLVER (MSR)
        if len(top_candidates) == 1:
            best = top_candidates[0]
            print(f"[MSR] Absolute match found: {best['blob']['id']}")
        else:
            print(f"[MSR] Resolving tie between {len(top_candidates)} candidates...")
            best = self._msr_resolve_tie(query_text, top_candidates)
            print(f"[MSR] Resolved to {best['blob']['id']} via keyword weighting.")

        # 5. FINAL VALIDATION
        if best["score"] >= 0.5:
            print(f"[HIT] Returning response for {best['blob']['id']}")
            return best["blob"]["response"]
        else:
            print(f"[REJECT] Result {best['blob']['id']} failed safety threshold (Score: {best['score']:.2f})")
            return self._fallback(query_text, sh)

    def _msr_resolve_tie(self, query, top_3):
        """
        REFINED MICRO SEMANTIC RESOLVER (MSR)
        1. Keyword Rule Engine (Domain Detection)
        2. Tiny Naive Bayes Classifier (Fallback)
        """
        query_tokens = self._get_input_tokens(query)
        
        # 1. KEYWORD RULE ENGINE (DOMAIN DETECTION)
        domains = {
            "CONTROL": {"reboot", "restart", "shutdown", "stop", "start"},
            "INFO": {"status", "health", "report", "stats", "metrics"}
        }
        
        query_domain = "GENERAL"
        for dom, keywords in domains.items():
            if query_tokens.intersection(keywords):
                query_domain = dom
                break
        
        # Filter by domain
        domain_matches = [c for c in top_3 if c["blob"].get("domain") == query_domain]
        if len(domain_matches) == 1:
            print(f"  -> Domain Match: {query_domain}")
            return domain_matches[0]
        
        # 2. TINY NAIVE BAYES (Fallback)
        # We simulate this via a "prioritized overlap" score
        print(f"  -> Falling back to Naive Bayes weighting...")
        best_cand = top_3[0]
        max_nb_score = -1.0
        
        for cand in (domain_matches if domain_matches else top_3):
            sig = set(cand["blob"]["signature"])
            intersection = query_tokens.intersection(sig)
            
            # Simple NB-like score: Prior (Distance) * Likelihood (Overlap)
            # Higher overlap score + lower Hamming distance = best result
            likelihood = sum(len(t) for t in intersection)
            prior = (65 - cand["dist"]) / 64.0
            nb_score = prior * likelihood
            
            if nb_score > max_nb_score:
                max_nb_score = nb_score
                best_cand = cand
                
        return best_cand

    def _fallback(self, query_text, sh):
        print("[FALLBACK] Unknown intent. Routing to Offline Resolver...")
        self._log_for_offline_resolution(query_text, sh)
        return "NO_MATCH"

    def hamming_distance(self, h1, h2):
        x = h1 ^ h2
        return bin(x).count('1')

    def _log_for_offline_resolution(self, text, sh):
        log_path = os.path.join(self.cdn_dir, "fallback_logs.txt")
        with open(log_path, "a") as f:
            f.write(f"HASH: 0x{sh:016x} | QUERY: {text}\n")

if __name__ == "__main__":
    orchestrator = SimHashOrchestrator()
    
    # 1. Base Query
    print(orchestrator.route("reboot alpha node"))
    
    # 2. Contextual Query: No Context
    # "reboot it" (Unknown context)
    print(orchestrator.route("reboot it"))
    
    # 3. Contextual Query: Alpha Context
    orchestrator.set_context("alpha_node")
    print(orchestrator.route("reboot it"))
    
    # 4. Contextual Query: Beta Context
    orchestrator.set_context("beta_node")
    print(orchestrator.route("reboot it"))
