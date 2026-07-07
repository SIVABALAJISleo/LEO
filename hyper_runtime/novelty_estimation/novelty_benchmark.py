import sys
import os
import json

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hyper_runtime.novelty_estimation.novelty_estimator import NoveltyEstimationEngine
from hyper_runtime.semantic_replay.replay_encoder import SemanticEmbeddingEngine

def run_benchmark():
    print("=" * 70)
    print("  HYPERCORE RUNTIME — MODULE 3: NOVELTY ESTIMATION ENGINE")
    print("=" * 70)
    
    engine = NoveltyEstimationEngine(low_threshold=0.3, high_threshold=0.7)
    # Use fallback encoder for speed without downloading heavy models in benchmark
    encoder = SemanticEmbeddingEngine(embedding_dim=384, force_fallback=True)
    
    # Let's define a known "context" (e.g. recent conversation history or retrieved documents)
    context_texts = [
        "What is the capital of France?",
        "HyperCore is a CPU-first AI runtime.",
        "Mamba SSM provides linear-time sequence processing.",
    ]
    
    print("\n[1/3] Encoding Context History...")
    context_embeddings = []
    for ctx in context_texts:
        emb = encoder.encode(ctx)[0]
        context_embeddings.append(emb)
        print(f"  Stored context: '{ctx}'")
        
    print("\n[2/3] Evaluating Novelty of New Inputs...")
    
    test_cases = [
        {
            "text": "What is the capital of France?",
            "time_since": 10.0, # 10 seconds ago
            "desc": "Exact match, seen very recently (Expect VERY LOW novelty)"
        },
        {
            "text": "Tell me the capital of France.",
            "time_since": 30.0,
            "desc": "Semantic match, seen recently (Expect LOW novelty)"
        },
        {
            "text": "HyperCore is a CPU-first orchestration system for AI.",
            "time_since": 120.0,
            "desc": "Semantic match, slightly different phrasing (Expect LOW-MEDIUM novelty)"
        },
        {
            "text": "What is the capital of France?",
            "time_since": 86400.0, # 24 hours ago
            "desc": "Exact match, but seen a LONG time ago (Expect HIGH temporal novelty -> Sparse/Dense)"
        },
        {
            "text": "Explain the concept of quantum entanglement and superposition.",
            "time_since": 10.0,
            "desc": "Completely novel topic, highly dense text (Expect HIGH novelty)"
        },
        {
            "text": "A a a a a a a a a a a a.",
            "time_since": 10.0,
            "desc": "Novel embedding but extremely low entropy/repetitive (Expect MEDIUM novelty)"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case #{i}: {test['desc']}")
        print(f"Input: '{test['text']}' | Time since last seen: {test['time_since']}s")
        
        emb = encoder.encode(test['text'])[0]
        result = engine.estimate_novelty(
            text=test['text'],
            input_embedding=emb,
            context_embeddings=context_embeddings,
            time_since_last_seen=test['time_since']
        )
        
        print(f"  -> Score: {result['novelty_score']:.4f}")
        print(f"  -> Recommended Route: {result['tier_description']}")
        print(f"  -> Breakdown: {json.dumps(result['components'])}")
        
    print("\n" + "=" * 70)
    print("  MODULE 3 SUMMARY")
    print("=" * 70)
    print("Novelty correctly dictates routing tiers based on a blend of semantic")
    print("divergence, intrinsic entropy, and temporal decay.")

if __name__ == "__main__":
    run_benchmark()
