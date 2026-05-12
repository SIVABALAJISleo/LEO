import os
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SceneDataManager:
    """
    Manages baked scene data: lightmaps, probes, reflection captures.
    Ensures lighting-compute-free rendering on CPU.
    """
    def __init__(self, scene_dir: str = "data/scenes"):
        self.scene_dir = scene_dir
        os.makedirs(scene_dir, exist_ok=True)

    def load_scene_data(self, scene_id: str) -> Dict[str, Any]:
        """
        Loads all baked data associated with a scene.
        """
        path = os.path.join(self.scene_dir, f"{scene_id}_baked.json")
        logger.info(f"Loading baked scene data from: {path}")
        
        if not os.path.exists(path):
            return {"error": f"Baked data for {scene_id} not found."}

        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading scene data: {str(e)}")
            return {"error": str(e)}

    def register_baked_asset(self, scene_id: str, asset_type: str, asset_path: str):
        """
        Registration point for new baked lightmaps or probes.
        """
        # Load or create metadata
        meta_path = os.path.join(self.scene_dir, f"{scene_id}_baked.json")
        data = {}
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                data = json.load(f)
        
        if "assets" not in data:
            data["assets"] = []
            
        data["assets"].append({
            "type": asset_type,
            "path": asset_path,
            "timestamp": "now"
        })
        
        with open(meta_path, "w") as f:
            json.dump(data, f, indent=2)
            
        logger.info(f"Registered {asset_type} for scene {scene_id}")
