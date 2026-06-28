"""
tests/conftest.py – LEO AI global test configuration
======================================================
This file is automatically loaded by pytest BEFORE any test module is
imported.  It guarantees that environment variables needed for offline-safe
test execution are set before any backend code touches HuggingFace, torch,
or sentence-transformers.

Do NOT add test fixtures here that are specific to a single test module.
"""

import os

# ── Offline / CI Guard ────────────────────────────────────────────────────
# These MUST be set before any backend module is imported to prevent
# SentenceTransformer / HuggingFace from making outbound network requests.
os.environ.setdefault("LEO_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_DATASETS_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")   # Suppress fork warning

# ── Test Database ─────────────────────────────────────────────────────────
# Use a separate in-memory DB for tests so production DB is never touched.
os.environ.setdefault("DATABASE_URL", "sqlite:///./hyper_test.db")
