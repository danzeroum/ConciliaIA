"""Analyze Locust CSV outputs against ConciliaAI performance SLAs."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

SLAS = {
    "reconciliation_p95_ms": 100,
    "api_p99_ms": 500,
    "error_rate_percent": 0.1,
    "throughput_req_per_sec": 2.78,
}


def analyze_performance(csv_path: Path, scenario_name: str) -> bool:
    data = pd.read_csv(csv_path)
    reconciliation = data[data["Name"].str.contains("reconciliation", case=False)]

    if reconciliation.empty:
        print("⚠️  No reconciliation data found in report")
        return False

    row = reconciliation.iloc[0]
    p95_latency = float(row["95%"])
    p99_latency = float(row["99%"])
    request_count = float(row["Request Count"])
    failure_count = float(row["Failure Count"])
    throughput = float(row["Requests/s"])

    error_rate = (failure_count / request_count) * 100 if request_count else 0.0

    print("\n" + "=" * 60)
    print(f"PERFORMANCE ANALYSIS - {scenario_name}")
    print("=" * 60)
    print(f"P95 Latency: {p95_latency:.2f}ms (<= {SLAS['reconciliation_p95_ms']}ms)")
    print(f"P99 Latency: {p99_latency:.2f}ms (<= {SLAS['api_p99_ms']}ms)")
    print(f"Error Rate: {error_rate:.4f}% (<= {SLAS['error_rate_percent']}%)")
    print(
        f"Throughput: {throughput:.2f} req/s (>= {SLAS['throughput_req_per_sec']} req/s)"
    )
    print("=" * 60)

    passed = True

    if p95_latency > SLAS["reconciliation_p95_ms"]:
        print(f"❌ FAILED: P95 latency {p95_latency:.2f}ms exceeds SLA")
        passed = False
    else:
        print("✅ PASSED: P95 latency within SLA")

    if p99_latency > SLAS["api_p99_ms"]:
        print(f"❌ FAILED: P99 latency {p99_latency:.2f}ms exceeds SLA")
        passed = False
    else:
        print("✅ PASSED: P99 latency within SLA")

    if error_rate > SLAS["error_rate_percent"]:
        print(f"❌ FAILED: Error rate {error_rate:.4f}% exceeds SLA")
        passed = False
    else:
        print("✅ PASSED: Error rate within SLA")

    if throughput < SLAS["throughput_req_per_sec"]:
        print(f"❌ FAILED: Throughput {throughput:.2f} req/s below SLA")
        passed = False
    else:
        print("✅ PASSED: Throughput meets SLA")

    print("=" * 60)
    return passed


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python analyze_results.py <csv_path> <scenario_name>")
        return 1

    csv_path = Path(sys.argv[1])
    scenario_name = sys.argv[2]

    if not csv_path.exists():
        print(f"CSV file not found: {csv_path}")
        return 1

    success = analyze_performance(csv_path, scenario_name)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
