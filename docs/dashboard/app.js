// ═══════════════════════════════════════════════════════════════════
// VeriFlow Dashboard — Interactive JavaScript
// ═══════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    initTerminalAnimation();
    initStatsAnimation();
    initTabs();
    loadReportData();
    initNavHighlight();
    updateGlobalStatus();
    initLiveScanner();
});

// ── Terminal Typing Animation ──────────────────────────────────────
function initTerminalAnimation() {
    const output = document.getElementById('terminalOutput');
    if (!output) return;

    const lines = [
        { text: '$ python -m scanner trojan_samples/', color: '#3fb950', delay: 50 },
        { text: '', delay: 200 },
        { text: '  ⚡ VeriFlow Hardware Security Scanner v1.0.0', color: '#58a6ff', delay: 30 },
        { text: '  ──────────────────────────────────────────────', color: '#484f58', delay: 10 },
        { text: '', delay: 100 },
        { text: '  📂 Scanning directory: trojan_samples/', color: '#8b949e', delay: 40 },
        { text: '  📄 Found 3 file(s)', color: '#8b949e', delay: 40 },
        { text: '', delay: 200 },
        { text: '╔══════════════════════════════════════════════════════════╗', color: '#58a6ff', delay: 15 },
        { text: '║            VeriFlow Security Report                     ║', color: '#58a6ff', delay: 15 },
        { text: '╠══════════════════════════════════════════════════════════╣', color: '#58a6ff', delay: 15 },
        { text: '║  ⚠️  7 finding(s) detected                              ║', color: '#d29922', delay: 40 },
        { text: '║  🔴 Critical: 3  🟠 High: 3  🟡 Medium: 1              ║', color: '#d29922', delay: 40 },
        { text: '╚══════════════════════════════════════════════════════════╝', color: '#58a6ff', delay: 15 },
        { text: '', delay: 100 },
        { text: '  ❌ trojan_samples/alu_trojan.v', color: '#f85149', delay: 50 },
        { text: '     Modules: alu_trojan', color: '#8b949e', delay: 30 },
        { text: '', delay: 50 },
        { text: '     🔴 [CRITICAL] HT-001: Unused Trigger Logic', color: '#f85149', delay: 60 },
        { text: '        Line 55: trigger_cnt <= trigger_cnt + 1', color: '#484f58', delay: 30 },
        { text: '        → Signal has minimal usage (3 refs)', color: '#8b949e', delay: 30 },
        { text: '', delay: 50 },
        { text: '     🟠 [HIGH] HT-004: Time-bomb Pattern', color: '#d29922', delay: 60 },
        { text: '        Line 59: trigger_cnt == 32\'hDEAD_BEEF', color: '#484f58', delay: 30 },
        { text: '        → Magic constant activation trigger', color: '#8b949e', delay: 30 },
        { text: '', delay: 50 },
        { text: '     🟡 [MEDIUM] HT-005: Covert Channel', color: '#ca8a04', delay: 60 },
        { text: '        Line 88: carry_out <= operand_a[trigger_cnt[2:0]]', color: '#484f58', delay: 30 },
        { text: '        → Dynamic bit-indexing (side channel)', color: '#8b949e', delay: 30 },
        { text: '', delay: 200 },
        { text: '═══════════════════════════════════════════════════════════', color: '#f85149', delay: 10 },
        { text: '  OVERALL STATUS: ❌ FAIL — Critical vulnerabilities found', color: '#f85149', delay: 60 },
        { text: '═══════════════════════════════════════════════════════════', color: '#f85149', delay: 10 },
    ];

    let lineIndex = 0;
    let charIndex = 0;
    let currentLineEl = null;

    function typeNextChar() {
        if (lineIndex >= lines.length) return;

        const line = lines[lineIndex];

        if (charIndex === 0) {
            currentLineEl = document.createElement('span');
            currentLineEl.style.color = line.color || '#8b949e';
            output.appendChild(currentLineEl);
        }

        if (charIndex < line.text.length) {
            currentLineEl.textContent += line.text[charIndex];
            charIndex++;
            setTimeout(typeNextChar, line.delay || 30);
        } else {
            output.appendChild(document.createTextNode('\n'));
            lineIndex++;
            charIndex = 0;

            // Scroll to bottom
            const body = document.getElementById('terminalBody');
            if (body) body.scrollTop = body.scrollHeight;

            setTimeout(typeNextChar, line.delay || 50);
        }
    }

    // Start after a small delay
    setTimeout(typeNextChar, 800);
}

// ── Stats Counter Animation ────────────────────────────────────────
function initStatsAnimation() {
    const cards = document.querySelectorAll('.stat-card[data-animate]');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    cards.forEach(card => observer.observe(card));
}

function animateCounter(card) {
    const valueEl = card.querySelector('.stat-value');
    if (!valueEl) return;

    const target = parseInt(valueEl.textContent) || 0;
    let current = 0;
    const duration = 1500;
    const start = performance.now();

    function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
        current = Math.round(eased * target);
        valueEl.textContent = current;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

// ── Tab Switching ──────────────────────────────────────────────────
function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const target = tab.dataset.tab;
            document.getElementById('cleanPanel').classList.toggle('hidden', target !== 'clean');
            document.getElementById('trojanPanel').classList.toggle('hidden', target !== 'trojan');
        });
    });
}

// ── Load Report Data ───────────────────────────────────────────────
async function loadReportData() {
    // Try to load real data from JSON reports
    try {
        const cleanResp = await fetch('data/clean_report.json');
        if (cleanResp.ok) {
            const cleanData = await cleanResp.json();
            renderResults('cleanResults', cleanData);
            updateStats(cleanData, 'clean');
        }
    } catch (e) {
        // Use demo data if no report available
        renderDemoCleanResults();
    }

    try {
        const trojanResp = await fetch('data/trojan_report.json');
        if (trojanResp.ok) {
            const trojanData = await trojanResp.json();
            renderResults('trojanResults', trojanData);
            updateStats(trojanData, 'trojan');
        }
    } catch (e) {
        renderDemoTrojanResults();
    }
}

function renderResults(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container || !data.files) return;

    container.innerHTML = '';

    data.files.forEach(file => {
        const card = document.createElement('div');
        card.className = 'result-card';

        const statusClass = file.status === 'PASS' ? 'pass' : 'fail';
        const findingsHtml = file.findings.map(f => `
            <div class="finding-item ${f.severity}">
                <div class="finding-header">
                    <span class="severity-tag ${f.severity}">${f.severity}</span>
                    <span class="finding-rule">${f.rule_id}</span>
                    <span class="finding-name">${f.rule_name}</span>
                </div>
                <div class="finding-desc">${f.description}</div>
                <div class="finding-line">Line ${f.line_number}: ${escapeHtml(f.line_content)}</div>
            </div>
        `).join('');

        card.innerHTML = `
            <div class="result-header">
                <span class="result-status ${statusClass}">${file.status}</span>
                <span class="result-file">${file.path}</span>
                <span class="result-meta">${file.lines_scanned} lines | ${file.findings.length} findings</span>
            </div>
            ${findingsHtml ? `<div class="result-findings">${findingsHtml}</div>` : ''}
        `;

        container.appendChild(card);
    });
}

function renderDemoCleanResults() {
    const container = document.getElementById('cleanResults');
    if (!container) return;

    const demoFiles = [
        { name: 'designs/alu/alu.v', modules: 'alu', lines: 82 },
        { name: 'designs/counter/counter.v', modules: 'counter', lines: 38 },
        { name: 'designs/shift_register/shift_register.v', modules: 'shift_register', lines: 45 },
    ];

    container.innerHTML = demoFiles.map(f => `
        <div class="result-card">
            <div class="result-header">
                <span class="result-status pass">✅ PASS</span>
                <span class="result-file">${f.name}</span>
                <span class="result-meta">${f.lines} lines | 0 findings</span>
            </div>
        </div>
    `).join('');

    // Update stats
    document.getElementById('statFiles').textContent = '6';
    document.getElementById('statTests').textContent = '30';
    document.getElementById('statVulns').textContent = '7';
}

function renderDemoTrojanResults() {
    const container = document.getElementById('trojanResults');
    if (!container) return;

    const demoFindings = [
        {
            file: 'trojan_samples/alu_trojan.v',
            lines: 98,
            findings: [
                { severity: 'critical', rule: 'HT-001', name: 'Unused Trigger Logic', desc: 'Signal \'trigger_cnt\' is conditionally incremented but has minimal usage', line: 55 },
                { severity: 'high', rule: 'HT-004', name: 'Time-bomb Pattern', desc: 'Counter compared against 32-bit constant 0xDEAD_BEEF — classic trojan activation', line: 59 },
                { severity: 'medium', rule: 'HT-005', name: 'Covert Channel', desc: 'Dynamic bit-indexing using counter-derived index for data exfiltration', line: 88 },
            ]
        },
        {
            file: 'trojan_samples/counter_trojan.v',
            lines: 90,
            findings: [
                { severity: 'high', rule: 'HT-002', name: 'Suspicious State Machine', desc: 'State machine contains suspiciously named state \'T_DEAD\' (unreachable)', line: 47 },
                { severity: 'critical', rule: 'HT-003', name: 'Unauthorized I/O', desc: 'Output \'count\' modified based on suspicious \'armed\' flag', line: 82 },
            ]
        },
        {
            file: 'trojan_samples/shift_register_trojan.v',
            lines: 75,
            findings: [
                { severity: 'critical', rule: 'HT-005', name: 'Covert Channel', desc: 'Output mux with \'exfil_mode\' selector — classic covert channel trojan', line: 34 },
                { severity: 'high', rule: 'HT-001', name: 'Unused Trigger Logic', desc: 'Signal \'leak_counter\' incremented but rarely referenced', line: 41 },
            ]
        },
    ];

    container.innerHTML = demoFindings.map(f => `
        <div class="result-card">
            <div class="result-header">
                <span class="result-status fail">❌ FAIL</span>
                <span class="result-file">${f.file}</span>
                <span class="result-meta">${f.lines} lines | ${f.findings.length} findings</span>
            </div>
            <div class="result-findings">
                ${f.findings.map(finding => `
                    <div class="finding-item ${finding.severity}">
                        <div class="finding-header">
                            <span class="severity-tag ${finding.severity}">${finding.severity.toUpperCase()}</span>
                            <span class="finding-rule">${finding.rule}</span>
                            <span class="finding-name">${finding.name}</span>
                        </div>
                        <div class="finding-desc">${finding.desc}</div>
                        <div class="finding-line">Line ${finding.line}</div>
                    </div>
                `).join('')}
            </div>
        </div>
    `).join('');
}

function updateStats(data, type) {
    if (type === 'clean') {
        document.getElementById('statFiles').textContent =
            (parseInt(document.getElementById('statFiles').textContent) || 0) + data.summary.total_files;
    }
    if (type === 'trojan') {
        document.getElementById('statVulns').textContent = data.summary.total_findings;
    }
}

// ── Navigation Highlight ───────────────────────────────────────────
function initNavHighlight() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                navLinks.forEach(link => {
                    link.classList.toggle('active',
                        link.getAttribute('href') === `#${entry.target.id}`);
                });
            }
        });
    }, { rootMargin: '-20% 0px -80% 0px' });

    sections.forEach(section => observer.observe(section));
}

// ── Global Status ──────────────────────────────────────────────────
function updateGlobalStatus() {
    const badge = document.getElementById('globalStatus');
    if (badge) {
        badge.innerHTML = '<span class="status-dot"></span>Pipeline Active';
    }
}

// ── Utilities ──────────────────────────────────────────────────────
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ═══════════════════════════════════════════════════════════════════
// ═══ LIVE SCANNER ENGINE (Client-side Verilog Analysis) ═══════════
// ═══════════════════════════════════════════════════════════════════

// ── Sample Code Library ────────────────────────────────────────────
const SAMPLE_CODE = {
    clean_alu: `// Clean ALU Design — No trojans
module alu #(parameter WIDTH = 8) (
    input  wire [WIDTH-1:0] operand_a,
    input  wire [WIDTH-1:0] operand_b,
    input  wire [3:0]       opcode,
    output reg  [WIDTH-1:0] result,
    output reg              carry_out,
    output reg              zero_flag
);

    localparam OP_ADD = 4'd0, OP_SUB = 4'd1,
               OP_AND = 4'd2, OP_OR  = 4'd3,
               OP_XOR = 4'd4, OP_NOT = 4'd5,
               OP_SHL = 4'd6, OP_SHR = 4'd7;

    always @(*) begin
        carry_out = 1'b0;
        case (opcode)
            OP_ADD: {carry_out, result} = operand_a + operand_b;
            OP_SUB: {carry_out, result} = operand_a - operand_b;
            OP_AND: result = operand_a & operand_b;
            OP_OR:  result = operand_a | operand_b;
            OP_XOR: result = operand_a ^ operand_b;
            OP_NOT: result = ~operand_a;
            OP_SHL: result = operand_a << operand_b[2:0];
            OP_SHR: result = operand_a >> operand_b[2:0];
            default: result = {WIDTH{1'b0}};
        endcase
        zero_flag = (result == {WIDTH{1'b0}});
    end
endmodule`,

    trojan_alu: `// ALU with Hardware Trojan — Time Bomb + Covert Channel
module alu_trojan #(parameter WIDTH = 8) (
    input  wire             clk,
    input  wire             rst_n,
    input  wire [WIDTH-1:0] operand_a,
    input  wire [WIDTH-1:0] operand_b,
    input  wire [3:0]       opcode,
    output reg  [WIDTH-1:0] result,
    output reg              carry_out,
    output reg              zero_flag
);

    // ─── TROJAN: Hidden trigger counter ───
    reg [31:0] trigger_cnt;
    reg        trojan_active;

    // Rare activation condition
    assign rare_condition = (operand_a == 8'hDE) &&
                            (operand_b == 8'hAD) &&
                            (opcode == 4'hF);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            trigger_cnt <= 32'd0;
            trojan_active <= 1'b0;
        end else begin
            // HT-004: Time-bomb — count rare events
            if (rare_condition)
                trigger_cnt <= trigger_cnt + 1;

            // Activate after magic count
            if (trigger_cnt == 32'hDEAD_BEEF)
                trojan_active <= 1'b1;
        end
    end

    always @(*) begin
        carry_out = 1'b0;
        case (opcode)
            4'd0: {carry_out, result} = operand_a + operand_b;
            4'd1: {carry_out, result} = operand_a - operand_b;
            4'd2: result = operand_a & operand_b;
            default: result = {WIDTH{1'b0}};
        endcase
        zero_flag = (result == {WIDTH{1'b0}});
    end

    // HT-005: Covert channel — leak data through carry_out
    always @(posedge clk) begin
        if (trojan_active) begin
            carry_out <= operand_a[trigger_cnt[2:0]];
        end
    end
endmodule`,

    trojan_counter: `// Counter with Hardware Trojan — Hidden FSM Kill Switch
module counter_trojan #(parameter WIDTH = 8) (
    input  wire             clk,
    input  wire             rst_n,
    input  wire             enable,
    input  wire             up_down,
    input  wire             load,
    input  wire [WIDTH-1:0] data_in,
    output reg  [WIDTH-1:0] count,
    output wire             max_reached,
    output wire             min_reached
);

    // ─── TROJAN: Hidden FSM ───
    reg [2:0]  trojan_state;
    reg        armed;
    localparam T_IDLE   = 3'd0;
    localparam T_SEQ1   = 3'd1;
    localparam T_SEQ2   = 3'd2;
    localparam T_ARMED  = 3'd3;
    localparam T_DEAD   = 3'd4;   // Unreachable in normal operation

    // Magic activation sequence: load 0xAA, then 0x55, then 0xFF
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            trojan_state <= T_IDLE;
            armed <= 1'b0;
        end else if (load) begin
            case (trojan_state)
                T_IDLE:  trojan_state <= (data_in == 8'hAA) ? T_SEQ1 : T_IDLE;
                T_SEQ1:  trojan_state <= (data_in == 8'h55) ? T_SEQ2 : T_IDLE;
                T_SEQ2:  begin
                    if (data_in == 8'hFF) begin
                        trojan_state <= T_ARMED;
                        armed <= 1'b1;
                    end else
                        trojan_state <= T_IDLE;
                end
                default: trojan_state <= T_IDLE;
            endcase
        end
    end

    // Normal counter + trojan corruption
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            count <= {WIDTH{1'b0}};
        else if (load)
            count <= data_in;
        else if (enable) begin
            if (armed)
                count <= count ^ 8'hFF;  // HT-003: Corrupt output
            else
                count <= up_down ? count + 1 : count - 1;
        end
    end

    assign max_reached = (count == {WIDTH{1'b1}});
    assign min_reached = (count == {WIDTH{1'b0}});
endmodule`,

    trojan_shiftreg: `// Shift Register with Covert Exfiltration Channel
module shift_register_trojan #(parameter WIDTH = 8) (
    input  wire             clk,
    input  wire             rst_n,
    input  wire             enable,
    input  wire             load,
    input  wire             direction,
    input  wire             serial_in,
    input  wire [WIDTH-1:0] parallel_in,
    output wire             serial_out,
    output reg  [WIDTH-1:0] data_out
);

    // ─── TROJAN: Covert exfiltration ───
    reg        exfil_mode;
    reg [7:0]  leak_counter;
    wire       leak_bit;

    // XOR-reduce all register bits for covert leak
    assign leak_bit = ^data_out;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            leak_counter <= 8'd0;
            exfil_mode <= 1'b0;
        end else begin
            leak_counter <= leak_counter + 1;
            if (leak_counter == 8'hAB)
                exfil_mode <= 1'b1;
        end
    end

    // Normal shift register operation
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            data_out <= {WIDTH{1'b0}};
        else if (enable) begin
            if (load)
                data_out <= parallel_in;
            else if (direction)
                data_out <= {data_out[WIDTH-2:0], serial_in};
            else
                data_out <= {serial_in, data_out[WIDTH-1:1]};
        end
    end

    // HT-005: Covert channel through serial_out
    assign serial_out = exfil_mode ? leak_bit : data_out[WIDTH-1];
endmodule`,
};

// ── Detection Rules (ported from Python analyzer.py) ───────────────
const RULES = [
    {
        id: 'HT-001',
        name: 'Unused Trigger Logic',
        severity: 'critical',
        patterns: [
            { regex: /\b(trigger|trig|trojan|payload|bomb)\w*\s*<=?\s*/gi, desc: 'Signal with suspicious trigger-related name' },
            { regex: /\breg\s+.*\b(trigger|trig_cnt|trojan_cnt|bomb_cnt|payload_cnt)\b/gi, desc: 'Register with trigger-related name declared' },
        ],
    },
    {
        id: 'HT-002',
        name: 'Suspicious State Machine',
        severity: 'high',
        patterns: [
            { regex: /\b(T_ARMED|T_DEAD|T_KILL|TROJAN|ARMED|KILL_SWITCH|EXFIL)\b/gi, desc: 'Suspiciously named state or constant' },
            { regex: /\breg\s+.*\b(armed|trojan_active|kill_switch|exfil_mode|trojan_state)\b/gi, desc: 'Register with suspicious control name' },
            { regex: /localparam\s+\w*(armed|dead|kill|trojan|exfil)\w*\s*=/gi, desc: 'Suspicious state constant declaration' },
        ],
    },
    {
        id: 'HT-003',
        name: 'Unauthorized I/O Access',
        severity: 'critical',
        patterns: [
            { regex: /\b(carry_out|data_out|serial_out|count|result)\b\s*<=?\s*.*\b(trojan|armed|exfil|trigger)/gi, desc: 'Output modified based on suspicious signal' },
            { regex: /if\s*\(\s*(armed|trojan_active|exfil_mode|kill_switch)\s*\)[\s\S]*?(carry_out|data_out|serial_out|count|result)\s*<=?/gi, desc: 'Output conditionally modified by suspicious flag' },
        ],
    },
    {
        id: 'HT-004',
        name: 'Time-bomb Pattern',
        severity: 'high',
        patterns: [
            { regex: /(@\s*\(\s*(?:pos|neg)edge.*[\s\S]*?==\s*\d+\'h[0-9A-F]{4,})|(\b\d+\'h[0-9A-F]{4,})/gi, desc: 'Large hex constant (potential time-bomb limit)' },
            { regex: /==\s*\d+\'h(DEAD|BEEF|BABE|CAFE|FACE|1337|FEED|C0DE)/gi, desc: 'Known magic constant detected' },
        ],
    },
    {
        id: 'HT-006',
        name: 'Rare Input Trigger',
        severity: 'high',
        patterns: [
            { regex: /==\s*\d+'h[A-Fa-f0-9]+\s*\)\s*&&/gi, desc: 'Chained comparison with magic constants' },
            { regex: /&&\s*.*==.*&&\s*.*==/gi, desc: 'Multiple exact comparisons chained together' },
            { regex: /(assign\s+.*==\s*\d+\'h[0-9A-F]{4,})/gi, desc: 'Combinational logic comparison with large hex constant' },
            { regex: /(8\'h(DE|AD|BE|EF|BA|CA|FE|FA|13|37|AA|55|FF))\b/gi, desc: 'Known magic byte constant' },
        ],
    },
    {
        id: 'HT-005',
        name: 'Covert Channel',
        severity: 'medium',
        patterns: [
            { regex: /\^\s*\w+(\s*\[\s*\w+\s*\])*/gi, desc: 'XOR reduction (possible data leak)' },
            { regex: /\w+\s*\[\s*\w+\s*\[\s*\d+\s*:\s*\d+\s*\]\s*\]/gi, desc: 'Dynamic bit-indexing (side channel)' },
            { regex: /\b(exfil|leak|covert|steal|sniff)\w*/gi, desc: 'Signal with exfiltration-related name' },
            { regex: /\?\s*(leak_bit|exfil_bit|\^data_out|\^data)\b/gi, desc: 'Conditional mux with suspicious leak signal' },
        ],
    },
    {
        id: 'LINT-001',
        name: 'Undriven Signal',
        severity: 'low',
        patterns: [
            // Intentionally light for the live scanner to avoid false positives
        ],
    },
    {
        id: 'LINT-003',
        name: 'Latch Inference',
        severity: 'low',
        patterns: [
            // Intentionally light — complex analysis needed
        ],
    },
];

// ── Scan Engine ────────────────────────────────────────────────────
function analyzeVerilog(code) {
    const lines = code.split('\n');
    const findings = [];

    lines.forEach((line, index) => {
        const lineNum = index + 1;
        const trimmed = line.trim();

        // Skip comments
        if (trimmed.startsWith('//')) return;

        RULES.forEach(rule => {
            rule.patterns.forEach(pattern => {
                // Reset regex lastIndex for global patterns
                pattern.regex.lastIndex = 0;
                const match = pattern.regex.exec(line);
                if (match) {
                    findings.push({
                        rule_id: rule.id,
                        rule_name: rule.name,
                        severity: rule.severity,
                        line_number: lineNum,
                        line_content: trimmed,
                        description: pattern.desc,
                        match: match[0],
                    });
                }
            });
        });
    });

    // Deduplicate findings on same line with same rule
    const seen = new Set();
    const unique = findings.filter(f => {
        const key = `${f.rule_id}:${f.line_number}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
    });

    return unique;
}

// ── Init Live Scanner ──────────────────────────────────────────────
function initLiveScanner() {
    const codeInput = document.getElementById('codeInput');
    const lineNumbers = document.getElementById('lineNumbers');
    const sampleSelect = document.getElementById('sampleSelect');

    if (!codeInput || !lineNumbers) return;

    // Update line numbers on input
    function updateLineNumbers() {
        const lines = codeInput.value.split('\n').length;
        lineNumbers.textContent = Array.from({ length: Math.max(lines, 1) }, (_, i) => i + 1).join('\n');
    }

    codeInput.addEventListener('input', updateLineNumbers);
    codeInput.addEventListener('scroll', () => {
        lineNumbers.scrollTop = codeInput.scrollTop;
    });

    // Handle Tab key for indentation
    codeInput.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = codeInput.selectionStart;
            const end = codeInput.selectionEnd;
            codeInput.value = codeInput.value.substring(0, start) + '    ' + codeInput.value.substring(end);
            codeInput.selectionStart = codeInput.selectionEnd = start + 4;
            updateLineNumbers();
        }
    });

    // Sample selector
    if (sampleSelect) {
        sampleSelect.addEventListener('change', () => {
            const key = sampleSelect.value;
            if (key && SAMPLE_CODE[key]) {
                codeInput.value = SAMPLE_CODE[key];
                updateLineNumbers();
            }
        });
    }

    updateLineNumbers();
}

// ── Run Live Scan (called from button onclick) ─────────────────────
function runLiveScan() {
    const code = document.getElementById('codeInput').value;
    const resultsBody = document.getElementById('scanResultsBody');
    const scanStatus = document.getElementById('scanStatus');

    if (!code.trim()) {
        resultsBody.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">⚠️</div>
                <p>Please paste some Verilog code first</p>
            </div>`;
        return;
    }

    // Show scanning state
    scanStatus.innerHTML = '<span class="scan-status-dot scanning"></span>Scanning...';
    resultsBody.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon" style="animation: pulse 1s infinite;">🔍</div>
            <p>Analyzing code...</p>
        </div>`;

    // Small delay for visual effect
    setTimeout(() => {
        const findings = analyzeVerilog(code);
        renderLiveResults(findings, code.split('\n').length);
    }, 600);
}

// ── Render Live Results ────────────────────────────────────────────
function renderLiveResults(findings, totalLines) {
    const resultsBody = document.getElementById('scanResultsBody');
    const scanStatus = document.getElementById('scanStatus');

    const critical = findings.filter(f => f.severity === 'critical').length;
    const high = findings.filter(f => f.severity === 'high').length;
    const medium = findings.filter(f => f.severity === 'medium').length;
    const low = findings.filter(f => f.severity === 'low').length;

    // Update status
    if (findings.length === 0) {
        scanStatus.innerHTML = '<span class="scan-status-dot pass"></span>✅ Clean — No issues';
    } else if (critical > 0) {
        scanStatus.innerHTML = `<span class="scan-status-dot fail"></span>❌ ${findings.length} finding(s)`;
    } else {
        scanStatus.innerHTML = `<span class="scan-status-dot warning"></span>⚠️ ${findings.length} finding(s)`;
    }

    // Build results HTML
    let html = '';

    // Summary banner
    if (findings.length === 0) {
        html += `<div class="live-summary pass">✅ PASS — No vulnerabilities detected (${totalLines} lines scanned)</div>`;
    } else {
        const cls = critical > 0 ? 'fail' : 'warning';
        const icon = critical > 0 ? '❌' : '⚠️';
        html += `<div class="live-summary ${cls}">
            ${icon} ${findings.length} finding(s) in ${totalLines} lines — `;
        if (critical) html += `🔴 ${critical} Critical `;
        if (high) html += `🟠 ${high} High `;
        if (medium) html += `🟡 ${medium} Medium `;
        if (low) html += `🔵 ${low} Low `;
        html += `</div>`;
    }

    // Individual findings
    findings.forEach(f => {
        html += `
        <div class="live-finding ${f.severity}">
            <div class="finding-header">
                <span class="severity-tag ${f.severity}">${f.severity.toUpperCase()}</span>
                <span class="finding-rule">${f.rule_id}</span>
                <span class="finding-name">${f.rule_name}</span>
            </div>
            <div class="finding-desc">${escapeHtml(f.description)}</div>
            <div class="finding-line">Line ${f.line_number}: <code>${escapeHtml(f.line_content)}</code></div>
        </div>`;
    });

    resultsBody.innerHTML = html;
}

