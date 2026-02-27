import logging
import time
import os
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HYPER-Minimal")

# Base imports
try:
    from . import models, database, auth
    from .database import engine, get_db
except (ImportError, ValueError):
    import models, database, auth
    from database import engine, get_db

# Create table
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="HYPER: Minimal Debug")

@app.get("/health")
def health():
    return {"status": "ok", "time": time.time()}

@app.post("/api/auth/register")
def register(username: str, db: Session = Depends(get_db)):
    # Very minimal test
    user = models.User(username=username, email=f"{username}@test.com", hashed_password="hashed")
    db.add(user)
    db.commit()
    return {"status": "created", "user": username}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Minimal Engine...")
    uvicorn.run(app, host="0.0.0.0", port=8005)
