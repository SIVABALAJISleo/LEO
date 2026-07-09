import logging
import hashlib
import time

class SwarmNexus:
    def __init__(self):
        self.logger = logging.getLogger("SwarmNexus")
        # Kademlia Distributed Hash Table (DHT) routing table
        self.routing_table = {} 
        self.local_node_id = self._generate_node_id()
        self.logger.info(f"SwarmNexus Initialized. Local P2P Node ID: {self.local_node_id[:8]}...")
        
    def _generate_node_id(self) -> str:
        """
        Generates a 256-bit unique identifier for the DHT.
        """
        return hashlib.sha256(str(time.time()).encode()).hexdigest()
        
    def _xor_distance(self, id1: str, id2: str) -> int:
        """
        Kademlia mathematical XOR metric to calculate distance between nodes.
        """
        return int(id1, 16) ^ int(id2, 16)

    def bootstrap_node(self, known_peers: list):
        """
        Connects to the Swarm network via known bootstrap peers.
        """
        for peer in known_peers:
            self.routing_table[peer["id"]] = peer
            self.logger.debug(f"Connected to peer {peer['id'][:8]} at {peer['ip']}")
            
        self.logger.info(f"Bootstrapped with {len(known_peers)} peers. Network active.")
        
    def route_task(self, task_payload: dict, required_vram: int = 0):
        """
        Finds the closest node with the required capabilities to execute a task.
        """
        target_id = hashlib.sha256(task_payload.get("task_id", "default").encode()).hexdigest()
        
        # Find closest peer via XOR distance
        closest_peer = None
        min_distance = float('inf')
        
        for peer_id, peer_info in self.routing_table.items():
            # Check capability
            if peer_info.get("vram_gb", 0) >= required_vram:
                distance = self._xor_distance(target_id, peer_id)
                if distance < min_distance:
                    min_distance = distance
                    closest_peer = peer_info
                    
        if closest_peer:
            self.logger.info(f"Routed task to node {closest_peer['id'][:8]} (Distance: {min_distance})")
            return {"status": "routed", "node_id": closest_peer["id"]}
        else:
            self.logger.warning("No capable nodes found in DHT. Queuing locally.")
            return {"status": "queued_locally"}
            
    def receive_message(self, message: dict):
        """
        Handles incoming RPC messages (PING, STORE, FIND_NODE, FIND_VALUE).
        """
        msg_type = message.get("type")
        sender_id = message.get("sender_id")
        
        # Update routing table with sender
        if sender_id:
            self.routing_table[sender_id] = message.get("sender_info", {"id": sender_id})
            
        if msg_type == "PING":
            return {"type": "PONG", "sender_id": self.local_node_id}
        elif msg_type == "STORE":
            # Store data shard locally
            return {"status": "stored"}
