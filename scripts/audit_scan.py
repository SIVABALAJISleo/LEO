import os
import json
import sys

dirs_to_check = [
    'core', 'backend', 'hyper', 'leo', 'optimization', 'algorithm_discovery',
    'universal_compute_router', 'benchmark_workers', 'benchmarks', 'execution',
    'predictors', 'cache', 'contracts', 'src', 'cli', 'dashboard', 'information_sufficiency',
    'hyper_omega', 'hyper_x', 'hyper_runtime', 'hyper_cco', 'hyper_universal',
    'models', 'pipeline', 'rag', 'spectral', 'physics', 'render'
]

summary = {}
for d in dirs_to_check:
    if os.path.exists(d):
        files = []
        for root, dirs, filenames in os.walk(d):
            # Skip node_modules, .git, venv
            dirs[:] = [sub for sub in dirs if sub not in ('node_modules', '.git', '__pycache__', '.venv', 'venv')]
            for f in filenames:
                if f.endswith(('.py', '.json', '.md', '.ts', '.tsx')):
                    rel = os.path.relpath(os.path.join(root, f), d)
                    files.append(rel)
        summary[d] = {
            'count': len(files),
            'sample': files[:15]
        }
    else:
        summary[d] = 'NOT_FOUND'

print(json.dumps(summary, indent=2))
