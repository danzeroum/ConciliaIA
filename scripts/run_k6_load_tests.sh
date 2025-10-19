#!/bin/bash
set -euo pipefail

echo "🔥 Running Load Tests with K6"
echo "============================="

mkdir -p reports

echo "Starting API server..."
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!
trap 'kill $API_PID >/dev/null 2>&1 || true' EXIT

sleep 5

echo "Starting K6 load test..."
k6 run tests/load/k6_load_test.js \
  --out json=reports/k6-results.json \
  --summary-export=reports/k6-summary.json

kill $API_PID
trap - EXIT

echo ""
echo "✅ K6 load tests completed!"
echo "📊 Results: reports/k6-results.json"
