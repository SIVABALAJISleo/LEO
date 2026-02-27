#!/bin/bash
ROOT=$(dirname "$0")/..
mkdir -p "$ROOT/test-results"
echo "Starting Integration Tests..."
npx vitest run --reporter=json --outputFile="$ROOT/test-results/integration-vitest.json"
