#!/usr/bin/env python3
"""BuildToValue v7.4-Platinum - SLO Reporter."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

try:  # pragma: no cover - optional dependency
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:  # pragma: no cover - dependency optional
    MATPLOTLIB_AVAILABLE = False
    print("⚠️ matplotlib não disponível. Instale com: pip install matplotlib", file=sys.stderr)


class SLOReporter:
    """Gerador de relatórios de SLO."""

    def __init__(self, slo_dir: str = ".buildtovalue/slo-reports") -> None:
        self.slo_dir = Path(slo_dir)
        self.slo_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    def load_sli_data(self, days: int = 30) -> List[Dict[str, Any]]:
        data: List[Dict[str, Any]] = []
        for offset in range(days):
            date_str = (datetime.utcnow() - timedelta(days=offset)).strftime("%Y%m%d")
            sli_file = self.slo_dir / f"slis-{date_str}.json"
            if sli_file.exists():
                with sli_file.open("r", encoding="utf-8") as handle:
                    data.append(json.load(handle))
        return sorted(data, key=lambda item: item["timestamp"])

    # ------------------------------------------------------------------
    @staticmethod
    def calculate_error_budget(slo_target: float, actual_rate: float, window_days: int) -> Dict[str, float]:
        error_budget_percent = max(0.0, 100.0 - slo_target)
        errors_allowed = error_budget_percent / 100.0
        actual_errors = max(0.0, (100.0 - actual_rate) / 100.0)
        error_budget_consumed = (actual_errors / errors_allowed * 100.0) if errors_allowed else 0.0
        error_budget_remaining = max(0.0, min(100.0, 100.0 - error_budget_consumed))

        expected_daily_burn = (100.0 / window_days) if window_days else 0.0
        actual_daily_burn = (error_budget_consumed / window_days) if window_days else 0.0
        burn_rate = (actual_daily_burn / expected_daily_burn) if expected_daily_burn else 0.0

        status = "healthy"
        epsilon = 1e-6
        if error_budget_remaining + epsilon < 5:
            status = "critical"
        elif error_budget_remaining + epsilon < 20:
            status = "warning"

        return {
            "error_budget_percent": error_budget_percent,
            "error_budget_consumed": error_budget_consumed,
            "error_budget_remaining": error_budget_remaining,
            "burn_rate": burn_rate,
            "status": status,
        }

    # ------------------------------------------------------------------
    def generate_text_report(self) -> str:
        data = self.load_sli_data(30)
        if not data:
            return "⚠️ Nenhum dado de SLI disponível"

        latest = data[-1]
        slis = latest.get("slis", {})

        def fmt(value: float, suffix: str = "") -> str:
            return f"{value:.2f}{suffix}" if isinstance(value, (int, float)) else str(value)

        report_lines = ["=" * 80, "BuildToValue v7.4-Platinum - SLO Compliance Report", "=" * 80]
        report_lines.append(f"Report Date: {datetime.utcnow():%Y-%m-%d %H:%M:%S UTC}")
        report_lines.append("Data Range: Last 30 days")
        report_lines.append("")

        success_rate = float(slis.get("task_success_rate_30d", 0))
        budget = self.calculate_error_budget(99.5, success_rate, 30)

        report_lines.extend(
            [
                "1. Task Success Rate",
                "-" * 80,
                f"  Current:              {fmt(success_rate, '%')}",
                "  Target:               99.50%",
                f"  Error Budget:         {fmt(budget['error_budget_percent'], '%')}",
                f"  Budget Consumed:      {fmt(budget['error_budget_consumed'], '%')}",
                f"  Budget Remaining:     {fmt(budget['error_budget_remaining'], '%')}",
                f"  Burn Rate:            {budget['burn_rate']:.2f}x",
                f"  Status:               {budget['status'].upper()}",
                "",
            ]
        )

        latency = float(slis.get("task_latency_p95_7d", 0))
        report_lines.extend(
            [
                "2. Task Latency (P95)",
                "-" * 80,
                f"  Current:              {latency:.2f}s",
                "  Target:               ≤10.00s",
                f"  Status:               {'✅ MEETING' if latency <= 10.0 else '❌ EXCEEDING'}",
                "",
            ]
        )

        mpaa = float(slis.get("mpaa_validation_accuracy_7d", 0))
        report_lines.extend(
            [
                "3. MPAA Validation Accuracy",
                "-" * 80,
                f"  Current:              {mpaa:.2f}%",
                "  Target:               ≥95.00%",
                f"  Status:               {'✅ MEETING' if mpaa >= 95.0 else '❌ BELOW'}",
                "",
            ]
        )

        cost = float(slis.get("cost_per_task_30d", 0))
        report_lines.extend(
            [
                "4. Cost Per Task",
                "-" * 80,
                f"  Current:              ${cost:.4f}",
                "  Target:               ≤$0.02",
                f"  Status:               {'✅ MEETING' if cost <= 0.02 else '⚠️ EXCEEDING'}",
                "",
            ]
        )

        meeting_count = sum([success_rate >= 99.5, latency <= 10.0, mpaa >= 95.0, cost <= 0.02])
        compliance = meeting_count / 4 * 100
        report_lines.extend(
            [
                "Overall Assessment",
                "-" * 80,
                f"  SLOs Meeting Target:  {meeting_count}/4",
                f"  Compliance Rate:      {compliance:.1f}%",
            ]
        )

        if meeting_count == 4:
            report_lines.append("  Overall Status:       🟢 EXCELLENT")
        elif meeting_count >= 3:
            report_lines.append("  Overall Status:       🟡 GOOD")
        else:
            report_lines.append("  Overall Status:       🔴 NEEDS ATTENTION")

        report_lines.extend(["", "=" * 80])
        return "\n".join(report_lines)

    # ------------------------------------------------------------------
    def generate_visual_report(self, output_file: str | None = None) -> None:
        if not MATPLOTLIB_AVAILABLE:
            print("❌ matplotlib não disponível para gráficos", file=sys.stderr)
            return

        data = self.load_sli_data(30)
        if not data:
            print("⚠️ Nenhum dado disponível para gráfico", file=sys.stderr)
            return

        timestamps = [datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00")) for item in data]
        success_rates = [item["slis"].get("task_success_rate_30d", 0) for item in data]
        latencies = [item["slis"].get("task_latency_p95_7d", 0) for item in data]
        mpaa_accuracy = [item["slis"].get("mpaa_validation_accuracy_7d", 0) for item in data]
        costs = [item["slis"].get("cost_per_task_30d", 0) for item in data]

        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle("BuildToValue v7.4 - SLO Compliance Dashboard", fontsize=16, fontweight="bold")

        ax1, ax2, ax3, ax4 = axes.flatten()

        ax1.plot(timestamps, success_rates, "b-", linewidth=2, label="Success Rate")
        ax1.axhline(99.5, color="green", linestyle="--", label="Target 99.5%")
        ax1.axhline(98.0, color="orange", linestyle="--", label="Warning 98%")
        ax1.set_title("Task Success Rate (30d)", fontweight="bold")
        ax1.set_ylabel("Success Rate (%)")
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))

        ax2.plot(timestamps, latencies, "r-", linewidth=2, label="P95 Latency")
        ax2.axhline(10.0, color="green", linestyle="--", label="Target 10s")
        ax2.axhline(15.0, color="orange", linestyle="--", label="Warning 15s")
        ax2.set_title("Task Latency P95 (7d)", fontweight="bold")
        ax2.set_ylabel("Latency (s)")
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))

        ax3.plot(timestamps, mpaa_accuracy, "g-", linewidth=2, label="MPAA Accuracy")
        ax3.axhline(95.0, color="green", linestyle="--", label="Target 95%")
        ax3.axhline(90.0, color="orange", linestyle="--", label="Warning 90%")
        ax3.set_title("MPAA Validation Accuracy (7d)", fontweight="bold")
        ax3.set_ylabel("Accuracy (%)")
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        ax3.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))

        ax4.plot(timestamps, costs, "m-", linewidth=2, label="Cost/Task")
        ax4.axhline(0.02, color="green", linestyle="--", label="Target $0.02")
        ax4.axhline(0.05, color="orange", linestyle="--", label="Warning $0.05")
        ax4.set_title("Cost Per Task (30d)", fontweight="bold")
        ax4.set_ylabel("Cost (USD)")
        ax4.grid(True, alpha=0.3)
        ax4.legend()
        ax4.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))

        fig.autofmt_xdate()
        plt.tight_layout()

        if output_file:
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_file, dpi=300, bbox_inches="tight")
            print(f"✅ Gráfico salvo em: {output_file}")
        else:  # pragma: no cover - interactive path
            plt.show()

    # ------------------------------------------------------------------
    def export_markdown(self, output_file: str | None = None) -> str:
        data = self.load_sli_data(30)
        if not data:
            return "⚠️ Nenhum dado disponível"

        latest = data[-1]
        slis = latest.get("slis", {})

        success_rate = float(slis.get("task_success_rate_30d", 0))
        latency = float(slis.get("task_latency_p95_7d", 0))
        mpaa = float(slis.get("mpaa_validation_accuracy_7d", 0))
        cost = float(slis.get("cost_per_task_30d", 0))

        rows = [
            "# BuildToValue v7.4-Platinum - SLO Compliance Report",
            "",
            f"**Report Date:** {datetime.utcnow():%Y-%m-%d %H:%M:%S UTC}",
            "**Data Range:** Last 30 days",
            "",
            "## Summary",
            "",
            "| SLO | Current | Target | Status |",
            "|-----|---------|--------|--------|",
            f"| Task Success Rate | {success_rate:.2f}% | ≥99.5% | {'✅' if success_rate >= 99.5 else '❌'} |",
            f"| Task Latency P95 | {latency:.2f}s | ≤10.0s | {'✅' if latency <= 10.0 else '❌'} |",
            f"| MPAA Accuracy | {mpaa:.2f}% | ≥95.0% | {'✅' if mpaa >= 95.0 else '❌'} |",
            f"| Cost Per Task | ${cost:.4f} | ≤$0.02 | {'✅' if cost <= 0.02 else '⚠️'} |",
            "",
            "## Error Budget Analysis",
            "",
        ]

        budget = self.calculate_error_budget(99.5, success_rate, 30)
        rows.extend(
            [
                f"- **Error Budget:** {budget['error_budget_percent']:.2f}%",
                f"- **Budget Consumed:** {budget['error_budget_consumed']:.2f}%",
                f"- **Budget Remaining:** {budget['error_budget_remaining']:.2f}%",
                f"- **Burn Rate:** {budget['burn_rate']:.2f}x",
                f"- **Status:** {budget['status'].upper()}",
                "",
                "## Recommendations",
                "",
            ]
        )

        if success_rate < 99.5:
            rows.append("- ⚠️ **Task Success Rate** below target: Investigate recent failures")
        if latency > 10.0:
            rows.append("- ⚠️ **Task Latency** exceeding target: Review resource allocation")
        if mpaa < 95.0:
            rows.append("- ⚠️ **MPAA Accuracy** below target: Review validation thresholds")
        if cost > 0.02:
            rows.append("- ⚠️ **Cost Per Task** exceeding target: Optimize provider usage")
        if not any([success_rate < 99.5, latency > 10.0, mpaa < 95.0, cost > 0.02]):
            rows.append("- ✅ All SLOs meeting targets. Excellent performance!")

        rows.extend(["", "---", "*Generated by BuildToValue SLO Reporter v7.4-Platinum*"])
        content = "\n".join(rows)

        if output_file:
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as handle:
                handle.write(content)
            print(f"✅ Relatório Markdown salvo em: {output_file}")

        return content


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BuildToValue SLO Reporter")
    parser.add_argument("--format", choices=["text", "visual", "markdown"], default="text")
    parser.add_argument("--output", "-o", help="Arquivo de saída")
    parser.add_argument("--days", type=int, default=30, help="Dias de dados para análise")
    parser.add_argument("--directory", default=".buildtovalue/slo-reports", help="Diretório de relatórios de SLO")
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    reporter = SLOReporter(args.directory)

    if args.format == "text":
        report = reporter.generate_text_report()
        if args.output:
            with open(args.output, "w", encoding="utf-8") as handle:
                handle.write(report)
            print(f"✅ Relatório salvo em: {args.output}")
        else:
            print(report)
        return 0

    if args.format == "visual":
        if not MATPLOTLIB_AVAILABLE:
            print("❌ matplotlib necessário para relatórios visuais", file=sys.stderr)
            return 1
        output_file = args.output or f"{reporter.slo_dir}/slo-dashboard-{datetime.utcnow():%Y%m%d}.png"
        reporter.generate_visual_report(output_file)
        return 0

    if args.format == "markdown":
        output_file = args.output or f"{reporter.slo_dir}/slo-report-{datetime.utcnow():%Y%m%d}.md"
        reporter.export_markdown(output_file)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
