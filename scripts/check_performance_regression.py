"""Check for performance regressions."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def check_regression() -> None:
    """Check if performance metrics regressed."""

    results_file = Path("reports/performance-results.json")
    baseline_file = Path("reports/performance-baseline.json")

    if not results_file.exists():
        print("❌ No performance results found")
        sys.exit(1)

    with results_file.open() as file:
        results = json.load(file)

    if not baseline_file.exists():
        print("⚠️  No baseline found, creating new baseline")
        baseline_file.write_text(json.dumps(results, indent=2))
        sys.exit(0)

    with baseline_file.open() as file:
        baseline = json.load(file)

    regressions: list[dict[str, float]] = []

    for test_name, current_time in results.items():
        if test_name in baseline:
            baseline_time = baseline[test_name]
            regression_pct = ((current_time - baseline_time) / baseline_time) * 100

            if regression_pct > 20:
                regressions.append(
                    {
                        "test": test_name,
                        "baseline": baseline_time,
                        "current": current_time,
                        "regression": regression_pct,
                    }
                )

    if regressions:
        print("❌ Performance regressions detected:")
        for item in regressions:
            print(
                f"   {item['test']}: {item['baseline']:.2f}ms → {item['current']:.2f}ms "
                f"({item['regression']:+.1f}%)"
            )
        sys.exit(1)

    print("✅ No performance regressions detected")
    sys.exit(0)


if __name__ == "__main__":
    check_regression()
