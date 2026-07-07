import sys
import os

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hyper_runtime.speculative_decoding.speculative_decoder import SpeculativeExecutionEngine

def run_benchmark():
    print("=" * 70)
    print("  HYPERCORE RUNTIME — MODULE 5: SPECULATIVE EXECUTION ENGINE")
    print("=" * 70)
    
    # K=4 means we draft 4 tokens before verifying them
    engine = SpeculativeExecutionEngine(k_draft_tokens=4, acceptance_rate=0.7)
    
    test_cases = [
        {
            "desc": "Novel Query (Relies on Draft Model)",
            "prompt": "Explain quantum tunneling in microprocessors.",
            "target": 30
        },
        {
            "desc": "Cached Query (Uses Replay-Assisted Speculation)",
            "prompt": "What is the capital of France?",
            "target": 30
        }
    ]
    
    print("\n[Executing Speculative Generation]")
    print("-" * 70)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nWorkload #{i}: {test['desc']}")
        print(f"Prompt: '{test['prompt']}' | Target length: {test['target']} tokens")
        
        result = engine.generate(test["prompt"], target_length=test["target"])
        metrics = result["metrics"]
        
        print(f"  Speedup Factor:          {metrics['speedup_factor']}x")
        print(f"  Draft Acceptance Ratio:  {metrics['acceptance_ratio']*100:.1f}%")
        print(f"  Replay-Assisted Drafts:  {metrics['replay_assisted_drafts']}")
        print(f"  Actual Wall-Clock Time:  {metrics['wall_clock_time']:.3f}s")
        print(f"  Baseline Est. Time:      {metrics['baseline_time_estimate']:.3f}s")
        
    print("\n" + "=" * 70)
    print("  MODULE 5 SUMMARY")
    print("=" * 70)
    print("Speculative execution allows the heavy CPU model to verify multiple tokens")
    print("in parallel, achieving massive latency reduction without sacrificing quality.")

if __name__ == "__main__":
    run_benchmark()
