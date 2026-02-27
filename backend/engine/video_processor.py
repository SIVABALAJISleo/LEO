import asyncio
import logging
import subprocess
import os

from backend.core.hyper_config import config

logger = logging.getLogger(__name__)

class VideoProcessor:
    """
    Handles headless CPU/iGPU video encoding bridging using local FFmpeg.
    Asynchronous architecture prevents blocking the FastAPI loop.
    """
    
    def __init__(self):
        self._check_ffmpeg()
        
    def _check_ffmpeg(self):
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            self.available = True
        except FileNotFoundError:
            logger.error("FFmpeg not found in PATH. Video processing restricted.")
            self.available = False
            
    async def encode_video(self, input_path: str, output_path: str, codec: str = "libx264") -> bool:
        """
        Runs an FFmpeg process asynchronously.
        Thread/Performance settings driven by Phase 6 config.
        """
        if not self.available:
            logger.error("VideoProcessor: ffmpeg not installed.")
            return False
            
        if not os.path.exists(input_path):
            logger.error(f"VideoProcessor: Input file {input_path} missing.")
            return False
            
        cmd = [
            "ffmpeg", "-y",  # Overwrite output
            "-i", input_path,
        ]
        
        # Hardware acceleration injection based on config
        if config.ENABLE_IGPU_ACCEL:
            # We add generic fallback flags that help on QuickSync / VAAPI based instances
            # If they fail, ffmpeg softly falls back to CPU based on the software codec requested.
            cmd.insert(1, "-hwaccel")
            cmd.insert(2, "auto")

        cmd.extend([
            "-c:v", codec,
            "-preset", config.FFMPEG_PRESET,
            "-crf", str(config.FFMPEG_CRF),
            "-threads", str(config.RENDER_THREADS), # Distribute across allowed cores
            "-c:a", "aac",
            output_path
        ])
        
        logger.info(f"Starting async video encode: {' '.join(cmd)}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Video encoded successfully: {output_path}")
                return True
            else:
                logger.error(f"Video encode failed:\n{stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"FFmpeg exception: {e}")
            return False

video_processor = VideoProcessor()
