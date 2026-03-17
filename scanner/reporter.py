#!/usr/bin/env python3
"""
VeriFlow Security Scanner - Report Generator
=============================================
Generates formatted security reports in multiple output formats:
- Terminal (rich console output)
- JSON (machine-readable)
- HTML (for dashboard integration)
- GitHub Actions annotations
"""

import json
import os
from datetime import datetime
from pathlib import Path
from scanner.analyzer import ScanResult, Severity


SEVERITY_EMOJI = {
    Severity.CRITICAL: "🔴",
    Severity.HIGH: "🟠",
    Severity.MEDIUM: "🟡",
    Severity.LOW: "🔵",
    Severity.INFO: "⚪",
}

SEVERITY_COLOR = {
    Severity.CRITICAL: "#dc2626",
    Severity.HIGH: "#ea580c",
    Severity.MEDIUM: "#ca8a04",
    Severity.LOW: "#2563eb",
    Severity.INFO: "#6b7280",
}


def print_terminal_report(results: list[ScanResult]):
    """Print a formatted report to the terminal."""
    total_findings = sum(len(r.findings) for r in results)
    total_critical = sum(r.critical_count for r in results)
    total_high = sum(r.high_count for r in results)
    total_medium = sum(r.medium_count for r in results)
    total_low = sum(r.low_count for r in results)
    total_files = len(results)
    clean_files = sum(1 for r in results if r.is_clean)

    print()
    print("╔" + "═" * 62 + "╗")
    print("║" + "VeriFlow Security Report".center(62) + "║")
    print("╠" + "═" * 62 + "╣")
    print(f"║  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<54}║")
    print(f"║  Files scanned: {total_files:<45}║")
    print(f"║  Clean files:   {clean_files:<45}║")
    print("╠" + "═" * 62 + "╣")

    if total_findings == 0:
        print("║" + "  ✅ No vulnerabilities detected!".ljust(62) + "║")
    else:
        print("║" + f"  ⚠️  {total_findings} finding(s) detected".ljust(62) + "║")
        print("║" + f"  🔴 Critical: {total_critical}  🟠 High: {total_high}  🟡 Medium: {total_medium}  🔵 Low: {total_low}".ljust(62) + "║")

    print("╚" + "═" * 62 + "╝")

    for result in results:
        if not result.findings:
            print(f"\n  ✅ {result.file_path} — CLEAN ({result.lines_scanned} lines)")
            continue

        print(f"\n  {'⚠️' if result.status == 'WARNING' else '❌'} {result.file_path}")
        print(f"     Modules: {', '.join(result.modules_found)}")
        print(f"     Lines: {result.lines_scanned} | Findings: {len(result.findings)}")
        print()

        for finding in result.findings:
            emoji = SEVERITY_EMOJI.get(finding.severity, "❓")
            print(f"     {emoji} [{finding.severity.value.upper()}] {finding.rule_id}: {finding.rule_name}")
            print(f"        Line {finding.line_number}: {finding.line_content}")
            print(f"        → {finding.description}")
            print(f"        💡 {finding.recommendation}")
            print()

    # Overall status
    if total_critical > 0 or total_high > 0:
        print("═" * 64)
        print("  OVERALL STATUS: ❌ FAIL — Critical/High vulnerabilities found")
        print("═" * 64)
        return False
    elif total_medium > 0:
        print("═" * 64)
        print("  OVERALL STATUS: ⚠️  WARNING — Medium issues found")
        print("═" * 64)
        return True
    else:
        print("═" * 64)
        print("  OVERALL STATUS: ✅ PASS")
        print("═" * 64)
        return True


def generate_json_report(results: list[ScanResult], output_path: str):
    """Generate a JSON report for machine consumption."""
    report = {
        "veriflow_version": "1.0.0",
        "scan_date": datetime.now().isoformat(),
        "summary": {
            "total_files": len(results),
            "total_findings": sum(len(r.findings) for r in results),
            "critical": sum(r.critical_count for r in results),
            "high": sum(r.high_count for r in results),
            "medium": sum(r.medium_count for r in results),
            "low": sum(r.low_count for r in results),
            "clean_files": sum(1 for r in results if r.is_clean),
            "overall_status": "FAIL" if any(
                r.critical_count + r.high_count > 0 for r in results
            ) else "PASS"
        },
        "files": []
    }

    for result in results:
        file_report = {
            "path": result.file_path,
            "lines_scanned": result.lines_scanned,
            "modules": result.modules_found,
            "status": result.status,
            "findings": [f.to_dict() for f in result.findings]
        }
        report["files"].append(file_report)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"  📄 JSON report saved to: {output_path}")
    return report


def generate_html_report(results: list[ScanResult], output_path: str):
    """Generate an HTML report for the dashboard."""
    total_findings = sum(len(r.findings) for r in results)
    total_critical = sum(r.critical_count for r in results)
    total_high = sum(r.high_count for r in results)
    total_medium = sum(r.medium_count for r in results)
    total_low = sum(r.low_count for r in results)

    overall_status = "FAIL" if (total_critical + total_high) > 0 else ("WARNING" if total_medium > 0 else "PASS")
    status_class = {"PASS": "status-pass", "WARNING": "status-warning", "FAIL": "status-fail"}[overall_status]
    status_emoji = {"PASS": "✅", "WARNING": "⚠️", "FAIL": "❌"}[overall_status]

    findings_html = ""
    for result in results:
        if result.is_clean:
            findings_html += f"""
            <div class="file-card clean">
                <div class="file-header">
                    <span class="file-status pass">✅ CLEAN</span>
                    <span class="file-name">{result.file_path}</span>
                    <span class="file-meta">{result.lines_scanned} lines | Modules: {', '.join(result.modules_found)}</span>
                </div>
            </div>"""
        else:
            findings_list = ""
            for finding in result.findings:
                sev_color = SEVERITY_COLOR.get(finding.severity, "#6b7280")
                findings_list += f"""
                <div class="finding">
                    <div class="finding-header">
                        <span class="severity-badge" style="background:{sev_color}">{finding.severity.value.upper()}</span>
                        <span class="rule-id">{finding.rule_id}</span>
                        <span class="rule-name">{finding.rule_name}</span>
                    </div>
                    <div class="finding-location">Line {finding.line_number}: <code>{finding.line_content}</code></div>
                    <div class="finding-desc">{finding.description}</div>
                    <div class="finding-rec">💡 {finding.recommendation}</div>
                </div>"""

            findings_html += f"""
            <div class="file-card has-findings">
                <div class="file-header">
                    <span class="file-status fail">{'❌' if result.critical_count + result.high_count > 0 else '⚠️'} {result.status}</span>
                    <span class="file-name">{result.file_path}</span>
                    <span class="file-meta">{result.lines_scanned} lines | {len(result.findings)} findings</span>
                </div>
                <div class="findings-list">{findings_list}
                </div>
            </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VeriFlow Security Report</title>
    <style>
        :root {{
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #21262d;
            --text-primary: #f0f6fc;
            --text-secondary: #8b949e;
            --border: #30363d;
            --accent: #58a6ff;
            --success: #3fb950;
            --warning: #d29922;
            --danger: #f85149;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        .header {{
            text-align: center;
            padding: 2rem;
            margin-bottom: 2rem;
            background: linear-gradient(135deg, var(--bg-secondary), var(--bg-tertiary));
            border-radius: 12px;
            border: 1px solid var(--border);
        }}
        .header h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
        .header .subtitle {{ color: var(--text-secondary); }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .stat-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
        }}
        .stat-value {{ font-size: 2rem; font-weight: bold; }}
        .stat-label {{ color: var(--text-secondary); font-size: 0.875rem; }}
        .status-pass .stat-value {{ color: var(--success); }}
        .status-warning .stat-value {{ color: var(--warning); }}
        .status-fail .stat-value {{ color: var(--danger); }}
        .file-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            margin-bottom: 1rem;
            overflow: hidden;
        }}
        .file-header {{
            padding: 1rem 1.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }}
        .file-status {{
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        .file-status.pass {{ background: rgba(63,185,80,0.15); color: var(--success); }}
        .file-status.fail {{ background: rgba(248,81,73,0.15); color: var(--danger); }}
        .file-name {{ font-weight: 600; font-family: monospace; }}
        .file-meta {{ color: var(--text-secondary); font-size: 0.85rem; margin-left: auto; }}
        .findings-list {{ padding: 0 1.5rem 1.5rem; }}
        .finding {{
            padding: 1rem;
            margin-top: 0.75rem;
            background: var(--bg-tertiary);
            border-radius: 6px;
            border-left: 3px solid var(--border);
        }}
        .finding-header {{ display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }}
        .severity-badge {{
            color: white;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .rule-id {{ font-family: monospace; color: var(--accent); }}
        .rule-name {{ font-weight: 600; }}
        .finding-location {{
            font-family: monospace;
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }}
        .finding-location code {{
            background: var(--bg-primary);
            padding: 0.15rem 0.4rem;
            border-radius: 3px;
        }}
        .finding-desc {{ margin-bottom: 0.5rem; }}
        .finding-rec {{ color: var(--text-secondary); font-size: 0.9rem; }}
        .timestamp {{ text-align: center; color: var(--text-secondary); margin-top: 2rem; font-size: 0.85rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ VeriFlow Security Report</h1>
            <p class="subtitle">Automated Hardware Security Analysis</p>
        </div>

        <div class="stats">
            <div class="stat-card {status_class}">
                <div class="stat-value">{status_emoji} {overall_status}</div>
                <div class="stat-label">Overall Status</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(results)}</div>
                <div class="stat-label">Files Scanned</div>
            </div>
            <div class="stat-card status-fail">
                <div class="stat-value">{total_critical}</div>
                <div class="stat-label">Critical</div>
            </div>
            <div class="stat-card status-warning">
                <div class="stat-value">{total_high}</div>
                <div class="stat-label">High</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_medium}</div>
                <div class="stat-label">Medium</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_low}</div>
                <div class="stat-label">Low</div>
            </div>
        </div>

        {findings_html}

        <div class="timestamp">
            Report generated by VeriFlow v1.0.0 on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>"""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html)

    print(f"  📊 HTML report saved to: {output_path}")


def generate_github_annotations(results: list[ScanResult]):
    """Output findings as GitHub Actions annotations."""
    for result in results:
        for finding in result.findings:
            level = "error" if finding.severity in [Severity.CRITICAL, Severity.HIGH] else "warning"
            msg = f"{finding.rule_id}: {finding.rule_name} — {finding.description}"
            print(f"::{level} file={finding.file_path},line={finding.line_number}::{msg}")
