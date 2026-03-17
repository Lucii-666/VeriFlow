# VeriFlow — Copilot Custom Instructions

## Project Context
VeriFlow is a CI/CD pipeline for hardware (Verilog/SystemVerilog) design verification and security scanning. This repository contains RTL designs, testbenches, and an automated security scanner.

## When generating Verilog code:
- Use **synchronous reset** (`negedge rst_n`) by default
- Always use **non-blocking assignments** (`<=`) in sequential blocks
- Always use **blocking assignments** (`=`) in combinational blocks
- Include **`timescale** directives in testbenches
- Add **VCD dump** (`$dumpfile`/`$dumpvars`) in every testbench
- Use **parameterized widths** (`parameter WIDTH = 8`) for reusability
- Follow the naming convention: `tb_<module_name>.v` for testbenches

## When generating testbenches:
Include this boilerplate structure:
1. Signal declarations matching the DUT ports
2. DUT instantiation with named port connections
3. Clock generation: `initial clk = 0; always #5 clk = ~clk;`
4. Reset sequence: Assert reset for 3 clock cycles
5. Test stimulus with pass/fail tracking:
   - Integer `pass_count` and `fail_count` counters
   - A `task` for applying stimulus and checking results
6. Test summary displaying pass/fail counts
7. Timeout watchdog: `initial begin #100000; $finish(1); end`
8. VCD waveform dump

## When modifying the security scanner:
- Detection rules follow the ID scheme: `HT-XXX` for hardware trojans, `LINT-XXX` for lint
- Severity levels: CRITICAL, HIGH, MEDIUM, LOW, INFO
- Each finding must include: rule_id, rule_name, severity, line number, description, recommendation
- The scanner uses regex-based pattern matching (no synthesis required)

## Repository structure:
- `designs/` — Clean, verified RTL designs
- `trojan_samples/` — Intentionally trojaned designs (for demo)
- `scanner/` — Python-based security scanner
- `scripts/` — Automation scripts
- `docs/dashboard/` — Web-based results dashboard
- `.github/workflows/` — CI/CD pipeline
