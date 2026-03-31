import os
import base64
import logging
import io
from typing import List, Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

class TextCompositionEngine:
    """Assembles text from fragments and templates. Point 3 (Knowledge Composition)"""
    TEMPLATES = {
        "definition": "# Definition: {entity}\n\n{text}\n\n## Key Characteristics\n{fragments}",
        "steps": "# Actionable Steps: {entity}\n\n{text}\n\n## Workflow\n{fragments}",
        "examples": "# Practical Examples: {entity}\n\n{text}\n\n## Contextual Instances\n{fragments}",
        "advantages": "# Strategic Advantages: {entity}\n\n{text}\n\n## Benefits\n{fragments}",
    }

    def compose(self, intent: str, entity: str, base_text: str, fragments: List[str]) -> str:
        """Standard assembly from base text and list of strings."""
        from backend.core.refiner import global_refiner
        template_key = "definition" if intent not in self.TEMPLATES else intent
        template = self.TEMPLATES.get(template_key)
        fragment_str = "\n".join([f"- {f}" for f in fragments])
        raw_composed = template.format(entity=entity, text=base_text, fragments=fragment_str)
        return global_refiner.refine(raw_composed)

    def compose_from_fragments(self, entity: str, fragment_data: Dict[str, str]) -> str:
        """AI Systems Architect (Point 3): Build graph of reusable fragments."""
        parts = []
        for key in ["definition", "steps", "examples", "advantages"]:
            if key in fragment_data:
                template = self.TEMPLATES[key]
                parts.append(template.format(entity=entity, text=fragment_data[key], fragments=""))
        
        return "\n\n---\n\n".join(parts)

class ImageCompositionEngine:
    """Procedural image rendering using Pillow. NO DIFFUSION."""
    def __init__(self):
        # Use a system font if available, fallback to default
        try:
            self.font = ImageFont.truetype("arial.ttf", 24)
        except:
            self.font = ImageFont.load_default()

    def generate_card(self, title: str, subtitle: str, theme: str = "dark") -> str:
        """Generates a base64 encoded PNG card."""
        bg_color = (30, 30, 30) if theme == "dark" else (240, 240, 240)
        text_color = (255, 255, 255) if theme == "dark" else (0, 0, 0)
        
        img = Image.new('RGB', (800, 450), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Add a subtle gradient/border
        draw.rectangle([10, 10, 790, 440], outline=(100, 100, 100), width=2)
        
        draw.text((50, 50), title, font=self.font, fill=text_color)
        draw.text((50, 100), subtitle, font=self.font, fill=(150, 150, 150))
        
        # Save to buffer
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode('utf-8')

class VideoCompositionEngine:
    """Frame-based video assembly using MoviePy. NO AI MODELS."""
    def compose_quick(self, title: str, duration: int = 3) -> str:
        """Assembles a simple MP4/GIF from procedural frames."""
        try:
            from moviepy.editor import ColorClip, TextClip, CompositeVideoClip
            
            # Simple 3-second clip
            bg = ColorClip(size=(1280, 720), color=(0, 0, 40), duration=duration)
            txt = TextClip(title, fontsize=70, color='white', font='Arial', duration=duration).set_position('center')
            
            import tempfile
            video = CompositeVideoClip([bg, txt])
            output_path = os.path.join(tempfile.gettempdir(), f"composed_video_{hash(title)}.mp4")
            video.write_videofile(output_path, fps=24, codec="libx264", logger=None)
            
            with open(output_path, "rb") as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"video_composition_failed: {e}")
            return ""

class UniversalComposer:
    def __init__(self):
        self.text = TextCompositionEngine()
        self.image = ImageCompositionEngine()
        self.video = VideoCompositionEngine()

    def assemble(self, request_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Route to appropriate composition engine."""
        if request_type == "text":
            result = self.text.compose(
                intent=data.get("intent", "default"),
                entity=data.get("entity", "Result"),
                base_text=data.get("base_text", ""),
                fragments=data.get("fragments", [])
            )
            return {"type": "text", "content": result}
            
        elif request_type == "image":
            b64_img = self.image.generate_card(
                title=data.get("title", "HYPER Card"),
                subtitle=data.get("subtitle", "Composition Engine v1"),
                theme=data.get("theme", "dark")
            )
            return {"type": "image", "content": b64_img, "format": "png"}
            
        elif request_type == "video":
            b64_vid = self.video.compose_quick(
                title=data.get("title", "HYPER Motion")
            )
            return {"type": "video", "content": b64_vid, "format": "mp4"}
            
        return {"error": "unknown_composition_type"}

global_composer = UniversalComposer()
