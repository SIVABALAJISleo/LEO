import numpy as np
import random

class GossipWorker:
    def __init__(self, node_id, peers, learning_rate=0.01):
        self.node_id = node_id
        self.peers = peers
        self.model_weights = np.random.randn(1000).astype(np.float32) * 0.01
        self.learning_rate = learning_rate
        
    def train_step(self):
        grad = np.random.randn(1000).astype(np.float32)
        self.model_weights -= self.learning_rate * grad
        
    def gossip(self, peer_weights):
        self.model_weights = (self.model_weights + peer_weights) / 2.0

class GossipSwarm:
    def __init__(self, num_nodes=4):
        self.nodes = [GossipWorker(i, []) for i in range(num_nodes)]
        for n in self.nodes:
            n.peers = [p for p in self.nodes if p.node_id != n.node_id]
            
    def run_epoch(self):
        for node in self.nodes:
            node.train_step()
            
        for node in self.nodes:
            peer = random.choice(node.peers)
            node.gossip(peer.model_weights)
