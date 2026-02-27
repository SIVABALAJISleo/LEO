import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class EngineAdapter:
    """
    Integrates external engine outputs as consumable runtime media.
    Principle: Only load and stream, never render.
    """
    def __init__(self):
        self.supported_engines = ["unity", "unreal", "godot", "blender", "omniverse"]

    def load_output(self, engine_name: str, output_path: str) -> Dict[str, Any]:
        if engine_name.lower() not in self.supported_engines:
            raise ValueError(f"Engine {engine_name} not supported.")
            
        logger.info(f"Connecting to {engine_name} stream at {output_path}")
        
        # In a CPU-first system, we don't render. We consume a stream or pre-baked files.
        if os.path.isdir(output_path):
            return self._handle_frame_sequence(output_path)
        elif output_path.startswith(("rtsp://", "rtmp://", "http://")):
            return self._handle_network_stream(output_path)
        else:
            return self._handle_video_file(output_path)

    def _handle_frame_sequence(self, path: str) -> Dict[str, Any]:
        frames = sorted([f for f in os.listdir(path) if f.endswith(('.png', '.jpg', '.exr'))])
        return {
            "type": "frame_sequence",
            "path": path,
            "frame_count": len(frames),
            "is_hdr": any(f.endswith('.exr') for f in frames),
            "sample_frames": frames[:5]
        }

    def _handle_video_file(self, path: str) -> Dict[str, Any]:
        return {
            "type": "video",
            "path": path,
            "size": os.path.getsize(path) if os.path.exists(path) else 0,
            "codec": "h264" # Placeholder
        }

    def _handle_network_stream(self, url: str) -> Dict[str, Any]:
        return {
            "type": "stream",
            "url": url,
            "status": "connected"
        }
