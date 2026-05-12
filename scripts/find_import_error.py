import importlib
import sys
import os

modules_to_test = [
    "backend.models",
    "backend.database",
    "backend.auth",
    "rag.query",
    "experts.router",
    "orchestration.ingestion",
    "orchestration.cache",
    "orchestration.physics_consumer",
    "orchestration.data_consumers",
    "orchestration.scene_data",
    "orchestration.scientific_data",
    # Add newly added modules
    "orchestration.intelligence.adaptive_downgrade",
    "orchestration.intelligence.fallback_graph",
    "orchestration.intelligence.async_offload",
    "orchestration.intelligence.self_profiler",
    "engine_hv.advanced.progressive_compute",
    "engine_hv.advanced.temporal_recon",
    "engine_hv.advanced.perceptual_metric",
    "engine_hv.advanced.tile_solver",
    "engine_hv.advanced.probabilistic",
    "experts.behavior_emulation"
]

os.environ["PYTHONPATH"] = "."

for mod_name in modules_to_test:
    print(f"Testing {mod_name}...", end=" ")
    sys.stdout.flush()
    try:
        importlib.import_module(mod_name)
        print("SUCCESS")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
