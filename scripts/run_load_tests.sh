#!/bin/bash
set -euo pipefail

echo "🔥 Running Load Tests with Locust"
echo "=================================="

mkdir -p reports

echo "Starting API server..."
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!
trap 'kill $API_PID >/dev/null 2>&1 || true' EXIT

sleep 5

echo "Starting Locust load test..."
locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  --users=100 \
  --spawn-rate=10 \
  --run-time=5m \
  --html=reports/locust-report.html \
  --csv=reports/locust-results

kill $API_PID
trap - EXIT

echo ""
echo "✅ Load tests completed!"
echo "📊 Report: reports/locust-report.html"
