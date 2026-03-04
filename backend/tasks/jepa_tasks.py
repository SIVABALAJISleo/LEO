import io
import base64
import logging
from PIL import Image

from backend.celery_app import app

logger = logging.getLogger(__name__)

_jepa_processor = None
_jepa_model = None

_blip_processor = None
_blip_model = None

def get_jepa_model():
    global _jepa_processor, _jepa_model
    if _jepa_model is None:
        import torch
        from transformers import AutoImageProcessor, AutoModel
        
        model_name = "google/vit-base-patch16-224-in21k"
        _jepa_processor = AutoImageProcessor.from_pretrained(model_name)
        _jepa_model = AutoModel.from_pretrained(model_name)
        _jepa_model.eval()
    return _jepa_processor, _jepa_model

def get_blip_model():
    global _blip_processor, _blip_model
    if _blip_model is None:
        from transformers import AutoProcessor, BlipForConditionalGeneration
        
        model_name = "Salesforce/blip-image-captioning-base"
        _blip_processor = AutoProcessor.from_pretrained(model_name)
        _blip_model = BlipForConditionalGeneration.from_pretrained(model_name)
    return _blip_processor, _blip_model

@app.task(bind=True, name="sota.caption")
def caption_image(self, image_base64: str):
    """Generates an english caption for a given image bytes array."""
    try:
        image_bytes = base64.b64decode(image_base64)
        raw_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        processor, model = get_blip_model()
        
        inputs = processor(raw_image, return_tensors="pt")
        out = model.generate(**inputs, max_new_tokens=50)
        
        caption = processor.decode(out[0], skip_special_tokens=True)
        
        return {
            "status": "success",
            "caption": caption
        }
    except Exception as exc:
        logger.error(f"BLIP Caption Task Failed: {exc}")
        raise self.retry(exc=exc, countdown=5)

@app.task(bind=True, name="sota.jepa_compare")
def compare_images(self, context_base64: str, target_base64: str):
    import torch
    import torch.nn.functional as F
    
    try:
        ctx_image = Image.open(io.BytesIO(base64.b64decode(context_base64))).convert("RGB")
        tgt_image = Image.open(io.BytesIO(base64.b64decode(target_base64))).convert("RGB")
        
        processor, model = get_jepa_model()
        
        def _embed(img):
            inputs = processor(images=img, return_tensors="pt")
            with torch.no_grad():
                outputs = model(**inputs)
            if outputs.pooler_output is not None:
                return outputs.pooler_output
            return outputs.last_hidden_state.mean(dim=1)
            
        h_c = _embed(ctx_image)
        h_t = _embed(tgt_image)
        
        similarity = F.cosine_similarity(h_c, h_t, dim=-1).item()
        normalized_score = max(0.0, min(1.0, (similarity + 1.0) / 2.0))
        
        return {
            "status": "success",
            "similarity_score": round(similarity, 4),
            "normalized_percentage": round(normalized_score * 100, 2)
        }
    except Exception as exc:
        logger.error(f"JEPA Comparison Task Failed: {exc}")
        raise self.retry(exc=exc, countdown=5)
