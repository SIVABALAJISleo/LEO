import numpy as np
from core_ai.verification.zkp_z3_verifier import ZKPVerifier
from core_ai.contract_engine import AlgorithmicAlchemyContract

def run_tests():
    print("--- LEO v6.0 Algorithmic Alchemy Test Suite ---")
    
    # 1. Test KAN Subsumption
    print("\n[1] Testing KAN Subsumption Bypass")
    contract = AlgorithmicAlchemyContract()
    X = np.random.randn(256, 128).astype(np.float32)
    W = np.random.randn(128, 256).astype(np.float32)
    
    kan_out = contract.execute_gemm(X, W, precision_req='KAN_APPROX')
    print(f"KAN Output Shape: {kan_out.shape}")
    print(f"KAN Sample Val: {kan_out[0,0]:.4f}")
    
    # 2. Test Topological Shape Preservation
    print("\n[2] Testing Topological Shape Preservation")
    X_big = np.random.randn(256, 256).astype(np.float32)
    W_big = np.random.randn(256, 256).astype(np.float32)
    
    topo_out = contract.execute_gemm(X_big, W_big, preserve_shape=True)
    print(f"Topological Output Shape: {topo_out.shape} (Must remain 256x256 despite 128x128 core)")
    
    # 3. Test DFA Engine with Z3 Verification
    print("\n[3] Testing DFA Engine (Int8) & Z3 Verification")
    A = np.random.randint(-128, 127, size=(64, 64), dtype=np.int8)
    B = np.random.randint(-128, 127, size=(64, 64), dtype=np.int8)
    
    C = contract.execute_gemm(A, B, precision_req='INT8')
    
    verifier = ZKPVerifier()
    # Test Z3 Verifier on a subset to keep it fast
    # A and B are Int8, C is Int32
    verifier.prove_equivalence_int8(A, B, C)
    
if __name__ == "__main__":
    run_tests()
