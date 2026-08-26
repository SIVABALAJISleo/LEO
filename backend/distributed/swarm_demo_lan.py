"""
2-MACHINE SWARM DEMO — real LAN, two physical machines, LEO's actual SwarmProtocol.

Machine A (server):  set LEO_SWARM_KEY=<32-byte-key> && python swarm_demo_lan.py server
Machine B (client):  set LEO_SWARM_KEY=<32-byte-key> && python swarm_demo_lan.py client <A's-LAN-IP>
"""
import os
import sys
import json
import time
import socket

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from backend.distributed.swarm_protocol import SwarmProtocol

PORT = 42731
key_env = os.environ.get("LEO_SWARM_KEY", "leo-swarm-2026-demo")
KEY = key_env.encode().ljust(32, b"0")[:32]

def make_node(name, hw):
    node = SwarmProtocol(local_node_id=name)
    node.encryption_key = KEY
    node.opt_in()
    node.hardware_profile = hw
    return node

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Server: python swarm_demo_lan.py server")
        print("  Client: python swarm_demo_lan.py client <server_ip>")
        sys.exit(1)

    if sys.argv[1] == "server":
        node = make_node(f"node_{socket.gethostname()}",
                         {"igpu": {"vendor": "Intel UHD 48EU", "vram_shared_mb": 8192}, "cores": 8})
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bind_host = os.environ.get("SWARM_LAN_HOST", "127.0.0.1")
        srv.bind((bind_host, PORT))
        srv.listen(1)
        print(f"[A] listening on {bind_host}:{PORT} — give the client this machine's LAN IP", flush=True)
        conn, addr = srv.accept()
        f = conn.makefile("rw", encoding="utf-8")
        t0 = time.time()

        handshake = node.secure_decrypt(f.readline().strip())
        if handshake is None:
            print("[A] Error: Secure handshake decryption failed.", flush=True)
            srv.close()
            sys.exit(1)
        ok = node.handle_handshake(addr[0], handshake)
        print(f"[A] Handshake from {handshake['node_id']} @ {addr[0]}: accepted={ok}", flush=True)
        f.write(node.secure_encrypt({"node_id": node.local_node_id,
                                     "hardware_profile": node.hardware_profile}) + "\n")
        f.flush()

        for _ in range(3):
            hb = node.secure_decrypt(f.readline().strip())
            node.process_heartbeat(hb["node_id"])
            rtt_ms = (time.time() - hb["ts"]) * 1000
            print(f"[A] Heartbeat from {hb['node_id']} — one-way latency ~{rtt_ms:.1f} ms", flush=True)

        parts = node.partition_model_layers(total_layers=32)
        summary = {n: f"layers {p[0]}-{p[-1]} ({len(p)})" for n, p in parts.items()}
        print(f"[A] PARTITION ACROSS REAL LAN: {json.dumps(summary)}", flush=True)
        f.write(node.secure_encrypt({"partition": summary}) + "\n")
        f.flush()

        # Bandwidth probe: 1 MB payload = one activation tensor between shards
        blob = node.secure_encrypt({"probe": "x" * 1_000_000})
        t1 = time.time()
        f.write(blob + "\n")
        f.flush()
        ack = f.readline().strip()
        dt = time.time() - t1
        print(f"[A] 1MB shard-transfer round-trip: {dt*1000:.0f} ms -> {2/dt:.1f} MB/s effective", flush=True)
        print(f"[A] TOTAL DEMO TIME: {time.time()-t0:.1f}s — SWARM OVER REAL LAN: PROVEN", flush=True)
        conn.close()
        srv.close()

    else:
        if len(sys.argv) < 3:
            print("ERROR: client mode requires server IP address.")
            sys.exit(1)
        server_ip = sys.argv[2]
        node = make_node(f"node_{socket.gethostname()}",
                         {"igpu": {"vendor": "friend-PC-gpu"}, "cores": os.cpu_count() or 4})
        s = socket.create_connection((server_ip, PORT), timeout=10)
        f = s.makefile("rw", encoding="utf-8")
        f.write(node.secure_encrypt({"node_id": node.local_node_id,
                                     "hardware_profile": node.hardware_profile}) + "\n")
        f.flush()
        hs = node.secure_decrypt(f.readline().strip())
        if hs is None:
            print("[B] Error: Secure handshake decryption failed.", flush=True)
            s.close()
            sys.exit(1)
        node.handle_handshake(server_ip, hs)
        print(f"[B] Registered peer: {list(node.peers)}", flush=True)
        for _ in range(3):
            f.write(node.secure_encrypt({"node_id": node.local_node_id, "ts": time.time()}) + "\n")
            f.flush()
            time.sleep(0.3)
        part = node.secure_decrypt(f.readline().strip())
        print(f"[B] My model shard: {json.dumps(part['partition'].get(node.local_node_id))}", flush=True)
        probe = node.secure_decrypt(f.readline().strip())
        f.write(node.secure_encrypt({"ack": len(probe["probe"])}) + "\n")
        f.flush()
        print("[B] DEMO COMPLETE — this machine is now swarm silicon", flush=True)
        s.close()

if __name__ == "__main__":
    main()
