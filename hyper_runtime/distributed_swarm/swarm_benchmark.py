import sys
import os
import time

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hyper_runtime.distributed_swarm.delta_coherence_bus import DeltaCoherenceBus
from hyper_runtime.distributed_swarm.federated_routing_memory import FederatedRoutingMemory

def run_benchmark():
    print("=" * 70)
    print("  HYPERCORE RUNTIME — MODULE 11: DISTRIBUTED CPU SWARM ENGINE")
    print("=" * 70)
    
    # Initialize Node A (e.g., Edge Device in New York)
    bus_a = DeltaCoherenceBus(node_id="Node_NY_01")
    FederatedRoutingMemory()
    
    # Initialize Node B (e.g., Edge Device in London)
    bus_b = DeltaCoherenceBus(node_id="Node_LDN_02")
    memory_b = FederatedRoutingMemory()
    
    # Connect them via the Coherence Bus
    bus_a.register_peer("Node_LDN_02")
    bus_b.register_peer("Node_NY_01")
    # In this mock, we map the queues manually to simulate the network
    bus_a.peer_queues["Node_LDN_02"] = []
    bus_b.peer_queues["Node_NY_01"] = []
    
    print("\n[1] Node NY encounters a novel workload cluster and explores.")
    cluster_hash = "hash_financial_q3_report"
    
    # Node A discovers that this cluster can be safely routed to Speculative Decoding
    # saving 60% of FLOPs, rather than exact fallback.
    print(f"    Node_NY_01 discovers safe route: 'Speculative Decoding' for {cluster_hash}")
    
    delta_payload = {
        "cluster_id": cluster_hash,
        "best_route": "Speculative Decoding",
        "confidence": 0.92
    }
    
    # Node A broadcasts the delta
    bus_a.broadcast_delta("route_discovery", delta_payload)
    
    print("\n[2] Asynchronous Delta Synchronization...")
    # Simulate network transfer
    time.sleep(0.1)
    
    # Node B receives the broadcast via its queue (simulating bus poll)
    received_events_b = bus_a.peer_queues["Node_LDN_02"]
    
    for event in received_events_b:
        print(f"    Node_LDN_02 received topic: '{event['topic']}' from {event['node_id']}")
        memory_b.apply_delta(event)
        
    print("\n[3] Node London encounters the same workload cluster.")
    # Node B checks its memory
    route = memory_b.get_route(cluster_hash)
    print(f"    Node_LDN_02 routing decision: {route}")
    
    print("\n" + "=" * 70)
    print("  MODULE 11 SUMMARY")
    print("=" * 70)
    print("By broadcasting routing discovery deltas, the CPU Swarm amortizes the cost")
    print("of exploring computational shortcuts. When one node discovers a cheap path,")
    print("all connected nodes instantly inherit that intelligence via the Delta Bus.")

if __name__ == "__main__":
    run_benchmark()
