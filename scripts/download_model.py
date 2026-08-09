import os
import requests

MODEL_URL = "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "qwen2.5-0.5b-instruct-q4_k_m.gguf")

def download_model():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Downloading model from {MODEL_URL}...")
    response = requests.get(MODEL_URL, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0

    with open(OUTPUT_PATH, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    pct = (downloaded / total_size) * 100
                    print(f"\rProgress: {downloaded / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB ({pct:.1f}%)", end="")
    print("\nDownload finished successfully!")
    print(f"Model saved to: {os.path.abspath(OUTPUT_PATH)}")

if __name__ == "__main__":
    download_model()
