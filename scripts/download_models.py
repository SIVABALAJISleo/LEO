import os
import requests
from tqdm import tqdm

MODELS = {
    "tinyllama": {
        "url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
        "filename": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
        "desc": "TinyLlama 1.1B (Quantized INT4) - ~670MB"
    }
}

def download_model(model_id, target_dir="models"):
    if model_id not in MODELS:
        print(f"Error: Model {model_id} not found in manifest.")
        return

    model = MODELS[model_id]
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, model["filename"])

    if os.path.exists(target_path):
        print(f"Model already exists at {target_path}. Skipping.")
        return

    print(f"Downloading {model['desc']}...")
    response = requests.get(model["url"], stream=True)
    total_size = int(response.headers.get('content-length', 0))

    with open(target_path, "wb") as f, tqdm(
        desc=model["filename"],
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            bar.update(size)

    print(f"Download complete! Model saved to {target_path}")

if __name__ == "__main__":
    import sys
    # Default to tinyllama
    model_to_download = "tinyllama"
    if len(sys.argv) > 1:
        model_to_download = sys.argv[1]
    
    download_model(model_to_download)
