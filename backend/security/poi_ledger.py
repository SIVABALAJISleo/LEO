"""
backend/security/poi_ledger.py
LEO AI V44 "OMNISCIENCE" — Blockchain-Verified "Proof of Intelligence" (PoI) ledger.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Dict, Any, List


class ProofOfIntelligenceBlock:
    """A single signed block in the local Proof of Intelligence ledger."""

    def __init__(
        self,
        index: int,
        timestamp: float,
        previous_hash: str,
        metrics: Dict[str, Any],
        seal_signature: str = ""
    ):
        self.index = index
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.metrics = metrics
        self.seal_signature = seal_signature
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Compute the SHA-256 hash of the block's content."""
        raw = f"{self.index}{self.timestamp}{self.previous_hash}{json.dumps(self.metrics)}{self.seal_signature}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "metrics": self.metrics,
            "seal_signature": self.seal_signature,
            "hash": self.hash
        }


class ProofOfIntelligenceLedger:
    """Lightweight local P2P blockchain tracking LEO V44 performance metrics."""

    def __init__(self):
        self.chain: List[ProofOfIntelligenceBlock] = []
        # Create genesis block
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = ProofOfIntelligenceBlock(
            index=0,
            timestamp=time.time(),
            previous_hash="0" * 64,
            metrics={"info": "LEO V44 Genesis Block"},
            seal_signature="OMNISCIENCE_GENESIS"
        )
        self.chain.append(genesis)

    def get_latest_block(self) -> ProofOfIntelligenceBlock:
        return self.chain[-1]

    def add_metric_block(self, metrics: Dict[str, Any]) -> ProofOfIntelligenceBlock:
        """Creates, signs, and appends a new verified metric block."""
        latest = self.get_latest_block()
        idx = latest.index + 1
        ts = time.time()
        
        # Sign the block using a simulated keypair signature
        raw_seal = f"LEO_V44_SEAL_{idx}_{ts}_{metrics.get('avoidance_rate_pct', 99.0):.1f}_{metrics.get('avg_watts', 15.0):.1f}"
        signature = hashlib.sha256(raw_seal.encode()).hexdigest()[:32]
        
        block = ProofOfIntelligenceBlock(
            index=idx,
            timestamp=ts,
            previous_hash=latest.hash,
            metrics=metrics,
            seal_signature=signature
        )
        self.chain.append(block)
        return block

    def verify_chain(self) -> bool:
        """Validates the cryptographic integrity of the ledger chain."""
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]
            if curr.hash != curr.calculate_hash():
                return False
            if curr.previous_hash != prev.hash:
                return False
        return True


# Global Singleton Ledger
_poi_ledger = ProofOfIntelligenceLedger()


def get_poi_ledger() -> ProofOfIntelligenceLedger:
    return _poi_ledger
