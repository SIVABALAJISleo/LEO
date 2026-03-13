#!/bin/bash
# HYPER Production Deployment Orchestrator
# This script builds and launches the full-stack engine in one command.

echo "🚀 Starting HYPER Production Build..."

# 1. Clean up old builds
rm -rf dist/

# 2. Start Docker Orchestration
echo "🐳 Building and starting containers..."
docker-compose up --build -d

echo "✅ HYPER is now running at http://localhost:8000"
echo "📊 Monitor status: docker-compose logs -f"
