"""
backend/layer8_distributed/cognitive_cdn.py
LEO: STAGE 9 — COGNITIVE CDN

Purpose: Distributable intelligence infrastructure.
Every solved query becomes a procedural asset bundle that can be
replicated globally, achieving 'compute once, reuse globally'.
"""

import gzip
import json
import logging
from typing import Dict, Any

from backend.layer8_distributed.security_trust import trust_layer

logger = logging.getLogger(__name__)

class CognitiveCDN:
    def __init__(self):
        self.status = "ACTIVE"
        logger.info("Stage 9: Cognitive CDN delivery module initialized.")

    def bundle_procedural_asset(self, crystal_payload: Dict[str, Any]) -> bytes:
        """
        Takes a crystallized logic block, signs it via the Trust Layer,
        and compresses it into a distributable edge payload (CDN bundle).
        """
        # 1. Ensure zero-trust provenance
        signed_crystal = trust_layer.sign_crystal(crystal_payload)
        
        # 2. Package metadata
        asset_bundle = {
            "version": "1.0",
            "asset_type": "procedural_graph",
            "data": signed_crystal
        }
        
        # 3. Compress for edge delivery
        serialized = json.dumps(asset_bundle).encode('utf-8')
        compressed_payload = gzip.compress(serialized)
        
        logger.debug(f"Generated Cognitive CDN Bundle: {len(compressed_payload)} bytes.")
        return compressed_payload

    def unpack_and_verify_asset(self, compressed_payload: bytes) -> Dict[str, Any]:
        """
        Receives a compressed CDN bundle from the mesh, decompresses it,
        and validates the cryptographic signature before allowing local execution.
        """
        try:
            serialized = gzip.decompress(compressed_payload)
            asset_bundle = json.loads(serialized)
            
            crystal_data = asset_bundle.get("data", {})
            if not trust_layer.verify_provenance(crystal_data):
                raise ValueError("Signature verification failed for CDN asset.")
                
            logger.info("Successfully unpacked and verified Cognitive CDN asset.")
            return crystal_data
            
        except Exception as e:
            logger.error(f"Failed to unpack Cognitive CDN asset: {e}")
            return {"error": "Asset verification failed."}

    def execute_asset_payload(self, crystal_data: Dict[str, Any], query_context: str) -> str:
        """
        Takes the unpacked procedural source code (AST), dynamically compiles it
        into local memory, and executes it. Bypasses neural inference entirely.
        """
        source = crystal_data.get("source")
        if not source:
            return "Execution failed: No executable source in asset."
            
        try:
            # 1. Compile the AST payload
            code_obj = compile(source, '<string>', 'exec')
            local_vars = {}
            
            # 2. Execute to load function into memory
            exec(code_obj, globals(), local_vars)  # nosec B102
            
            # 3. Call the generated function
            func = local_vars.get('execute_procedural_graph')
            if func:
                return func(query_context.lower())
            else:
                return "Execution failed: Function entrypoint missing."
                
        except Exception as e:
            logger.error(f"Dynamic CDN asset execution failed: {e}")
            return f"Execution error: {e}"

# Singleton for edge CDN routing
cdn_router = CognitiveCDN()
