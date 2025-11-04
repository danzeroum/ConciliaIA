#!/usr/bin/env bash
# BuildToValue v7.4-Platinum - SLI Calculator
set -euo pipefail

WORKDIR=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

resolve_path() {
  local primary="$1"
  local fallback="$2"
  if [[ -e "$primary" ]]; then
    echo "$primary"
  else
    echo "$fallback"
  fi
}

LEDGER=$(resolve_path "$WORKDIR/.buildtovalue/ledger.jsonl" ".buildtovalue/ledger.jsonl")
COST_LEDGER=$(resolve_path "$WORKDIR/.buildtovalue/cost-ledger.jsonl" ".buildtovalue/cost-ledger.jsonl")
SLOS_CONFIG=$(resolve_path "$WORKDIR/scripts/slo/slos.yaml" "scripts/slo/slos.yaml")

python_calc() {
  local current_py="${PYTHONPATH:-}"
  if [[ -n "$current_py" ]]; then
    PYTHONPATH="$current_py:$WORKDIR" python3 - "$@"
  else
    PYTHONPATH="$WORKDIR" python3 - "$@"
  fi
}

calculate_success_rate_sli() {
  local window_days="${1:-30}"
  python_calc "$LEDGER" "$window_days" <<'PY'
import json, sys, datetime
from pathlib import Path

ledger_path = Path(sys.argv[1])
window_days = int(sys.argv[2])
if not ledger_path.exists():
    print("0")
    raise SystemExit

cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=window_days)
cutoff_iso = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")

total = 0
success = 0
with ledger_path.open("r", encoding="utf-8") as handle:
    for line in handle:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("timestamp", "") < cutoff_iso:
            continue
        total += 1
        if entry.get("result") == "success":
            success += 1

if total == 0:
    print("0")
else:
    print(f"{(success / total) * 100:.2f}")
PY
}

calculate_latency_p95_sli() {
  local window_days="${1:-7}"
  python_calc "$LEDGER" "$window_days" <<'PY'
import json, sys, datetime
from pathlib import Path

ledger_path = Path(sys.argv[1])
window_days = int(sys.argv[2])
if not ledger_path.exists():
    print("0")
    raise SystemExit

cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=window_days)
cutoff_iso = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")

durations = []
with ledger_path.open("r", encoding="utf-8") as handle:
    for line in handle:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("timestamp", "") < cutoff_iso:
            continue
        duration = entry.get("duration_seconds")
        if duration is not None:
            durations.append(float(duration))

if not durations:
    print("0")
else:
    durations.sort()
    index = max(0, min(len(durations) - 1, int(len(durations) * 0.95) - 1))
    print(f"{durations[index]:.2f}")
PY
}

calculate_mpaa_accuracy_sli() {
  local window_days="${1:-7}"
  python_calc "$WORKDIR" "$window_days" <<'PY'
import json, sys, datetime
from pathlib import Path

workdir = Path(sys.argv[1])
window_days = int(sys.argv[2])
reports_dir = workdir / '.buildtovalue' / 'reports'
if not reports_dir.exists():
    print("0")
    raise SystemExit

cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=window_days)
cutoff_ts = cutoff.timestamp()

total = 0
approved = 0
for path in reports_dir.glob("mpaa_result.json*"):
    if not path.is_file():
        continue
    if path.stat().st_mtime < cutoff_ts:
        continue
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        continue
    total += 1
    if data.get("decision") == "approve":
        approved += 1

if total == 0:
    print("0")
else:
    print(f"{(approved / total) * 100:.2f}")
PY
}

calculate_cost_per_task_sli() {
  local window_days="${1:-30}"
  python_calc "$LEDGER" "$COST_LEDGER" "$window_days" <<'PY'
import json, sys, datetime
from pathlib import Path

ledger_path = Path(sys.argv[1])
cost_path = Path(sys.argv[2])
window_days = int(sys.argv[3])
if not ledger_path.exists() or not cost_path.exists():
    print("0")
    raise SystemExit

cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=window_days)
cutoff_iso = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")

total_tasks = 0
with ledger_path.open("r", encoding="utf-8") as handle:
    for line in handle:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("timestamp", "") >= cutoff_iso:
            total_tasks += 1

if total_tasks == 0:
    print("0")
    raise SystemExit

total_cost = 0.0
with cost_path.open("r", encoding="utf-8") as handle:
    for line in handle:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("timestamp", "") >= cutoff_iso:
            total_cost += float(entry.get("cost_usd", 0))

print(f"{total_cost / total_tasks:.4f}")
PY
}

get_target() {
  local slo_name="$1"
  if command -v yq >/dev/null 2>&1; then
    yq -r ".slos[] | select(.name == \"$slo_name\") | .objective.target" "$SLOS_CONFIG"
  else
    case "$slo_name" in
      task_success_rate) echo "99.5" ;;
      task_latency_p95) echo "10.0" ;;
      mpaa_validation_accuracy) echo "95.0" ;;
      cost_per_task) echo "0.02" ;;
      *) echo "0" ;;
    esac
  fi
}

compare_floats() {
  python_calc "$1" "$2" "$3" <<'PY'
import sys
value = float(sys.argv[1])
target = float(sys.argv[2])
operator = sys.argv[3]
if operator == '>=':
    print("1" if value >= target else "0")
elif operator == '<=':
    print("1" if value <= target else "0")
else:
    print("0")
PY
}

generate_sli_report() {
  echo "📊 BuildToValue v7.4 - SLI Report"
  echo "=================================="
  echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo ""

  local success_rate=$(calculate_success_rate_sli 30)
  local success_target=$(get_target "task_success_rate")
  echo "Task Success Rate (30d):"
  echo "  Current: ${success_rate}%"
  echo "  Target: ${success_target}%"
  if [[ $(compare_floats "$success_rate" "$success_target" ">=") == "1" ]]; then
    echo "  Status: ✅ MEETING SLO"
  else
    echo "  Status: ❌ BELOW SLO"
  fi
  echo ""

  local latency_p95=$(calculate_latency_p95_sli 7)
  local latency_target=$(get_target "task_latency_p95")
  echo "Task Latency P95 (7d):"
  echo "  Current: ${latency_p95}s"
  echo "  Target: ≤${latency_target}s"
  if [[ $(compare_floats "$latency_p95" "$latency_target" "<=") == "1" ]]; then
    echo "  Status: ✅ MEETING SLO"
  else
    echo "  Status: ❌ ABOVE SLO"
  fi
  echo ""

  local mpaa_accuracy=$(calculate_mpaa_accuracy_sli 7)
  local mpaa_target=$(get_target "mpaa_validation_accuracy")
  echo "MPAA Validation Accuracy (7d):"
  echo "  Current: ${mpaa_accuracy}%"
  echo "  Target: ≥${mpaa_target}%"
  if [[ $(compare_floats "$mpaa_accuracy" "$mpaa_target" ">=") == "1" ]]; then
    echo "  Status: ✅ MEETING SLO"
  else
    echo "  Status: ❌ BELOW SLO"
  fi
  echo ""

  local cost_per_task=$(calculate_cost_per_task_sli 30)
  local cost_target=$(get_target "cost_per_task")
  echo "Cost Per Task (30d):"
  echo "  Current: \$${cost_per_task}"
  echo "  Target: ≤\$${cost_target}"
  if [[ $(compare_floats "$cost_per_task" "$cost_target" "<=") == "1" ]]; then
    echo "  Status: ✅ MEETING SLO"
  else
    echo "  Status: ⚠️ ABOVE SLO"
  fi
}

export_slis_json() {
  local output_file="${1:-.buildtovalue/slo-reports/slis-$(date +%Y%m%d).json}"
  mkdir -p "$(dirname "$output_file")"
  python_calc "$LEDGER" "$COST_LEDGER" "$output_file" "$WORKDIR" <<'PY'
import json, sys, datetime
from pathlib import Path

ledger_path = Path(sys.argv[1])
cost_path = Path(sys.argv[2])
output_file = Path(sys.argv[3])
workdir = Path(sys.argv[4])

def success_rate(window_days: int) -> float:
    if not ledger_path.exists():
        return 0.0
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=window_days)
    cutoff_iso = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
    total = success = 0
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("timestamp", "") < cutoff_iso:
            continue
        total += 1
        if entry.get("result") == "success":
            success += 1
    return (success / total * 100) if total else 0.0

def latency_p95(window_days: int) -> float:
    if not ledger_path.exists():
        return 0.0
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=window_days)
    cutoff_iso = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
    durations = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("timestamp", "") < cutoff_iso:
            continue
        duration = entry.get("duration_seconds")
        if duration is not None:
            durations.append(float(duration))
    if not durations:
        return 0.0
    durations.sort()
    index = max(0, min(len(durations) - 1, int(len(durations) * 0.95) - 1))
    return durations[index]

def mpaa_accuracy(window_days: int) -> float:
    reports_dir = workdir / '.buildtovalue' / 'reports'
    if not reports_dir.exists():
        return 0.0
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=window_days)
    cutoff_ts = cutoff.timestamp()
    total = approved = 0
    for path in reports_dir.glob('mpaa_result.json*'):
        if not path.is_file() or path.stat().st_mtime < cutoff_ts:
            continue
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            continue
        total += 1
        if data.get('decision') == 'approve':
            approved += 1
    return (approved / total * 100) if total else 0.0

def cost_per_task(window_days: int) -> float:
    if not ledger_path.exists() or not cost_path.exists():
        return 0.0
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=window_days)
    cutoff_iso = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
    total_tasks = 0
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("timestamp", "") >= cutoff_iso:
            total_tasks += 1
    if total_tasks == 0:
        return 0.0
    total_cost = 0.0
    for line in cost_path.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("timestamp", "") >= cutoff_iso:
            total_cost += float(entry.get("cost_usd", 0))
    return total_cost / total_tasks

data = {
    "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "slis": {
        "task_success_rate_30d": success_rate(30),
        "task_latency_p95_7d": latency_p95(7),
        "mpaa_validation_accuracy_7d": mpaa_accuracy(7),
        "cost_per_task_30d": cost_per_task(30),
    },
}
output_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"✅ SLIs exportados para: {output_file}")
PY
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  case "${1:-report}" in
    success-rate)
      calculate_success_rate_sli "${2:-30}"
      ;;
    latency-p95)
      calculate_latency_p95_sli "${2:-7}"
      ;;
    mpaa-accuracy)
      calculate_mpaa_accuracy_sli "${2:-7}"
      ;;
    cost-per-task)
      calculate_cost_per_task_sli "${2:-30}"
      ;;
    report)
      generate_sli_report
      ;;
    export)
      export_slis_json "${2:-}"
      ;;
    *)
      echo "Uso: $0 {success-rate|latency-p95|mpaa-accuracy|cost-per-task|report|export} [window_days]"
      exit 1
      ;;
  esac
fi
