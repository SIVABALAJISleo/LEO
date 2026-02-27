import os
import logging
import subprocess

logger = logging.getLogger(__name__)

class QuantizationPipeline:
    """
    Handles automatic conversion and quantization of HuggingFace models
    to GGUF format for optimal CPU inference.
    Requires `llama.cpp` to be built or cloned locally to use `convert.py` and `quantize`.
    """
    def __init__(self, llama_cpp_dir: str = "./llama.cpp"):
        self.llama_cpp_dir = llama_cpp_dir
        self.convert_script = os.path.join(llama_cpp_dir, "convert.py")
        self.quantize_bin = os.path.join(llama_cpp_dir, "quantize")

    def is_available(self) -> bool:
        return os.path.exists(self.convert_script) and os.path.exists(self.quantize_bin)

    def convert_hf_to_gguf(self, hf_model_path: str, output_path: str, outtype: str = "f16") -> bool:
        """Converts a standard HuggingFace model directory to a GGUF file (typically f16 baseline)."""
        logger.info(f"Converting HF model {hf_model_path} to GGUF format...")
        try:
            cmd = [
                "python", self.convert_script,
                hf_model_path,
                "--outfile", output_path,
                "--outtype", outtype
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Conversion successful: {output_path}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Conversion failed: {e.output}")
            return False
            
    def quantize_gguf(self, input_gguf: str, output_gguf: str, method: str = "q4_k_m") -> bool:
        """
        Quantizes a GGUF file to a smaller bit format (e.g., Q4_K_M for heavy CPU optimization).
        """
        logger.info(f"Quantizing {input_gguf} to {method} format...")
        try:
            cmd = [
                self.quantize_bin,
                input_gguf,
                output_gguf,
                method
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Quantization successful: {output_gguf}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Quantization failed: {e.output}")
            return False

# Easy facade for the backend to interact with
quantizer = QuantizationPipeline()
