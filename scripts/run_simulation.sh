#!/bin/bash
# =============================================================================
# VeriFlow - Simulation Runner Script
# =============================================================================
# Usage: ./scripts/run_simulation.sh <design.v> <testbench.v>
#    or: ./scripts/run_simulation.sh all
# =============================================================================

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${BLUE}  ⚡ VeriFlow Simulation Runner${NC}"
echo "  ──────────────────────────────────────"
echo ""

# Check for iverilog
if ! command -v iverilog &> /dev/null; then
    echo -e "${RED}  ❌ Error: Icarus Verilog (iverilog) not found${NC}"
    echo "  Install with: sudo apt-get install iverilog"
    exit 1
fi

run_single_sim() {
    local DESIGN=$1
    local TESTBENCH=$2
    local NAME=$(basename $(dirname "$DESIGN"))
    local OUTPUT="/tmp/veriflow_${NAME}.vvp"

    echo -e "  ${BLUE}━━━ Simulating: ${NAME} ━━━${NC}"
    echo "  Design:    $DESIGN"
    echo "  Testbench: $TESTBENCH"
    echo ""

    # Compile
    if iverilog -o "$OUTPUT" "$TESTBENCH" "$DESIGN" 2>&1; then
        echo -e "  ${GREEN}✅ Compilation successful${NC}"
    else
        echo -e "  ${RED}❌ Compilation failed${NC}"
        return 1
    fi

    # Simulate
    echo ""
    vvp "$OUTPUT"

    # Cleanup
    rm -f "$OUTPUT"
    echo ""
}

if [ "$1" == "all" ]; then
    PASS=0
    FAIL=0

    for design_dir in designs/*/; do
        DESIGN=$(find "$design_dir" -name "*.v" ! -name "tb_*" | head -1)
        TB=$(find "$design_dir" -name "tb_*.v" | head -1)

        if [ -n "$DESIGN" ] && [ -n "$TB" ]; then
            if run_single_sim "$DESIGN" "$TB"; then
                PASS=$((PASS + 1))
            else
                FAIL=$((FAIL + 1))
            fi
        fi
    done

    echo "  ══════════════════════════════════════"
    echo "  Passed: $PASS | Failed: $FAIL"
    echo "  ══════════════════════════════════════"

    [ $FAIL -gt 0 ] && exit 1
elif [ $# -eq 2 ]; then
    run_single_sim "$1" "$2"
else
    echo "  Usage:"
    echo "    $0 <design.v> <testbench.v>"
    echo "    $0 all"
    exit 1
fi
