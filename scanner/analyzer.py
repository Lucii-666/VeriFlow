#!/usr/bin/env python3
"""
VeriFlow Security Scanner - Core Analysis Engine
=================================================
Performs static analysis on Verilog/SystemVerilog files to detect potential
hardware trojans and security vulnerabilities.

This scanner uses pattern-based detection with configurable rules to identify:
- Unused trigger logic (potential trojan triggers)
- Suspicious state machines with hidden/unreachable states
- Unauthorized I/O modifications
- Time-bomb patterns (sequential counter-based activation)
- Covert channels (side-channel leakage)
- Rare input triggers (combinational magic-value comparisons)
- Common lint issues
"""

import re
import os
import sys
import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
from pathlib import Path


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Finding:
    """Represents a single security finding."""
    rule_id: str
    rule_name: str
    severity: Severity
    file_path: str
    line_number: int
    line_content: str
    description: str
    recommendation: str

    def to_dict(self):
        d = asdict(self)
        d["severity"] = self.severity.value
        return d


@dataclass
class ScanResult:
    """Aggregated results from scanning a single file."""
    file_path: str
    findings: list = field(default_factory=list)
    lines_scanned: int = 0
    modules_found: list = field(default_factory=list)

    @property
    def critical_count(self):
        return sum(1 for f in self.findings if f.severity == Severity.CRITICAL)

    @property
    def high_count(self):
        return sum(1 for f in self.findings if f.severity == Severity.HIGH)

    @property
    def medium_count(self):
        return sum(1 for f in self.findings if f.severity == Severity.MEDIUM)

    @property
    def low_count(self):
        return sum(1 for f in self.findings if f.severity == Severity.LOW)

    @property
    def is_clean(self):
        return len(self.findings) == 0

    @property
    def status(self):
        if self.critical_count > 0 or self.high_count > 0:
            return "FAIL"
        elif self.medium_count > 0:
            return "WARNING"
        else:
            return "PASS"


class VerilogAnalyzer:
    """
    Core static analysis engine for Verilog files.

    Parses Verilog source files and applies detection rules to identify
    potential hardware trojans and security vulnerabilities.
    """

    # ── Magic Number Patterns ──────────────────────────────────────────────
    MAGIC_CONSTANTS = [
        (r"32'h[Dd][Ee][Aa][Dd]_?[Bb][Ee][Ee][Ff]", "DEAD_BEEF"),
        (r"32'h[Cc][Aa][Ff][Ee]_?[Bb][Aa][Bb][Ee]", "CAFE_BABE"),
        (r"32'h[Bb][Aa][Aa][Dd]_?[Ff][Oo][Oo][Dd]", "BAAD_FOOD"),
        (r"32'h[Dd][Ee][Aa][Dd]_?[Cc][Oo][Dd][Ee]", "DEAD_CODE"),
        (r"32'h[Ff]{8}", "FFFFFFFF"),
        (r"16'h[Dd][Ee][Aa][Dd]", "DEAD"),
        (r"8'h[Bb][Aa]", "BA (trigger pattern)"),
        (r"8'h[Dd][Ee]", "DE (trigger pattern)"),
        (r"8'h[Aa][Dd]", "AD (trigger pattern)"),
    ]

    # ── Rare Condition Patterns ────────────────────────────────────────────
    RARE_CONDITION_PATTERNS = [
        r"==\s*\d+'h[A-Fa-f0-9]+\s*\)\s*&&",    # Chained comparisons with hex constants
        r"&&.*==.*&&.*==",                         # Triple AND comparison
    ]

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: list[ScanResult] = []

    def scan_file(self, file_path: str) -> ScanResult:
        """Scan a single Verilog file for security vulnerabilities."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, "r") as f:
            lines = f.readlines()

        content = "".join(lines)
        result = ScanResult(
            file_path=str(path),
            lines_scanned=len(lines)
        )

        # Extract module names
        result.modules_found = re.findall(r"module\s+(\w+)", content)

        # Run all detection rules
        self._check_unused_trigger_logic(lines, result)
        self._check_suspicious_state_machines(lines, content, result)
        self._check_unauthorized_io(lines, content, result)
        self._check_timebomb_patterns(lines, content, result)
        self._check_rare_input_triggers(lines, content, result)
        self._check_covert_channels(lines, content, result)
        self._check_magic_constants(lines, content, result)
        self._check_lint_issues(lines, content, result)

        self.results.append(result)
        return result

    def scan_directory(self, dir_path: str) -> list[ScanResult]:
        """Recursively scan all Verilog files in a directory."""
        results = []
        path = Path(dir_path)

        for ext in ["*.v", "*.sv", "*.vh"]:
            for verilog_file in path.rglob(ext):
                if self.verbose:
                    print(f"  Scanning: {verilog_file}")
                try:
                    result = self.scan_file(str(verilog_file))
                    results.append(result)
                except Exception as e:
                    print(f"  ⚠️  Error scanning {verilog_file}: {e}")

        return results

    # ══════════════════════════════════════════════════════════════════════
    # Detection Rules
    # ══════════════════════════════════════════════════════════════════════

    def _check_unused_trigger_logic(self, lines: list, result: ScanResult):
        """
        HT-001: Detect signals that are incremented/modified based on
        specific conditions but never used in primary outputs.
        """
        # Find all signal declarations
        declared_regs = {}
        for i, line in enumerate(lines):
            match = re.search(r"reg\s+(?:\[\d+:\d+\]\s+)?(\w+)", line)
            if match:
                sig_name = match.group(1)
                declared_regs[sig_name] = i + 1

        # Find signals that are conditionally incremented
        for i, line in enumerate(lines):
            match = re.search(r"(\w+)\s*<=\s*\1\s*\+\s*1", line)
            if match:
                sig_name = match.group(1)
                # Check if this signal drives any output
                content = "".join(lines)
                # Count usage (exclude declaration and increment)
                usage_count = len(re.findall(rf"\b{sig_name}\b", content))
                if usage_count <= 4:  # Declared, incremented, but barely used
                    result.findings.append(Finding(
                        rule_id="HT-001",
                        rule_name="Unused Trigger Logic",
                        severity=Severity.CRITICAL,
                        file_path=result.file_path,
                        line_number=i + 1,
                        line_content=line.strip(),
                        description=(
                            f"Signal '{sig_name}' is conditionally incremented but has "
                            f"minimal usage ({usage_count} refs). This pattern is consistent "
                            f"with a hidden trigger counter used in hardware trojans."
                        ),
                        recommendation=(
                            f"Verify that '{sig_name}' serves a legitimate design purpose. "
                            f"If unused, remove it to reduce attack surface."
                        )
                    ))

    def _check_suspicious_state_machines(self, lines: list, content: str, result: ScanResult):
        """
        HT-002: Detect state machines with suspicious patterns like
        unreachable states or hidden transitions.
        """
        # Find state machine patterns (localparam with sequential values)
        state_defs = re.findall(r"localparam\s+(\w+)\s*=\s*\d+'d(\d+)", content)
        if len(state_defs) >= 3:
            state_names = [s[0] for s in state_defs]
            # Check for "dead" or suspicious state names
            suspicious_names = ["dead", "hidden", "secret", "trojan", "armed", "kill"]
            for name in state_names:
                for sus in suspicious_names:
                    if sus.upper() in name.upper():
                        line_num = 0
                        for i, line in enumerate(lines):
                            if name in line and "localparam" in line:
                                line_num = i + 1
                                break
                        result.findings.append(Finding(
                            rule_id="HT-002",
                            rule_name="Suspicious State Machine",
                            severity=Severity.HIGH,
                            file_path=result.file_path,
                            line_number=line_num,
                            line_content=lines[line_num - 1].strip() if line_num > 0 else "",
                            description=(
                                f"State machine contains suspiciously named state '{name}' "
                                f"(matched keyword: '{sus}'). Hidden or unreachable states "
                                f"are a common trojan insertion technique."
                            ),
                            recommendation=(
                                f"Review the state machine for unreachable states and verify "
                                f"all transitions are intentional and documented."
                            )
                        ))

        # Check for armed/active flags
        for i, line in enumerate(lines):
            if re.search(r"reg\s+.*\b(armed|trojan_active|kill_switch|exfil_mode)\b", line):
                result.findings.append(Finding(
                    rule_id="HT-002",
                    rule_name="Suspicious State Machine",
                    severity=Severity.HIGH,
                    file_path=result.file_path,
                    line_number=i + 1,
                    line_content=line.strip(),
                    description=(
                        f"Register with suspicious name detected. Flags named 'armed', "
                        f"'trojan_active', 'kill_switch', or 'exfil_mode' suggest "
                        f"trojan activation logic."
                    ),
                    recommendation="Review the purpose of this control flag and its drivers."
                ))

    def _check_unauthorized_io(self, lines: list, content: str, result: ScanResult):
        """
        HT-003: Detect cases where outputs are modified under unexpected
        conditions, especially conditional on internal state.
        """
        # Find output declarations
        outputs = re.findall(r"output\s+(?:reg|wire)?\s*(?:\[\d+:\d+\]\s+)?(\w+)", content)

        for i, line in enumerate(lines):
            for out_name in outputs:
                # Check if output is assigned inside a conditional that references
                # suspicious signals
                if re.search(rf"\b{out_name}\b\s*<=", line):
                    # Look at surrounding context (previous 5 lines for conditionals)
                    context_start = max(0, i - 5)
                    context = "".join(lines[context_start:i + 1])
                    suspicious_conds = ["trojan", "armed", "exfil", "trigger",
                                        "corrupt", "kill", "backdoor"]
                    for cond in suspicious_conds:
                        if cond in context.lower() and cond not in line.lower().split("//")[0]:
                            # Check it's in an if-condition, not just a comment
                            if re.search(rf"if\s*\(.*{cond}", context, re.IGNORECASE):
                                result.findings.append(Finding(
                                    rule_id="HT-003",
                                    rule_name="Unauthorized I/O Access",
                                    severity=Severity.CRITICAL,
                                    file_path=result.file_path,
                                    line_number=i + 1,
                                    line_content=line.strip(),
                                    description=(
                                        f"Output '{out_name}' is conditionally modified based "
                                        f"on suspicious signal (matched: '{cond}'). This could "
                                        f"indicate unauthorized manipulation of design outputs."
                                    ),
                                    recommendation=(
                                        f"Verify that all paths modifying '{out_name}' are "
                                        f"part of the intended specification."
                                    )
                                ))

    def _check_timebomb_patterns(self, lines: list, content: str, result: ScanResult):
        """
        HT-004: Detect SEQUENTIAL counter-based activation (time bombs).
        Only triggers when a counter is compared against large constants
        inside a clocked always block (posedge/negedge).
        """
        # Find all clocked (sequential) always blocks
        seq_blocks = list(re.finditer(
            r'always\s*@\s*\(\s*(?:pos|neg)edge', content, re.IGNORECASE
        ))

        for i, line in enumerate(lines):
            # Pattern: counter == large_hex_constant
            match = re.search(r"(\w+)\s*==\s*(\d+)'h([A-Fa-f0-9_]+)", line)
            if match:
                sig_name = match.group(1)
                bit_width = int(match.group(2))
                hex_val = match.group(3)

                # Only flag as time-bomb for large (16+ bit) constants
                if bit_width >= 16:
                    # Verify this line is inside a sequential block
                    line_offset = sum(len(l) for l in lines[:i])
                    in_sequential = False
                    for block in seq_blocks:
                        if block.start() < line_offset:
                            in_sequential = True  # Approximate: line comes after a sequential block start

                    if in_sequential:
                        result.findings.append(Finding(
                            rule_id="HT-004",
                            rule_name="Time-bomb Pattern",
                            severity=Severity.HIGH,
                            file_path=result.file_path,
                            line_number=i + 1,
                            line_content=line.strip(),
                            description=(
                                f"Signal '{sig_name}' compared against {bit_width}-bit "
                                f"constant 0x{hex_val} inside a sequential (clocked) block. "
                                f"Large counter comparisons in clocked logic are a classic "
                                f"hardware trojan time-bomb activation pattern."
                            ),
                            recommendation=(
                                f"Verify that the comparison value 0x{hex_val} has a "
                                f"legitimate design purpose. Document the expected "
                                f"activation count if intentional."
                            )
                        ))
                    else:
                        # Combinational large constant → route to HT-006
                        result.findings.append(Finding(
                            rule_id="HT-006",
                            rule_name="Rare Input Trigger",
                            severity=Severity.HIGH,
                            file_path=result.file_path,
                            line_number=i + 1,
                            line_content=line.strip(),
                            description=(
                                f"Combinational comparison of '{sig_name}' against "
                                f"{bit_width}-bit constant 0x{hex_val}. Input-value "
                                f"comparisons with specific constants can be used as "
                                f"rare-event triggers for hardware trojans."
                            ),
                            recommendation=(
                                f"Verify that this comparison is in the design "
                                f"specification. Document why this specific value "
                                f"is compared."
                            )
                        ))

    def _check_covert_channels(self, lines: list, content: str, result: ScanResult):
        """
        HT-005: Detect potential covert/side channels where internal
        signals are leaked through outputs.
        """
        # XOR-reduction leaking data
        for i, line in enumerate(lines):
            if re.search(r"\^(\w+)", line):
                # Check if XOR reduction is assigned to output
                if "assign" in line and "serial_out" in line:
                    result.findings.append(Finding(
                        rule_id="HT-005",
                        rule_name="Covert Channel",
                        severity=Severity.MEDIUM,
                        file_path=result.file_path,
                        line_number=i + 1,
                        line_content=line.strip(),
                        description=(
                            f"XOR-reduction of internal register routed to output. "
                            f"This is a known technique for creating covert side-channels "
                            f"that leak internal state one bit at a time."
                        ),
                        recommendation=(
                            f"Verify that the XOR-reduction serves a legitimate "
                            f"function (e.g., parity). Review the output path."
                        )
                    ))

            # Check for conditional output muxing (normal vs exfiltration)
            if re.search(r"assign\s+\w+\s*=\s*\w+\s*\?", line):
                if any(sus in line.lower() for sus in ["exfil", "trojan", "secret", "leak"]):
                    result.findings.append(Finding(
                        rule_id="HT-005",
                        rule_name="Covert Channel",
                        severity=Severity.CRITICAL,
                        file_path=result.file_path,
                        line_number=i + 1,
                        line_content=line.strip(),
                        description=(
                            f"Output multiplexer with suspicious mode selector. "
                            f"Conditional output switching between normal and 'exfiltration' "
                            f"paths is a hallmark of covert channel trojans."
                        ),
                        recommendation=(
                            f"Remove the conditional output path and verify the "
                            f"signal drives only intended functionality."
                        )
                    ))

            # Bit-indexing with counter (operand_a[trigger_cnt[2:0]])
            if re.search(r"\w+\[\w+\[\d+:\d+\]\]", line):
                result.findings.append(Finding(
                    rule_id="HT-005",
                    rule_name="Covert Channel",
                    severity=Severity.MEDIUM,
                    file_path=result.file_path,
                    line_number=i + 1,
                    line_content=line.strip(),
                    description=(
                        f"Dynamic bit-indexing using counter-derived index. "
                        f"This pattern can be used to extract internal data "
                        f"bit-by-bit through a side channel."
                    ),
                    recommendation=(
                        f"Review whether dynamic bit selection is functionally "
                        f"required. Consider if this could leak sensitive data."
                    )
                ))

    def _check_rare_input_triggers(self, lines: list, content: str, result: ScanResult):
        """
        HT-006: Detect RARE INPUT triggers (combinational activation).
        Looks for multi-condition input comparisons with specific magic values
        in continuous assignments or combinational blocks.
        """
        # Determine combinational contexts by exclusion of clocked always blocks
        seq_blocks = list(re.finditer(
            r'always\s*@\s*\(\s*(?:pos|neg)edge', content, re.IGNORECASE
        ))

        for i, line in enumerate(lines):
            # Known rare condition patterns (e.g., A == 8'hFF && B == 8'h00)
            for pattern in self.RARE_CONDITION_PATTERNS:
                if re.search(pattern, line):
                    # Check if sequential or combinational
                    line_offset = sum(len(l) for l in lines[:i])
                    in_sequential = False
                    for block in seq_blocks:
                        if block.start() < line_offset:
                            in_sequential = True

                    is_assign = line.strip().startswith('assign')
                    is_combinational = is_assign or not in_sequential

                    if is_combinational:
                        result.findings.append(Finding(
                            rule_id="HT-006",
                            rule_name="Rare Input Trigger",
                            severity=Severity.HIGH,
                            file_path=result.file_path,
                            line_number=i + 1,
                            line_content=line.strip(),
                            description=(
                                f"Detected multiple specific value exact comparisons "
                                f"chained together in combinational logic. This "
                                f"pattern is highly indicative of a hardware trojan "
                                f"rare-event trigger waiting for a specific input state."
                            ),
                            recommendation=(
                                f"Verify that this rare condition is part of the "
                                f"intended functionality and not a malicious trigger."
                            )
                        ))

    def _check_magic_constants(self, lines: list, content: str, result: ScanResult):
        """
        Context-aware magic constant detection.
        Classifies as HT-004 (Time-bomb) in sequential context,
        or HT-006 (Rare Input Trigger) in combinational context.
        """
        # Determine if each line is in a sequential or combinational context
        seq_blocks = list(re.finditer(
            r'always\s*@\s*\(\s*(?:pos|neg)edge', content, re.IGNORECASE
        ))

        for i, line in enumerate(lines):
            for pattern, name in self.MAGIC_CONSTANTS:
                if re.search(pattern, line):
                    # Determine context
                    line_offset = sum(len(l) for l in lines[:i])
                    in_sequential = False
                    for block in seq_blocks:
                        if block.start() < line_offset:
                            in_sequential = True

                    is_assign = line.strip().startswith('assign')
                    is_combinational = is_assign or not in_sequential

                    if is_combinational:
                        result.findings.append(Finding(
                            rule_id="HT-006",
                            rule_name="Rare Input Trigger",
                            severity=Severity.HIGH,
                            file_path=result.file_path,
                            line_number=i + 1,
                            line_content=line.strip(),
                            description=(
                                f"Known magic constant '{name}' in combinational "
                                f"logic. Specific input values used as immediate "
                                f"activation triggers for hardware trojans."
                            ),
                            recommendation=(
                                f"Replace magic constants with named parameters "
                                f"and document their purpose."
                            )
                        ))
                    else:
                        result.findings.append(Finding(
                            rule_id="HT-004",
                            rule_name="Time-bomb Pattern",
                            severity=Severity.HIGH,
                            file_path=result.file_path,
                            line_number=i + 1,
                            line_content=line.strip(),
                            description=(
                                f"Known magic constant '{name}' in sequential "
                                f"logic. These values are commonly used as "
                                f"trojan activation triggers in clocked counters."
                            ),
                            recommendation=(
                                f"Replace magic constants with named parameters "
                                f"and document their purpose."
                            )
                        ))

    def _check_lint_issues(self, lines: list, content: str, result: ScanResult):
        """
        LINT rules: Detect common coding issues that may indicate
        poor design practices or potential vulnerabilities.
        """
        # LINT-001: Undriven signals (declared but never assigned)
        declared = set(re.findall(r"reg\s+(?:\[\d+:\d+\]\s+)?(\w+)", content))
        assigned = set(re.findall(r"(\w+)\s*<=", content))
        assigned.update(re.findall(r"assign\s+(\w+)", content))
        assigned.update(re.findall(r"\b(\w+)\s*=\s*[^=]", content)) # Blocking assignments

        for sig in declared - assigned:
            for i, line in enumerate(lines):
                if re.search(rf"reg\s+.*\b{sig}\b", line):
                    result.findings.append(Finding(
                        rule_id="LINT-001",
                        rule_name="Undriven Signal",
                        severity=Severity.MEDIUM,
                        file_path=result.file_path,
                        line_number=i + 1,
                        line_content=line.strip(),
                        description=f"Signal '{sig}' is declared but never assigned.",
                        recommendation=f"Remove unused signal '{sig}' or add a driver."
                    ))
                    break

        # LINT-003: Incomplete case statements (potential latch inference)
        case_blocks = re.finditer(r"case\s*\((.*?)\)(.*?)endcase", content, re.DOTALL)
        for case_match in case_blocks:
            case_body = case_match.group(2)
            if "default" not in case_body:
                # Find the line number
                case_start = case_match.start()
                line_num = content[:case_start].count("\n") + 1
                result.findings.append(Finding(
                    rule_id="LINT-003",
                    rule_name="Latch Inference",
                    severity=Severity.MEDIUM,
                    file_path=result.file_path,
                    line_number=line_num,
                    line_content=lines[line_num - 1].strip() if line_num <= len(lines) else "",
                    description=(
                        "Case statement without 'default' clause may infer "
                        "unintended latches in synthesis."
                    ),
                    recommendation="Add a 'default' clause to the case statement."
                ))
