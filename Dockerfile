# Multi-stage build for HYPER Production Engine
# Stage 1: Build the Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production Runtime
FROM python:3.10-slim AS runtime
WORKDIR /app

# Install system dependencies for OpenCV and MediaPipe
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and engines
COPY . .

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/dist ./dist

# Set environment variables
ENV PYTHONPATH=.
ENV PORT=8005
ENV NODE_ENV=production

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8005/health || exit 1

EXPOSE 8005

# Start the unified engine
CMD ["python", "backend/main.py"]
