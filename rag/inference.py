import structlog
import os
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

logger = structlog.get_logger()

class LocalInference:
    def __init__(self, model_path: str = None):
        self.model_path = model_path or os.getenv("MODEL_PATH", "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
        self.llm = None
        if Llama and os.path.exists(self.model_path):
            logger.info("loading_local_model", path=self.model_path)
            self.llm = Llama(model_path=self.model_path, n_ctx=2048, n_threads=4)
        else:
            logger.warning("model_not_found_or_llama_cpp_missing", path=self.model_path)

    def generate(self, prompt: str, max_tokens: int = 512):
        if not self.llm:
            return "Error: Local inference model not loaded. Please check model path and llama-cpp-python installation."
        
        logger.info("generating_response", prompt_length=len(prompt))
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
