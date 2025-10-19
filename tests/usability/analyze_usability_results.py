"""Aggregate usability testing outcomes and produce a summary report."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Dict, List


def aggregate_usability_results(results_dir: str = "tests/usability/results") -> Dict[str, object]:
    directory = Path(results_dir)
    files = list(directory.glob("P*_results.json"))

    if not files:
        print("⚠️  No usability test results found")
        return {}

    participants: List[dict] = []
    for file in files:
        with file.open("r", encoding="utf-8") as handler:
            participants.append(json.load(handler))

    sus_scores = [entry["sus_score"] for entry in participants if entry.get("sus_score")]
    tasks: Dict[str, Dict[str, object]] = {}

    for entry in participants:
        for task in entry.get("tasks", []):
            task_id = task["task_id"]
            task_stats = tasks.setdefault(
                task_id,
                {
                    "attempts": 0,
                    "successes": 0,
                    "times": [],
                    "clicks": [],
                    "errors": [],
                },
            )
            task_stats["attempts"] += 1
            if task.get("success"):
                task_stats["successes"] += 1
            if task.get("time_seconds") is not None:
                task_stats["times"].append(task["time_seconds"])
            if task.get("clicks") is not None:
                task_stats["clicks"].append(task["clicks"])
            if task.get("errors") is not None:
                task_stats["errors"].append(task["errors"])

    for stats in tasks.values():
        attempts = stats["attempts"] or 1
        stats["completion_rate"] = stats["successes"] / attempts
        stats["avg_time"] = mean(stats["times"]) if stats["times"] else None
        stats["avg_clicks"] = mean(stats["clicks"]) if stats["clicks"] else None
        stats["avg_errors"] = mean(stats["errors"]) if stats["errors"] else None

    aggregated = {
        "participants": len(participants),
        "sus_mean": mean(sus_scores) if sus_scores else None,
        "sus_min": min(sus_scores) if sus_scores else None,
        "sus_max": max(sus_scores) if sus_scores else None,
        "tasks": tasks,
    }
    return aggregated


def print_usability_report(aggregated: Dict[str, object]) -> None:
    if not aggregated:
        return

    print("\n" + "=" * 70)
    print("USABILITY TESTING - CONSOLIDATED REPORT")
    print("=" * 70)
    print(f"Participants: {aggregated['participants']}")

    sus_mean = aggregated.get("sus_mean")
    if sus_mean is not None:
        print("\nSystem Usability Scale (SUS)")
        print("- Mean: {:.1f}".format(sus_mean))
        print("- Min : {:.1f}".format(aggregated.get("sus_min", 0)))
        print("- Max : {:.1f}".format(aggregated.get("sus_max", 0)))

    print("\nTask Performance")
    for task_id, stats in sorted(aggregated.get("tasks", {}).items()):
        print(f"  Task {task_id}")
        print(
            "    Completion Rate: {:.1f}%".format(
                stats["completion_rate"] * 100 if stats.get("completion_rate") else 0.0
            )
        )
        if stats.get("avg_time") is not None:
            print(f"    Avg Time: {stats['avg_time']:.1f}s")
        if stats.get("avg_clicks") is not None:
            print(f"    Avg Clicks: {stats['avg_clicks']:.1f}")
        if stats.get("avg_errors") is not None:
            print(f"    Avg Errors: {stats['avg_errors']:.1f}")

    print("=" * 70 + "\n")


if __name__ == "__main__":
    aggregated = aggregate_usability_results()
    print_usability_report(aggregated)
