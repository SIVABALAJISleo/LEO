"""
backend/inference/contract_engine.py
LEO Real Semantic Contract Subsumption Engine
Real Embedding Model (SentenceTransformers) + Real FAISS Vector Index
"""
import os
import sys
from leo_real_engine import RealContractEngine

_global_engine = None

def get_real_contract_engine() -> RealContractEngine:
    global _global_engine
    if _global_engine is None:
        _global_engine = RealContractEngine()
        # Seed with canonical knowledge
        _global_engine.add_to_cache(
            "How do I reset my active directory password?",
            "1. Go to reset.company.com. 2. Enter your ID. 3. Click the email link."
        )
        _global_engine.add_to_cache(
            "What is the procurement process for new laptops?",
            "Submit a ticket to IT Purchasing. Manager approval is required for Tier 2 assets."
        )
        _global_engine.add_to_cache(
            "What is the company policy for working from home?",
            "Employees may work remotely up to 3 days per week with manager consent."
        )
        _global_engine.add_to_cache(
            "What is the capital of France?",
            "The capital of France is Paris."
        )
        _global_engine.add_to_cache(
            "What is the speed of light?",
            "The speed of light in vacuum is exactly 299,792,458 meters per second."
        )
    return _global_engine
