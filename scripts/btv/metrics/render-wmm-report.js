#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const reportPath = path.resolve(process.cwd(), '.buildtovalue/reports/what-matters.json');
let report;
try {
  report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
} catch (error) {
  console.error(`Failed to read What Matters report at ${reportPath}:`, error.message);
  process.exit(1);
}

const statusEmoji = (status) => (status === 'PASS' ? '✅' : '❌');
const overallStatus = report.overall_status === 'PASS' ? '✅ PASS' : '⚠️ NEEDS ATTENTION';

const lines = [];
lines.push('## 📊 What Matters Metrics Report');
lines.push('');
lines.push(`**Window:** ${report.window_days} days  `);
lines.push(`**Overall Status:** ${overallStatus}`);
lines.push('');

lines.push('### DORA Metrics');
lines.push('| Metric | Value | Target | Status |');
lines.push('|--------|-------|--------|--------|');
lines.push(`| Deployment Frequency | ${report.dora_metrics.deployment_frequency.value} deploys | ≥${report.dora_metrics.deployment_frequency.target} | ${statusEmoji(report.dora_metrics.deployment_frequency.status)} |`);
lines.push(`| Lead Time | ${Math.round(report.dora_metrics.lead_time_for_changes.value)} min | ≤${report.dora_metrics.lead_time_for_changes.target} min | ${statusEmoji(report.dora_metrics.lead_time_for_changes.status)} |`);
lines.push(`| Change Failure Rate | ${(report.dora_metrics.change_failure_rate.value * 100).toFixed(1)}% | ≤15% | ${statusEmoji(report.dora_metrics.change_failure_rate.status)} |`);
lines.push(`| MTTR | ${Math.round(report.dora_metrics.mean_time_to_recovery.value)} min | ≤${report.dora_metrics.mean_time_to_recovery.target} min | ${statusEmoji(report.dora_metrics.mean_time_to_recovery.status)} |`);
lines.push('');

lines.push('### Quality Metrics');
lines.push('| Metric | Value | Target | Status |');
lines.push('|--------|-------|--------|--------|');
lines.push(`| Flaky Test Rate | ${(report.quality_metrics.flaky_test_rate.value * 100).toFixed(1)}% | ≤2% | ${statusEmoji(report.quality_metrics.flaky_test_rate.status)} |`);
lines.push(`| AI Rework Ratio | ${(report.quality_metrics.ai_rework_ratio.value * 100).toFixed(1)}% | ≤15% | ${statusEmoji(report.quality_metrics.ai_rework_ratio.status)} |`);

console.log(lines.join('\n'));
