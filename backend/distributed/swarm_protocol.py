"""
backend/distributed/swarm_protocol.py
Layer 6 — The Swarm: Peer-to-peer swarm protocol.

Coordinates connection handshake, capability advertising, heartbeats, encryption,
and dynamic fallback routing.
"""

from __future__ import annotations

import os
import asyncio
import logging
import time
import json
import uuid
import hashlib
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class SwarmPeerNode:
    """Represents a discovered peer node participating in the virtual mesh."""

    def __init__(self, node_id: str, ip: str, hardware_profile: Dict[str, Any]):
        self.node_id = node_id
        self.ip = ip
        self.hardware_profile = hardware_profile
        self.status = "ACTIVE"
        self.last_heartbeat = time.time()
        self.assigned_layers: List[int] = []

    def is_alive(self, timeout_seconds: float = 30.0) -> bool:
        return (time.time() - self.last_heartbeat) < timeout_seconds


class SwarmProtocol:
    """
    Manages WebRTC/TCP control sockets and secure fleet coordination.
    Handles opt-in policies, dynamic capability sync, and layer partitioning.
    """

    def __init__(self, local_node_id: Optional[str] = None):
        self.local_node_id = local_node_id or f"node_{uuid.uuid4().hex[:8]}"
        self.opted_in = False
        self.peers: Dict[str, SwarmPeerNode] = {}
        self.encryption_key = os.urandom(32)
        
    def opt_in(self) -> bool:
        """User explicitly opts-in to swarm sharing."""
        self.opted_in = True
        logger.info(f"SwarmProtocol: Node {self.local_node_id} successfully opted-in to the swarm.")
        return True

    def opt_out(self):
        self.opted_in = False
        self.peers.clear()
        logger.info(f"SwarmProtocol: Node {self.local_node_id} opted-out from the swarm.")

    def secure_encrypt(self, payload: Dict[str, Any]) -> str:
        """Simulates end-to-end encrypted packet generation."""
        # Simple JSON conversion and hash signature matching
        serialized = json.dumps(payload)
        sig = hashlib.sha256(serialized.encode() + self.encryption_key).hexdigest()
        return json.dumps({"payload": serialized, "signature": sig})

    def secure_decrypt(self, packet_str: str) -> Optional[Dict[str, Any]]:
        """Decrypts and verifies packet signature."""
        try:
            data = json.loads(packet_str)
            payload_str = data["payload"]
            sig = data["signature"]
            expected_sig = hashlib.sha256(payload_str.encode() + self.encryption_key).hexdigest()
            if sig == expected_sig:
                return json.loads(payload_str)
            else:
                logger.warning("swarm.decryption: Signature validation failed. Packet dropped.")
                return None
        except Exception as e:
            logger.warning(f"swarm.decryption_error: {e}")
            return None

    def handle_handshake(self, ip: str, handshake_packet: Dict[str, Any]) -> bool:
        """Processes peer capability advertisement and registers the node."""
        if not self.opted_in:
            return False

        node_id = handshake_packet.get("node_id")
        hw_profile = handshake_packet.get("hardware_profile")
        
        if not node_id or not hw_profile:
            return False

        # Add or update node
        self.peers[node_id] = SwarmPeerNode(node_id, ip, hw_profile)
        logger.info(f"swarm.handshake_accepted: node_id={node_id} ip={ip} API={hw_profile.get('igpu', {}).get('vendor')}")
        return True

    def process_heartbeat(self, node_id: str):
        """Update last seen timestamp for node."""
        if node_id in self.peers:
            self.peers[node_id].last_heartbeat = time.time()
            self.peers[node_id].status = "ACTIVE"

    def prune_dead_nodes(self, timeout_seconds: float = 15.0):
        """Prunes nodes that missed heartbeat cycles."""
        dead_nodes = [nid for nid, peer in self.peers.items() if not peer.is_alive(timeout_seconds)]
        for nid in dead_nodes:
            logger.warning(f"swarm.peer_timeout: Node {nid} has dropped offline. Re-routing partitions.")
            del self.peers[nid]

    def partition_model_layers(self, total_layers: int = 32) -> Dict[str, List[int]]:
        """
        Dynamically divides model layers across all active nodes based on VRAM capacity.
        Returns: { node_id: [start_layer, ..., end_layer] }
        """
        active_peers = [p for p in self.peers.values() if p.status == "ACTIVE"]
        if not active_peers:
            return {self.local_node_id: list(range(total_layers))}

        # Calculate relative weights based on GPU VRAM or CPU score
        weights: Dict[str, float] = {}
        for peer in active_peers:
            vram = peer.hardware_profile.get("igpu", {}).get("vram_shared_mb", 4096)
            weights[peer.node_id] = max(1.0, vram / 1024.0)

        # Include local node
        weights[self.local_node_id] = 4.0  # mock local weight

        total_weight = sum(weights.values())
        
        # Partition
        partitions: Dict[str, List[int]] = {}
        curr_layer = 0
        
        all_nodes = sorted(weights.keys())
        for idx, node_id in enumerate(all_nodes):
            if idx == len(all_nodes) - 1:
                # Last node gets remainder
                partitions[node_id] = list(range(curr_layer, total_layers))
            else:
                share = int((weights[node_id] / total_weight) * total_layers)
                share = max(1, share)
                partitions[node_id] = list(range(curr_layer, min(total_layers, curr_layer + share)))
                curr_layer += share

        return partitions
