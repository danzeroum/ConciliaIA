#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

API_URL="${API_URL:-http://localhost:8000}"
RESULTS_DIR="tests/performance/results"

mkdir -p "${RESULTS_DIR}"

declare -A SCENARIOS=(
  [phase1_alpha]="users=5,spawn-rate=1,run-time=5m"
  [phase2_beta]="users=50,spawn-rate=5,run-time=10m"
  [phase3_growth]="users=100,spawn-rate=10,run-time=15m"
  [stress_test]="users=200,spawn-rate=20,run-time=5m"
)

run_scenario() {
  local scenario_name="$1"
  local params="$2"

  echo -e "\n${YELLOW}Running scenario: ${scenario_name}${NC}"
  echo "Parameters: ${params}"

  IFS=',' read -r users_param spawn_param runtime_param <<<"${params}"
  local users="${users_param#*=}"
  local spawn_rate="${spawn_param#*=}"
  local run_time="${runtime_param#*=}"

  locust -f tests/performance/locustfile.py \
    --host="${API_URL}" \
    --users="${users}" \
    --spawn-rate="${spawn_rate}" \
    --run-time="${run_time}" \
    --headless \
    --html="${RESULTS_DIR}/${scenario_name}_report.html" \
    --csv="${RESULTS_DIR}/${scenario_name}" \
    --only-summary

  python tests/performance/analyze_results.py \
    "${RESULTS_DIR}/${scenario_name}_stats.csv" \
    "${scenario_name}" || {
      echo -e "${RED}Scenario ${scenario_name} failed quality gates${NC}"
      exit 1
    }

  echo "Cooling down 30s..."
  sleep 30
}

for scenario in "${!SCENARIOS[@]}"; do
  run_scenario "${scenario}" "${SCENARIOS[$scenario]}"
  echo -e "${GREEN}Scenario ${scenario} completed${NC}"
done

printf "\n${GREEN}Performance testing complete! Reports in ${RESULTS_DIR}.${NC}\n"
