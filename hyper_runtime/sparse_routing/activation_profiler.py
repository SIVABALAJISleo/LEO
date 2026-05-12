import numpy as np
from sparse_router import SparseExpertRouter
from mod_runtime import MixtureOfDepthsRuntime

def profile_sparsity():
    seq_len = 2048
    hidden_dim = 4096
    h = np.random.randn(seq_len, hidden_dim)
    
    router = SparseExpertRouter(num_experts=8, top_k=2)
    indices, _ = router.route(h)
    moe_compute_reduction = 1.0 - (2.0 / 8.0) 
    
    mod = MixtureOfDepthsRuntime(capacity_factor=0.25)
    participating, capacity = mod.forward(h, layer_id=1)
    mod_compute_reduction = mod.analyze_compute_reduction(seq_len) 
    
    print(f"--- Activation Sparsity Profile ---")
    print(f"Sequence Length: {seq_len}")
    print(f"MoE Active Experts: {2}/8 -> {moe_compute_reduction*100:.1f}% FFN compute avoided")
    print(f"MoD Token Capacity: {capacity}/{seq_len} -> {mod_compute_reduction*100:.1f}% Block compute avoided")

if __name__ == "__main__":
    profile_sparsity()
