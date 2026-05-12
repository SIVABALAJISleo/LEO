FROM python:3.11-slim

# Avoid GPU bloat - CPU only build
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies (CPU optimized llama-cpp-python)
COPY requirements.txt .
ENV CMAKE_ARGS="-DLLAMA_AVX512=ON -DLLAMA_AVX2=ON"
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn "pydantic[email]"

# Copy app code
COPY project_leo /app/project_leo

EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "project_leo.api.routes:app", "--host", "0.0.0.0", "--port", "8000"]
