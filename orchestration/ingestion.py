import os
import json
import uuid
import time
from typing import Dict, Any, List
import logging
import mimetypes

logger = logging.getLogger(__name__)

class IngestionManager:
    """
    Handles ingestion of various assets: images, videos, 3D assets, VFX, NeRF, Baked Lightmaps, etc.
    Stores metadata for fast indexing and supports CPU-first proxy/baking workflows.
    """
    def __init__(self, data_dir: str = "data/assets"):
        self.data_dir = data_dir
        self.metadata_file = os.path.join(data_dir, "asset_metadata.json")
        os.makedirs(data_dir, exist_ok=True)
        self.load_metadata()

    def load_metadata(self):
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, "r") as f:
                    self.assets = json.load(f)
            except json.JSONDecodeError:
                logger.error("Failed to decode metadata. Starting fresh.")
                self.assets = {}
        else:
            self.assets = {}

    def save_metadata(self):
        with open(self.metadata_file, "w") as f:
            json.dump(self.assets, f, indent=2)

    def determine_asset_type(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        mime, _ = mimetypes.guess_type(file_path)
        
        if mime and mime.startswith('video'):
            return 'video'
        if mime and mime.startswith('image'):
            return 'image'
        
        if ext in ['.fbx', '.obj', '.gltf', '.glb', '.usd', '.usdc']:
            return '3d_model'
        if ext in ['.abc', '.vdb']:
            return 'vfx_cache'
        if ext in ['.bvh', '.fbx']: # FBX can be both
            return 'mocap'
        if ext in ['.exr', '.hdr']:
            return 'lightmap'
        if ext in ['.nerf', '.splat']:
            return 'nerf_grid'
            
        return 'unknown'

    def ingest(self, file_path: str, asset_type: str = None, metadata: Dict[str, Any] = None) -> str:
        """
        Ingest an asset and categorize it.
        Supported types: 'image', 'video', 'vfx_cache' (Alembic/VDB), 'mocap' (FBX/BVH),
        'lightmap', 'nerf_grid', 'physics_bake'.
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None

        asset_id = str(uuid.uuid4())
        
        if not asset_type:
            asset_type = self.determine_asset_type(file_path)
            
        # For this orchestration system, we track the source and intended storage
        # In a real deployed version, we might copy the file.
        
        asset_info = {
            "id": asset_id,
            "type": asset_type,
            "original_name": os.path.basename(file_path),
            "original_path": os.path.abspath(file_path),
            "timestamp": time.time(),
            "status": "ingested",
            "needs_proxy": asset_type == "video" or asset_type == "vfx_cache",
            "metadata": metadata or {}
        }
        
        self.assets[asset_id] = asset_info
        self.save_metadata()
        
        logger.info(f"Ingested asset {asset_id} of type {asset_type}")
        return asset_id

    def get_asset(self, asset_id: str) -> Dict[str, Any]:
        return self.assets.get(asset_id)

    def list_assets(self, asset_type: str = None) -> List[Dict[str, Any]]:
        if asset_type:
            return [a for a in self.assets.values() if a["type"] == asset_type]
        return list(self.assets.values())
