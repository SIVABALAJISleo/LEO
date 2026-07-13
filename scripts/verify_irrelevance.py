import time
import os
import sys
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bypass.leo_irrelevance_engine import IrrelevanceEngine

def simulate_video_stream():
    """Simulates a video stream of 100 frames where objects move slightly."""
    logger.info("Generating simulated video stream...")
    frames = []
    base_frame = np.random.randn(720, 1280, 3) # 720p HD frame
    for i in range(100):
        # 90% of frames have < 5% shift
        if i % 10 != 0:
            shift = np.random.randn(720, 1280, 3) * 0.01
            frames.append(base_frame + shift)
        else:
            # 10% of frames have > 5% shift (scene change / fast motion)
            base_frame = np.random.randn(720, 1280, 3)
            frames.append(base_frame)
    return frames

def run_verification():
    print("="*60)
    print("LEO AI: THE IRRELEVANCE PROTOCOL VERIFICATION")
    print("="*60)
    
    engine = IrrelevanceEngine()
    frames = simulate_video_stream()
    
    start_time = time.perf_counter()
    
    for i, frame in enumerate(frames):
        # The engine processes the frame, attempting all 3 bypass layers
        output = engine.process_frame(frame)
        
    end_time = time.perf_counter()
    
    total_time = end_time - start_time
    fps = len(frames) / total_time
    
    print("\n--- VERIFICATION RESULTS ---")
    print(f"Total Frames Processed : {len(frames)}")
    print(f"Total Time             : {total_time:.4f} seconds")
    print(f"Effective FPS          : {fps:.2f}")
    
    print("\n============================================================")
    if fps > 500:
        print("                 IRRELEVANCE PROTOCOL PASSED [OK]")
    else:
        print("                 IRRELEVANCE PROTOCOL FAILED [ERR]")
    print("============================================================\n")

if __name__ == "__main__":
    run_verification()
