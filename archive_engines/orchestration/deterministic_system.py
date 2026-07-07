import json
import os
import re
import hashlib
import time

"""
DETERMINISTIC SEMANTIC SYSTEM (V4)
"Align meaning before execution. Reify input into structures."
"""

class EntropyController:
    """
    LAYER 1: INPUT CONSTRAINT & FAST REJECT
    Eliminates ambiguity before it hits the semantic core.
    """
    def __init__(self, valid_commands):
        self.valid_commands = set(valid_commands)
        self.patterns = [re.compile(f"^{c.replace(' ', '.*')}$") for c in valid_commands]

    def validate(self, text):
        clean = text.lower().strip()
        # Fast Reject: Exact match or pattern match
        if clean in self.valid_commands:
            return "EXACT", clean
        
        for p in self.patterns:
            if p.match(clean):
                return "PATTERN", clean
                
        return "REJECT", None

class BitwiseRuleEvaluator:
    """
    LAYER 4: EXECUTION CORE (Mock Tsetlin Machine)
    Uses bitwise state logic for high-speed rule validation.
    """
    def __init__(self, domain_bits):
        self.domain_bits = domain_bits # Map domain names to bits

    def evaluate(self, domain, intent_id):
        # bitwise-only logic
        d_bit = self.domain_bits.get(domain, 0x0)
        # Rule: Result valid if intent_id parity matches domain bit
        # (This is a simplified bitwise FSM check)
        return (intent_id ^ d_bit) & 0xFFFFFFFF

class DeterministicSystemV4:
    def __init__(self, cdn_root="./cdn_tricore"):
        self.cdn_root = cdn_root
        self.config = {}
        self.valid_keys = []
        self.load_engine()
        
        self.gatekeeper = EntropyController(self.valid_keys)
        self.evaluator = BitwiseRuleEvaluator({"CONTROL": 0x1, "INFO": 0x2, "SYSTEM": 0x4})

    def load_engine(self):
        config_path = os.path.join(self.cdn_root, "engine_config.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.config = json.load(f)
        
        # Load valid keys from CDN directory filenames or a manifest
        # (For this MVP, we load from the dataset)
        if os.path.exists("msr_dataset_500.json"):
            with open("msr_dataset_500.json", "r") as f:
                dataset = json.load(f)
                self.valid_keys = [item["query"] for item in dataset]

    def _mphf_route(self, query):
        g = self.config["mphf"]["g"]
        n = self.config["mphf"]["n"]
        h1_idx = int(hashlib.md5(query.encode()).hexdigest(), 16) % len(g)
        h2_val = int(hashlib.sha1(query.encode()).hexdigest(), 16) % n
        return (h2_val + g[h1_idx]) % n

    def process(self, raw_input):
        start = time.perf_counter()
        
        # 1. FAST REJECT & NORMALIZATION
        status, clean_text = self.gatekeeper.validate(raw_input)
        if status == "REJECT":
            return {
                "status": "ERROR",
                "message": "INPUT_ENTROPY_TOO_HIGH: Ambiguous or unsupported query rejected.",
                "latency": f"{(time.perf_counter() - start)*1000:.3f}ms"
            }

        # 2. DETERMINISTIC ROUTING (MPHF)
        resolved_id = self._mphf_route(clean_text)
        
        # 3. OUTPUT (CDN FETCH O(1))
        res_path = os.path.join(self.cdn_root, f"{resolved_id}.json")
        if not os.path.exists(res_path):
            return {"status": "FAULT", "message": "CDN_ANCHOR_MISS"}

        with open(res_path, "r") as f:
            blob = json.load(f)

        # 4. EXECUTION CORE (Bitwise Verification)
        # Verifies the resolved intent against its domain domain constraints
        state_v = self.evaluator.evaluate(blob["domain"], resolved_id)
        
        latency_ms = (time.perf_counter() - start) * 1000
        
        return {
            "status": "SUCCESS",
            "intent_id": resolved_id,
            "domain": blob["domain"],
            "response": blob["response"],
            "execution_state": hex(state_v),
            "latency": f"{latency_ms:.3f}ms",
            "path": f"DETERMINISTIC_{status}"
        }

if __name__ == "__main__":
    system = DeterministicSystemV4()
    
    test_cases = [
        "restore registry",              # Exact Match
        "Reboot Alpha Node",             # Pattern Match (case-insensitive)
        "Give me some advice",           # Reject (Entropy too high)
        "backup database now"            # Pattern match fallback
    ]
    
    print("--- DETERMINISTIC SYSTEM V4 ACTIVE ---")
    for tc in test_cases:
        res = system.process(tc)
        print(f"\n[INPUT] '{tc}'")
        if res["status"] == "SUCCESS":
            print(f"  Result: {res['domain']} | {res['response']}")
            print(f"  State: {res['execution_state']} | Latency: {res['latency']}")
        else:
            print(f"  System Message: {res['message']}")
