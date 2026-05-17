import sys
import os
import numpy as np

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hyper_runtime.intelligence_layer.contextual_bandit import ThompsonSamplingRouter
from hyper_runtime.intelligence_layer.drift_detector import ADWINDriveDetector

def run_benchmark():
    print("=" * 70)
    print("  HYPERCORE RUNTIME — MODULE 1: SELF-BUILDING VALUE FUNCTION")
    print("=" * 70)
    
    router = ThompsonSamplingRouter()
    detector = ADWINDriveDetector(delta=0.1)
    
    print("\n[1/3] Initial Expected Routing Values (Prior = Uniform)")
    print("-" * 70)
    for k, v in router.get_routing_probabilities().items():
        print(f"  {k:<25}: Expected Success = {v:.2f}")
        
    print("\n[2/3] Simulating 100 Production Queries (Learning Phase)")
    print("-" * 70)
    
    # We simulate a scenario where "Semantic Replay" is highly successful (0.95 reward)
    # "Speculative Decoding" is moderately successful (0.80 reward)
    # "Exact Fallback" has high quality but massive latency penalty (0.40 reward)
    true_rewards = [0.95, 0.80, 0.70, 0.40]
    
    np.random.seed(42)
    for step in range(100):
        # 1. Select pathway
        chosen_arm = router.select_pathway(np.array([0]))
        
        # 2. Get feedback based on true environment reward distribution
        reward = np.random.normal(true_rewards[chosen_arm], 0.1)
        reward = float(np.clip(reward, 0.0, 1.0))
        
        # 3. Update router value function
        router.update_feedback(chosen_arm, reward)
        
        # 4. Feed reward to drift detector
        drifted = detector.add_element(reward)
        if drifted:
            print(f"    [Step {step}] Drift reported!")
            
    print("\nExpected Routing Success After Learning:")
    for k, v in router.get_routing_probabilities().items():
        print(f"  {k:<25}: Expected Success = {v:.4f}")
        
    print("\n[3/3] Simulating Concept Drift (Environment Change)")
    print("-" * 70)
    print("  Suddenly, 'Semantic Replay' cache matches drop in quality (Reward -> 0.10).")
    
    # Environment changes
    new_true_rewards = [0.10, 0.80, 0.70, 0.40]
    
    for step in range(100):
        chosen_arm = router.select_pathway(np.array([0]))
        reward = np.random.normal(new_true_rewards[chosen_arm], 0.1)
        reward = float(np.clip(reward, 0.0, 1.0))
        
        router.update_feedback(chosen_arm, reward)
        
        # ADWIN will monitor the reward stream
        if detector.add_element(reward):
            print(f"    [Step {step}] ADWIN successfully isolated reward drop / concept drift!")
            break
            
    print("\nPost-Drift expected values:")
    for k, v in router.get_routing_probabilities().items():
        print(f"  {k:<25}: Expected Success = {v:.4f}")
        
    print("\n" + "=" * 70)
    print("  MODULE 1 SUMMARY")
    print("=" * 70)
    print("Thompson Sampling enables LEO to learn the most optimal routing pathway")
    print("directly from production data (regret minimization) without heavy reward loops.")
    print("ADWIN drift detection safeguards the pipeline, resetting window parameters")
    print("the moment a shortcut begins degrading.")

if __name__ == "__main__":
    run_benchmark()
