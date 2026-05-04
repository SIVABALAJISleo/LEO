import uvicorn
import os

if __name__ == "__main__":
    # Create necessary directories if they don't exist
    os.makedirs("models", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    uvicorn.run("hyper_optimized_ai.app.main:app", host="0.0.0.0", port=8000, reload=False)
