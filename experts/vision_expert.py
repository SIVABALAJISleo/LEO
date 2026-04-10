import logging
import numpy as np
import cv2
from typing import Dict, Any, List

try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    HAS_MEDIAPIPE = True
except ImportError:
    HAS_MEDIAPIPE = False

logger = logging.getLogger(__name__)

class VisionExpert:
    """
    Expert for processing visual data (images, video frames).
    CPU-Native vision using MediaPipe.
    """
    def __init__(self):
        self.hands = None
        self.persisted_objects = {} # Map of ID -> {landmarks, confidence, last_seen}
        self.object_id_counter = 0
        
        if HAS_MEDIAPIPE:
            try:
                # Initialize MediaPipe Hands in CPU mode (Stream mode for temporal persistence)
                self.mp_hands = mp.solutions.hands
                self.hands = self.mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=4, # Increased for complex scenes
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                logger.info("VisionExpert initialized with MediaPipe Hands (Static/Stream CPU)")
            except Exception as e:
                logger.error(f"Failed to init MediaPipe: {e}")
        else:
            logger.info("VisionExpert initialized (Mock Mode - MediaPipe missing)")

    def run(self, query: str) -> str:
        """Standard expert interface for MoE router."""
        return f"Vision expert analyzing command: '{query}'. MediaPipe backend: {'ACTIVE' if self.hands else 'MOCK'}"

    def analyze_frame(self, frame: np.ndarray, frame_id: int = 0) -> Dict[str, Any]:
        """Process a single frame for landmarks with spatial persistence."""
        if not self.hands or frame is None:
            return {"status": "mock", "detections": [{"label": "human", "conf": 0.99}]}
            
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        detections = []
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                label = results.multi_handedness[idx].classification[0].label
                confidence = results.multi_handedness[idx].classification[0].score
                
                # Spatial Persistence Logic: Calculate Centroid
                landmarks = hand_landmarks.landmark
                cx = sum([lm.x for lm in landmarks]) / len(landmarks)
                cy = sum([lm.y for lm in landmarks]) / len(landmarks)
                
                # Check for existing objects in proximity
                tracked_id = None
                for obj_id, data in self.persisted_objects.items():
                    dist = np.sqrt((cx - data['cx'])**2 + (cy - data['cy'])**2)
                    if dist < 0.1: # Proximity threshold
                        tracked_id = obj_id
                        break
                
                if tracked_id is None:
                    tracked_id = self.object_id_counter
                    self.object_id_counter += 1
                
                # Update persistence
                self.persisted_objects[tracked_id] = {
                    "label": label,
                    "cx": cx,
                    "cy": cy,
                    "last_seen_frame": frame_id,
                    "confidence": confidence
                }

                detections.append({
                    "id": tracked_id,
                    "label": f"Hand ({label})",
                    "status": "TRACKED" if tracked_id in self.persisted_objects else "NEW",
                    "landmarks_count": len(landmarks),
                    "confidence": confidence
                })
        
        # Cleanup old persisted objects (optional, for memory)
        if frame_id % 30 == 0:
            self.persisted_objects = {k: v for k, v in self.persisted_objects.items() if frame_id - v['last_seen_frame'] < 30}

        return {
            "status": "success",
            "backend": "MediaPipe",
            "detections": detections,
            "persisted_objects_count": len(self.persisted_objects)
        }

    def process_video_sampling(self, video_path: str, interval_sec: float = 1.0) -> List[Dict[str, Any]]:
        """Sample-based inference for CPU stability."""
        logger.info(f"Sampling video {video_path} every {interval_sec}s")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
             return [{"error": "Could not open video"}]

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        interval_frames = max(1, int(fps * interval_sec))
        
        results = []
        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
                
            if frame_idx % interval_frames == 0:
                analysis = self.analyze_frame(frame, frame_id=frame_idx)
                results.append({
                    "frame_idx": frame_idx,
                    "timestamp": frame_idx / fps,
                    **analysis
                })
            frame_idx += 1
            
        cap.release()
        return results

