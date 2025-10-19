#!/bin/bash
set -euo pipefail

echo "🚀 Running Performance Test Suite"
echo "=================================="

echo ""
echo "📊 Running matching performance tests..."
pytest tests/performance/test_matching_performance.py -v -m performance

echo ""
echo "📊 Running API performance tests..."
pytest tests/performance/test_api_performance.py -v -m performance

echo ""
echo "📊 Running database performance tests..."
pytest tests/performance/test_database_performance.py -v -m performance

echo ""
echo "📊 Running stress tests..."
pytest tests/stress/test_stress.py -v -m stress

echo ""
echo "✅ Performance test suite completed!"
