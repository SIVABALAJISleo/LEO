import io
import base64
import logging
import cv2
import numpy as np
from PIL import Image

from backend.celery_app import app

logger = logging.getLogger(__name__)

# Lazy initialization placeholders
_yolo_model = None
_yolo_seg_model = None

def get_yolo_model():
    global _yolo_model
    if _yolo_model is None:
        logger.info("Initializing YOLO Model in Worker...")
        from ultralytics import YOLO
        _yolo_model = YOLO('yolov8n.pt')
    return _yolo_model
    
def get_yolo_seg_model():
    global _yolo_seg_model
    if _yolo_seg_model is None:
        logger.info("Initializing YOLO SEG Model in Worker...")
        from ultralytics import YOLO
        _yolo_seg_model = YOLO('yolov8n-seg.pt')
    return _yolo_seg_model

def _bytes_to_cv2(image_bytes: bytes) -> np.ndarray:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

@app.task(
    bind=True, 
    name="vision.detect", 
    max_retries=3, 
    autoretry_for=(Exception,), 
    retry_backoff=True, 
    time_limit=180, 
    soft_time_limit=150
)
def detect_objects(self, image_base64: str):
    """
    Executes YOLO bounding box logic.
    Inputs and outputs are stringified bytes (base64) so Redis handles them safely.
    For larger SaaS files, this receives an S3 'key' and downloads the file first.
    """
    try:
        model = get_yolo_model()
        image_bytes = base64.b64decode(image_base64)
        cv_image = _bytes_to_cv2(image_bytes)
        
        results = model(cv_image)
        
        detections = []
        for box in results[0].boxes:
            coords = box.xyxy[0].tolist()
            class_id = int(box.cls[0].item())
            class_name = model.names[class_id]
            confidence = float(box.conf[0].item())
            
            detections.append({
                "class": class_name,
                "confidence": round(confidence, 3),
                "box": {
                    "xmin": round(coords[0], 1), "ymin": round(coords[1], 1),
                    "xmax": round(coords[2], 1), "ymax": round(coords[3], 1)
                }
            })
            
        # Optional: return the parsed image back as base64 or upload to S3 directly here
        annotated_image = results[0].plot()
        is_success, buffer = cv2.imencode(".jpg", annotated_image)
        output_base64 = base64.b64encode(io.BytesIO(buffer).getvalue()).decode('utf-8')
        
        # Upload large output to Object Storage instead of passing through Redis Broker
        from backend.core.storage import upload_base64_result
        # self.request.id is the Celery Job ID
        s3_url = upload_base64_result(self.request.id, "vision_user", output_base64, "jpg")
        
        return {
            "status": "success",
            "detections": detections,
            "image_url": s3_url
        }
        
    except Exception as exc:
        logger.error(f"Vision Detection Task Failed: {exc}")
        raise self.retry(exc=exc, countdown=5)
