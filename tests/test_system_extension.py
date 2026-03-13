import sys
import sys
import os

# Ensure backend modules are importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestration.visibility_manager import VisibilityManager, VisibilityRegionType
from orchestration.specular_governor import SpecularGovernor
from orchestration.chaos_containment import ChaosContainment
from orchestration.entropy_accounting import EntropyAccountant, ComputeType

def test_visibility_manager():
    """Module 40: Verify visibility cost accounting."""
    vm = VisibilityManager()
    
    # Test 1: Register known region
    vm.register_region("region_1", VisibilityRegionType.KNOWN)
    
    # Test 2: Request known region (should be cheap)
    res1 = vm.request_visibility("region_1")
    assert res1["status"] == "visible"
    assert res1["compute_cost"] == 0.01
    
    # Test 3: Request unknown region (should be expensive)
    res2 = vm.request_visibility("region_unknown")
    assert res2["status"] == "visible"
    assert res2["compute_cost"] == 1.0 # Expensive creation
    
    # Test 4: Request same unknown region again (should now be cheap/known)
    res3 = vm.request_visibility("region_unknown")
    assert res3["compute_cost"] == 0.01 # Now cached
    
    print("\n✓ Visibility Manager Logic Verified")

def test_specular_governor():
    """Module 41: Verify path complexity bounding."""
    gov = SpecularGovernor(max_depth=4)
    
    # Test 1: Simple Path (Depth 2)
    simple_rays = [{"energy": 1.0}, {"energy": 0.8}]
    res1 = gov.evaluate_path(simple_rays)
    assert res1["status"] == "analytic"
    assert res1["final_depth"] == 2
    
    # Test 2: Infinite Mirror (Depth 5 > Limit 4)
    complex_rays = [{"energy": 0.9} for _ in range(10)]
    res2 = gov.evaluate_path(complex_rays)
    assert res2["status"] == "bounded"
    assert res2["final_depth"] == 5 # Stops exactly at limit + 1 check loop
    assert res2["governance_note"] == "Approximation used"
    
    print("✓ Specular Governor Logic Verified")

def test_chaos_containment():
    """Module 42: Verify chaos stability enforcement."""
    chaos = ChaosContainment(lyapunov_threshold=0.5)
    
    # Test 1: Stable System (Low Lyapunov)
    res_stable = chaos.analyze_trajectory(initial_state=1.0, time_steps=100, lyapunov_exponent=0.1)
    assert res_stable["mode"] == "DETERMINISTIC_TRAJECTORY"
    
    # Test 2: Chaotic System (High Lyapunov)
    res_chaos = chaos.analyze_trajectory(initial_state=1.0, time_steps=100, lyapunov_exponent=1.2)
    assert res_chaos["mode"] == "STATISTICAL_ENVELOPE"
    assert "envelope_divergence" in res_chaos
    
    print("✓ Chaos Containment Logic Verified")

def test_entropy_accounting():
    """Module 43: Verify compute cost tracking."""
    accountant = EntropyAccountant()
    
    # Perform operations
    accountant.record_operation("Read Cache", ComputeType.EVALUATION)
    accountant.record_operation("Vector Math", ComputeType.DERIVATION)
    accountant.record_operation("Generate Perlin Noise", ComputeType.CREATION)
    
    # Check audit
    report = accountant.get_audit_report()
    
    assert report["total_entropy_units"] == 1.0 + 10.0 + 100.0
    assert report["breakdown"]["creation"] == 100.0
    assert report["ledger_count"] == 3
    
    print("✓ Entropy Accounting Logic Verified")

if __name__ == "__main__":
    test_visibility_manager()
    test_specular_governor()
    test_chaos_containment()
    test_entropy_accounting()
    print("\nALL SYSTEM EXTENSION TESTS PASSED.")
