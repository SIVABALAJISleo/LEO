import os
import io
import logging
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import Response
from typing import Dict, Any
from pydantic import BaseModel

try:
    from ultralytics import YOLO
    from PIL import Image
    import numpy as np
    import cv2
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("ultralytics or cv2 not installed. YOLO Vision module disabled.")

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/vision", tags=["Vision"])

# Lazy load the models to save memory if not used immediately.
# Using YOLOv8n (nano) for CPU-first latency priority.
_model = None
_seg_model = None

# Multimodal LLM (Vision-Language)
_blip_processor = None
_blip_model = None

def get_yolo_model():
    global _model
    if not YOLO_AVAILABLE:
        raise HTTPException(status_code=503, detail="YOLO dependencies are not installed.")
    
    if _model is None:
        logger.info("Loading YOLOv8n model into CPU memory...")
        _model = YOLO('yolov8n.pt') 
    return _model

def get_yolo_seg_model():
    global _seg_model
    if not YOLO_AVAILABLE:
        raise HTTPException(status_code=503, detail="YOLO dependencies are not installed.")
    
    if _seg_model is None:
        logger.info("Loading YOLOv8n-Seg model into CPU memory...")
        _seg_model = YOLO('yolov8n-seg.pt') 
    return _seg_model

def get_blip_model():
    global _blip_processor, _blip_model
    try:
        from transformers import AutoProcessor, BlipForConditionalGeneration
    except ImportError:
        raise HTTPException(status_code=503, detail="Transformers not installed for BLIP.")
        
    if _blip_model is None:
        logger.info("Loading BLIP Image Captioning Model into CPU...")
        model_name = "Salesforce/blip-image-captioning-base"
        _blip_processor = AutoProcessor.from_pretrained(model_name)
        _blip_model = BlipForConditionalGeneration.from_pretrained(model_name)
    return _blip_processor, _blip_model

@router.post("/detect")
async def detect_objects(file: UploadFile = File(...)):
    """
    Receives an image, runs YOLOv8 object detection, and returns the image
    with bounding boxes drawn on it, along with the JSON object detections.
    """
    if not YOLO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Vision module disabled.")
        
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File provided is not an image.")

    try:
        # Read image to memory
        content = await file.read()
        image = Image.open(io.BytesIO(content)).convert("RGB")
        
        # Convert PIL Image to OpenCV format (BGR)
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Run YOLO inference
        model = get_yolo_model()
        results = model(cv_image)
        
        # Plot the bounding boxes on the image
        annotated_image = results[0].plot()
        
        # Extract the detection JSON data
        detections = []
        for box in results[0].boxes:
            # box.xyxy format: [xmin, ymin, xmax, ymax]
            # box.cls: class index
            # box.conf: confidence score
            coords = box.xyxy[0].tolist()
            class_id = int(box.cls[0].item())
            class_name = model.names[class_id]
            confidence = float(box.conf[0].item())
            
            detections.append({
                "class": class_name,
                "confidence": round(confidence, 3),
                "box": {
                    "xmin": round(coords[0], 1),
                    "ymin": round(coords[1], 1),
                    "xmax": round(coords[2], 1),
                    "ymax": round(coords[3], 1)
                }
            })

        # Convert the annotated image back to JPEG bytes to send to frontend
        is_success, buffer = cv2.imencode(".jpg", annotated_image)
        if not is_success:
            raise ValueError("Failed to encode processed image.")
            
        byte_io = io.BytesIO(buffer)
        
        # We can't return both JSON and Binary easily in standard HTTP without Multipart,
        # but for simplicity, we usually return JSON with base64, OR just the binary image.
        # Alternatively, returning the binary as response, and putting metadata in Headers.
        import base64
        base64_encoded = base64.b64encode(byte_io.getvalue()).decode('utf-8')
        
        return {
            "status": "success",
            "detections": detections,
            "image_base64": f"data:image/jpeg;base64,{base64_encoded}"
        }

    except Exception as e:
        logger.error(f"Error processing image for YOLO detection: {e}")
        raise HTTPException(status_code=500, detail=f"Vision processing failed: {str(e)}")

@router.post("/upscale")
async def upscale_image(file: UploadFile = File(...)):
    """
    Dummy endpoint representing Image Upscaling logic requested by user.
    Uses cv2 resize with sophisticated interpolation as a lightweight CPU stand-in
    before heavy GAN implementations.
    """
    if not YOLO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Vision module disabled.")
        
    try:
         content = await file.read()
         image = Image.open(io.BytesIO(content)).convert("RGB")
         cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
         
         # "Upscale" by 2x using Lanczos4 (highest quality CPU cubic filter)
         height, width = cv_image.shape[:2]
         upscaled = cv2.resize(cv_image, (width * 2, height * 2), interpolation=cv2.INTER_LANCZOS4)
         
         is_success, buffer = cv2.imencode(".png", upscaled)
         byte_io = io.BytesIO(buffer)
         
         import base64
         base64_encoded = base64.b64encode(byte_io.getvalue()).decode('utf-8')
         
         return {
             "status": "success",
             "resolution": f"{width*2}x{height*2}",
             "image_base64": f"data:image/png;base64,{base64_encoded}"
         }
    except Exception as e:
         logger.error(f"Error upscaling image: {e}")
         raise HTTPException(status_code=500, detail="Upscaling failed.")

@router.post("/segment")
async def segment_objects(file: UploadFile = File(...)):
    """
    SOTA Masking: Uses YOLO-seg to compute exact pixel boundaries.
    """
    if not YOLO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Vision module disabled.")
    
    try:
        content = await file.read()
        image = Image.open(io.BytesIO(content)).convert("RGB")
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Load Segmentation variant
        model = get_yolo_seg_model()
        results = model(cv_image)
        
        annotated_image = results[0].plot()
        
        is_success, buffer = cv2.imencode(".jpg", annotated_image)
        byte_io = io.BytesIO(buffer)
        
        import base64
        base64_encoded = base64.b64encode(byte_io.getvalue()).decode('utf-8')
        
        return {
            "status": "success",
            "image_base64": f"data:image/jpeg;base64,{base64_encoded}"
        }
    except Exception as e:
        logger.error(f"Semantic Segmentation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Segmentation failed. {str(e)}")

@router.post("/caption")
async def caption_image(file: UploadFile = File(...)):
    """
    Multimodal CV/NLP Integration. Feeds image pixels into BLIP 
    and streams out standard english contextual descriptions.
    """
    try:
        content = await file.read()
        raw_image = Image.open(io.BytesIO(content)).convert("RGB")
        
        processor, model = get_blip_model()
        
        # Unconditional NLP generation
        inputs = processor(raw_image, return_tensors="pt")
        out = model.generate(**inputs, max_new_tokens=50)
        
        caption = processor.decode(out[0], skip_special_tokens=True)
        
        return {
            "status": "success",
            "caption": caption
        }
    except Exception as e:
        logger.error(f"BLIP Captioning failed: {e}")
        raise HTTPException(status_code=500, detail=f"Captioning failed. {str(e)}")
