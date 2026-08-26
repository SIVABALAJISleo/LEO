import socket
import logging
import pickle

logger = logging.getLogger(__name__)

class SwarmNodeHandler:
    """
    Handles pipeline parallelism execution and UDP handoffs.
    Compresses activations to 1.58-bit before transit to save bandwidth.
    """
    def __init__(self, port: int = 59843):
        self.port = port
        import os
        host = os.environ.get("SWARM_NODE_HOST", "127.0.0.1")
        self.socket.bind((host, self.port))
        
    def compress_activations(self, tensor):
        """Simulates 1.58-bit ternary compression for activations before transit."""
        # A simple sign thresholding simulation for demonstration
        import numpy as np
        return np.sign(tensor).astype(np.int8)
        
    def decompress_activations(self, compressed_tensor):
        import numpy as np
        return compressed_tensor.astype(np.float32)

    def send_layer_handoff(self, target_ip: str, layer_idx: int, activation_tensor):
        """Sends the layer activation to the next node in the pipeline."""
        compressed = self.compress_activations(activation_tensor)
        payload = pickle.dumps({"layer_idx": layer_idx, "tensor": compressed})
        
        # In a real kernel-bypass setup, we'd use DPDK/io_uring here.
        # We simulate with standard UDP.
        self.socket.sendto(payload, (target_ip, self.port))
        logger.info(f"[SwarmNode] Handed off layer {layer_idx} execution to {target_ip}")

    def receive_layer_handoff(self, timeout=2.0):
        """Receives activation from previous node."""
        self.socket.settimeout(timeout)
        try:
            data, addr = self.socket.recvfrom(65535) # Max UDP size
            payload = pickle.loads(data)
            tensor = self.decompress_activations(payload["tensor"])
            return payload["layer_idx"], tensor, addr[0]
        except socket.timeout:
            return None, None, None
        except Exception as e:
            logger.error(f"[SwarmNode] Receive error: {e}")
            return None, None, None

    def close(self):
        self.socket.close()
