import os
import subprocess
import logging
import shutil
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ProxyWorkflow:
    """
    Automates 720p proxy generation for heavy 4K media using FFmpeg.
    Ensures CPU-first playback and editing.
    """
    def __init__(self, proxy_dir: str = "data/proxies"):
        self.proxy_dir = proxy_dir
        os.makedirs(proxy_dir, exist_ok=True)
        self.ffmpeg_available = shutil.which("ffmpeg") is not None
        if not self.ffmpeg_available:
            logger.warning("FFmpeg not found in PATH. Proxy generation will be mocked.")

    def generate_proxy(self, original_path: str) -> str:
        """
        Generate a 720p proxy from 4K/Heavy media.
        """
        if not os.path.exists(original_path):
            logger.error(f"Original file not found: {original_path}")
            return ""

        asset_id = os.path.basename(original_path).split('.')[0]
        proxy_path = os.path.join(self.proxy_dir, f"{asset_id}_proxy.mp4")
        
        if os.path.exists(proxy_path):
            logger.info(f"Proxy already exists for: {original_path}")
            return proxy_path

        logger.info(f"Generating 720p proxy for: {original_path}")
        
        if not self.ffmpeg_available:
            logger.info("MOCK: Simulating FFmpeg proxy generation...")
            # Create a dummy file for testing without ffmpeg
            with open(proxy_path, "w") as f:
                f.write("Mock proxy content")
            return proxy_path
            
        # CPU-optimized FFmpeg command
        # -preset ultrafast: minimize CPU time
        # -vf scale=-1:720: scale to 720p while maintaining aspect ratio
        cmd = [
            "ffmpeg", "-y", "-i", original_path,
            "-vf", "scale=-1:720",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
            "-c:a", "aac", "-b:a", "128k",
            proxy_path
        ]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f"Successfully generated proxy at {proxy_path}")
            return proxy_path
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed: {e.stderr.decode() if e.stderr else 'Unknown error'}")
            return ""
        except Exception as e:
            logger.error(f"Failed to generate proxy: {str(e)}")
            return ""

    def get_export_path(self, asset_id: str, original_path: str, is_final_export: bool) -> str:
        """
        Swap logic: use proxy for viewing, original for export.
        """
        if is_final_export:
            logger.info(f"Final export: using original source {original_path}")
            return original_path
        
        proxy_path = os.path.join(self.proxy_dir, f"{asset_id}_proxy.mp4")
        return proxy_path if os.path.exists(proxy_path) else original_path
