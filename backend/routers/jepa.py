import os
import io
import logging
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List
from pydantic import BaseModel

try:
    import torch
    import torch.nn.functional as F
    from torchvision import transforms
    from PIL import Image
    from transformers import AutoImageProcessor, AutoModel
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("torch or transformers not installed. JEPA module disabled.")

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/jepa", tags=["JEPA"])

# Lazy load the vision transformer
_processor = None
_model = None

def get_jepa_model():
    global _processor, _model
    if not TORCH_AVAILABLE:
        raise HTTPException(status_code=503, detail="PyTorch/Transformers dependencies are not installed.")
    
    if _model is None:
        logger.info("Loading Vision Transformer (ViT) into CPU memory for JEPA embeddings...")
        # A lightweight ViT model for semantic embedding extraction
        model_name = "google/vit-base-patch16-224-in21k"
        try:
            _processor = AutoImageProcessor.from_pretrained(model_name)
            _model = AutoModel.from_pretrained(model_name)
            _model.eval() # Set to evaluation mode
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            raise HTTPException(status_code=500, detail="Failed to load JEPA base encoder.")
    return _processor, _model

def get_image_embedding(image: Image.Image) -> torch.Tensor:
    processor, model = get_jepa_model()
    # Preprocess image
    inputs = processor(images=image, return_tensors="pt")
    
    # Extract features without gradient calculation for speed
    with torch.no_grad():
        outputs = model(**inputs)
        
    # Standard ViT pooler output serves as our abstract 'context' embedding (h_c or h_t)
    # Shape: (1, hidden_size) e.g. (1, 768)
    embedding = outputs.pooler_output
    if embedding is None:
        # Fallback to mean of last hidden state if no pooler
         embedding = outputs.last_hidden_state.mean(dim=1)
         
    return embedding

@router.post("/compare")
async def compare_images(
    context_file: UploadFile = File(...),
    target_file: UploadFile = File(...)
):
    """
    Implements a basic representation of JEPA's Joint Embedding comparison:
    1. Passes Context Image -> Encoder -> hc (Context Embedding)
    2. Passes Target Image -> Encoder -> ht (Target Embedding)
    3. Calculates abstract abstract Cosine Similarity between them.
    Returns the similarity score (0.0 to 1.0)
    """
    if not TORCH_AVAILABLE:
        raise HTTPException(status_code=503, detail="JEPA module disabled.")
        
    if not context_file.content_type.startswith('image/') or not target_file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Both files must be images.")

    try:
        # Read and open Context Image (x_c)
        ctx_content = await context_file.read()
        ctx_image = Image.open(io.BytesIO(ctx_content)).convert("RGB")
        
        # Read and open Target Image (x_t)
        tgt_content = await target_file.read()
        tgt_image = Image.open(io.BytesIO(tgt_content)).convert("RGB")
        
        # 1. Encoders (f_c and f_t - here sharing the same weight space for simplicity)
        h_c = get_image_embedding(ctx_image)
        h_t = get_image_embedding(tgt_image)
        
        # 3. Predictor/Loss Function proxy: Cosine similarity between target and context
        # sim(h_c, h_t)
        similarity = F.cosine_similarity(h_c, h_t, dim=-1)
        sim_score = similarity.item() # Convert 1D tensor to float
        
        # In a full JEPA, we would calculate L2 loss against a predicted \hat{h}_t,
        # but for demonstration we show raw similarity.
        # Ensure score is roughly 0-100% scale
        normalized_score = max(0.0, min(1.0, (sim_score + 1.0) / 2.0))
        
        return {
            "status": "success",
            "similarity_score": round(sim_score, 4),
            "normalized_percentage": round(normalized_score * 100, 2),
            "embedding_dimension": h_c.shape[-1]
        }

    except Exception as e:
        logger.error(f"Error during JEPA comparison: {e}")
        raise HTTPException(status_code=500, detail=f"JEPA inference failed: {str(e)}")
