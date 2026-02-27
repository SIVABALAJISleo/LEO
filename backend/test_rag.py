from fastapi import FastAPI
from rag.query import RagQueryEngine
import uvicorn

app = FastAPI()
try:
    print("Initializing RAG engine...")
    rag_engine = RagQueryEngine()
    print("RAG engine ready.")
except Exception as e:
    print(f"RAG Error: {e}")

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
