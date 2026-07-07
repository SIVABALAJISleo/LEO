import os
import re

dirs = [
    "adaptive_compute_router", "adaptive_self_correcting_system", "adversarial_verification_system",
    "approximation", "boundary_perfect_ai", "cdn_gatekeeper", "cdn_mock", "cdn_simhash", "cdn_tricore",
    "chaos", "closed_loop_synthesis", "composable_intel_ai", "controlled_ai_pipeline", "deterministic_query_system",
    "engine_hv", "fallback_modes", "gatekeeper_architecture", "high_accuracy_engine", "high_perf_intel_ai",
    "hybrid_ai_system", "hybrid_intel_ai", "hybrid_os_symbolic", "hyper_core_ai", "hyper_optimized_ai",
    "llm_os_core", "llm_os_intel", "local_first_intent_system", "native_engine", "optimistic", "outcome_driven_ai",
    "perfect_verification_system", "probabilistic", "safe_outcome_ai", "self_skeptical_engine", "steered_intel_ai",
    "uncertainty_resolution_v2", "upscale", "verified_outcome_ai", "verifier", "voxel", "vulkan_intel_ai",
    "zero_failure_ai", "orchestration", "router"
]

def fix_imports():
    for root, _, files in os.walk("."):
        if "venv" in root or "node_modules" in root or ".git" in root:
            continue
            
        for file in files:
            if not file.endswith(".py"):
                continue
                
            filepath = os.path.join(root, file)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            modified = False
            for d in dirs:
                # from archive_engines.orchestration import ... -> from archive_engines.orchestration import ...
                pattern_from = rf"from {d}(\.| )"
                if re.search(pattern_from, content):
                    content = re.sub(pattern_from, rf"from archive_engines.{d}\1", content)
                    modified = True
                    
                # import archive_engines.orchestration -> import archive_engines.orchestration
                pattern_import = rf"import {d}(\.| |\n)"
                if re.search(pattern_import, content):
                    content = re.sub(pattern_import, rf"import archive_engines.{d}\1", content)
                    modified = True
                    
            if modified:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Fixed imports in {filepath}")

if __name__ == "__main__":
    fix_imports()
