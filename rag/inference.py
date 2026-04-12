import structlog
import os
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

logger = structlog.get_logger()

class LocalInference:
    def __init__(self, model_path: str = None, **kwargs):
        self.model_path = model_path or os.getenv("MODEL_PATH", "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
        self.llm = None
        
        # Ensure models directory exists
        models_dir = os.path.dirname(self.model_path)
        if models_dir and not os.path.exists(models_dir):
            os.makedirs(models_dir, exist_ok=True)

        if Llama and os.path.exists(self.model_path):
            logger.info("loading_local_model", path=self.model_path)
            # Use n_threads from kwargs if provided, else default to 4
            n_threads = kwargs.get("n_threads", 4)
            self.llm = Llama(model_path=self.model_path, n_ctx=2048, n_threads=n_threads)
        else:
            download_url = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
            error_msg = f"ERROR: Model matching '{self.model_path}' not found! System requires a GGUF model for inference."
            logger.error("model_not_found", path=self.model_path, download_url=download_url)
            print(f"\n{'-'*50}\n{error_msg}")
            print(f"Please download the model from: {download_url}")
            print(f"And place it at: {os.path.abspath(self.model_path)}\n{'-'*50}\n")

    def generate(self, prompt: str, max_tokens: int = 512, stream: bool = False):
        if not self.llm:
            error_msg = "Error: Local inference model not loaded."
            if stream:
                def error_gen(): yield error_msg
                return error_gen()
            return error_msg
        
        logger.info("generating_response", prompt_length=len(prompt), stream=stream)
        if stream:
            return self.llm(
                prompt,
                max_tokens=max_tokens,
                stop=["<|user|>", "\n\n"],
                echo=False,
                stream=True
            )
        else:
            output = self.llm(
                prompt,
                max_tokens=max_tokens,
                stop=["<|user|>", "\n\n"],
                echo=False
            )
            return output['choices'][0]['text']

if __name__ == "__main__":
    # Mock generation if model doesn't exist
    inference = LocalInference()
    print(inference.generate("Hello, who are you?"))
