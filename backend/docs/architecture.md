# Architecture: CPU/iGPU-First Intelligence

## Overview
Project HYPER is built on the principle of **Algorithmic Substitution**. Instead of relying on GPU-heavy brute-force computation, we use specialized software layers to simulate, predict, and approximate high-level outcomes.

## Core Modules
1. **Semantic Router & Expert Hub**: Dispatches tasks to deterministic "Experts" instead of broad LLM inferences.
2. **Deterministic Reasoning Engine**: Handles logical and mathematical queries using symbolic templates.
3. **Zero-Binary Retrieval (Numpy-Index)**: Provides vector search without heavy binary dependencies or GPU overhead.
4. **Compute Reduction Layer**: Uses global memoization and predictive background scheduling to avoid re-computation.

## Algorithmic Strategy
- **Logic over Physics**: Physical simulations are replaced by state-machine transitions and perceptual interpolation.
- **Prediction over Rendering**: UI states are predicted and optimistically updated, reducing wait times for server truth.
- **Caching over Inference**: Semantic similarity checks ensure common queries are served in <5ms.
