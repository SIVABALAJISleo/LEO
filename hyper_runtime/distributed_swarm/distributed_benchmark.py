import time
from diloco_runtime import DiLoCoRuntime
from gossip_trainer import GossipSwarm

def run():
    print("Running Distributed Swarm Benchmarks...")
    
    diloco = DiLoCoRuntime(num_workers=8, inner_steps=100)
    start = time.time()
    diloco.train_round()
    end = time.time()
    print(f"DiLoCo Communication Overhead Avoided: {100 - (1/100)*100}%")
    print(f"DiLoCo Round Latency: {end-start:.3f}s")
    
    swarm = GossipSwarm(num_nodes=8)
    start = time.time()
    for _ in range(10):
        swarm.run_epoch()
    end = time.time()
    print(f"Gossip Decentralized Sync Latency (10 epochs): {end-start:.3f}s")

if __name__ == "__main__":
    run()
