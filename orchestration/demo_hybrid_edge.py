import os
import shutil
import logging
from .edge_compiler import EdgeCompiler
from .edge_client import HybridEdgeClient

# Setup basic logging
logging.basicConfig(level=logging.INFO)

def run_demo():
    # 1. Define Domain Knowledge (Source of Truth)
    knowledge = [
        {
            "intent": "check status core system",
            "response": {"output": "System Nominal.", "uptime": "99.99%"},
            "wasm_logic": "status_check_v1"
        },
        {
            "intent": "reboot primary node alpha",
            "response": {"output": "Reboot sequence initiated.", "prio": "high"},
            "wasm_logic": "safety_auth_v2"
        },
        {
            "intent": "get engine metrics",
            "response": {"output": "CPU: 42%, Mem: 1.2GB", "latency": "0.4ms"}
        }
    ]

    # 2. Define Vocabulary and Synonyms
    vocab = {
        "check": 1, "status": 2, "core": 3, "system": 4,
        "reboot": 5, "restart": 6, "primary": 7, "node": 8, "alpha": 9,
        "get": 10, "engine": 11, "metrics": 12, "stats": 13, "telemetry": 14
    }
    
    # Synonyms (Collapse to canonical)
    synonyms = {
        "restart": "reboot",
        "stats": "metrics",
        "telemetry": "metrics"
    }

    # 3. Compile for CDN
    cdn_root = "c:/Users/sivab/OneDrive/Documents/HYPER/remix-of-remix-of-remix-of-nvidia-inspired-design-main/cdn_mock"
    if os.path.exists(cdn_root):
        shutil.rmtree(cdn_root)
    os.makedirs(cdn_root, exist_ok=True)
    
    compiler = EdgeCompiler(cdn_root)
    compiler.compile(knowledge, vocab, synonyms)

    # 4. Initialize Edge Client
    client = HybridEdgeClient(os.path.join(cdn_root, "manifest.json"))

    # 5. Test Scenarios
    print("\n--- HYBRID EDGE SEMANTIC SYSTEM DEMO ---")
    
    # Scenario A: Exact Match
    print("\n[A] Exact Match Query:")
    res_a = client.resolve("check status core system")
    print(f"Result: {res_a}")

    # Scenario B: Synonym Collapse (restart -> reboot)
    print("\n[B] Synonym Collapse Query (Restart instead of Reboot):")
    res_b = client.resolve("restart primary node alpha")
    print(f"Result: {res_b}")

    # Scenario C: Mip-Map Backoff (Unknown token + partial match)
    print("\n[C] Mip-Map Backoff Query (Extra noise tokens):")
    res_c = client.resolve("please check core system now")
    print(f"Result: {res_c}")

    # Scenario D: Fallback (Total mismatch)
    print("\n[D] Fallback Query (Unknown intent):")
    res_d = client.resolve("what is the weather in orbit")
    print(f"Result: {res_d}")

if __name__ == "__main__":
    run_demo()
