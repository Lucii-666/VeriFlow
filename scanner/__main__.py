#!/usr/bin/env python3
"""
VeriFlow Security Scanner - CLI Entry Point
============================================
Usage:
    python -m scanner [OPTIONS] <path>

Options:
    --format    Output format: terminal, json, html, github (default: terminal)
    --output    Output file path for json/html reports
    --verbose   Enable verbose output
    --fail-on   Minimum severity to cause non-zero exit: critical, high, medium, low
"""

import sys
import os
import argparse
from pathlib import Path

# Add parent dir to path for module imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scanner.analyzer import VerilogAnalyzer, Severity
from scanner.reporter import (
    print_terminal_report,
    generate_json_report,
    generate_html_report,
    generate_github_annotations,
)


def main():
    parser = argparse.ArgumentParser(
        prog="veriflow-scanner",
        description="⚡ VeriFlow Hardware Security Scanner — "
                    "Detect hardware trojans in Verilog designs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m scanner designs/                  # Scan all designs
  python -m scanner trojan_samples/ --format json --output report.json
  python -m scanner designs/alu/alu.v         # Scan single file
  python -m scanner . --format github         # GitHub Actions annotations
        """
    )

    parser.add_argument(
        "path",
        help="Path to a Verilog file or directory to scan"
    )
    parser.add_argument(
        "--format",
        choices=["terminal", "json", "html", "github", "all"],
        default="terminal",
        help="Output format (default: terminal)"
    )
    parser.add_argument(
        "--output",
        default="reports/security_report",
        help="Output file path (without extension) for json/html reports"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--fail-on",
        choices=["critical", "high", "medium", "low"],
        default="high",
        help="Minimum severity to cause non-zero exit code (default: high)"
    )

    args = parser.parse_args()

    # ── Banner ─────────────────────────────────────────────────────────
    print()
    print("  ⚡ VeriFlow Hardware Security Scanner v1.0.0")
    print("  ─" * 25)
    print()

    # ── Scan ───────────────────────────────────────────────────────────
    analyzer = VerilogAnalyzer(verbose=args.verbose)
    scan_path = Path(args.path)

    if scan_path.is_file():
        print(f"  📂 Scanning file: {scan_path}")
        results = [analyzer.scan_file(str(scan_path))]
    elif scan_path.is_dir():
        print(f"  📂 Scanning directory: {scan_path}")
        results = analyzer.scan_directory(str(scan_path))
    else:
        print(f"  ❌ Error: Path not found: {scan_path}")
        sys.exit(1)

    if not results:
        print("  ⚠️  No Verilog files found to scan.")
        sys.exit(0)

    print(f"  📄 Found {len(results)} file(s)")
    print()

    # ── Report ─────────────────────────────────────────────────────────
    if args.format in ("terminal", "all"):
        passed = print_terminal_report(results)

    if args.format in ("json", "all"):
        generate_json_report(results, f"{args.output}.json")

    if args.format in ("html", "all"):
        generate_html_report(results, f"{args.output}.html")

    if args.format in ("github", "all"):
        generate_github_annotations(results)

    # ── Exit Code ──────────────────────────────────────────────────────
    fail_severities = {
        "critical": [Severity.CRITICAL],
        "high": [Severity.CRITICAL, Severity.HIGH],
        "medium": [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM],
        "low": [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW],
    }

    target_severities = fail_severities[args.fail_on]
    has_failures = any(
        any(f.severity in target_severities for f in r.findings)
        for r in results
    )

    if has_failures:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
