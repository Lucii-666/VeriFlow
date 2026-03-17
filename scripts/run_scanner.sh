#!/bin/bash
# =============================================================================
# VeriFlow - Security Scanner Runner Script
# =============================================================================
# Usage: ./scripts/run_scanner.sh [path] [format]
# =============================================================================

set -e

PATH_TO_SCAN=${1:-.}
FORMAT=${2:-terminal}

echo ""
echo "  ⚡ VeriFlow Security Scanner"
echo "  ──────────────────────────────────────"
echo ""
echo "  Target: $PATH_TO_SCAN"
echo "  Format: $FORMAT"
echo ""

python -m scanner "$PATH_TO_SCAN" --format "$FORMAT" --output reports/security_report
