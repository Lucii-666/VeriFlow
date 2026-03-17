// =============================================================================
// VeriFlow - ALU Testbench
// =============================================================================
// Comprehensive testbench for the ALU module.
// Tests all operations and edge cases.
// =============================================================================

`timescale 1ns / 1ps

module tb_alu;

    parameter WIDTH = 8;

    // Signals
    reg                  clk;
    reg                  rst_n;
    reg  [WIDTH-1:0]     operand_a;
    reg  [WIDTH-1:0]     operand_b;
    reg  [3:0]           opcode;
    wire [WIDTH-1:0]     result;
    wire                 carry_out;
    wire                 zero_flag;
    wire                 overflow_flag;

    // Test tracking
    integer pass_count = 0;
    integer fail_count = 0;
    integer test_num   = 0;

    // DUT instantiation
    alu #(.WIDTH(WIDTH)) dut (
        .clk           (clk),
        .rst_n         (rst_n),
        .operand_a     (operand_a),
        .operand_b     (operand_b),
        .opcode        (opcode),
        .result        (result),
        .carry_out     (carry_out),
        .zero_flag     (zero_flag),
        .overflow_flag (overflow_flag)
    );

    // Clock generation: 100 MHz
    initial clk = 0;
    always #5 clk = ~clk;

    // VCD dump for waveform viewing
    initial begin
        $dumpfile("alu_waveform.vcd");
        $dumpvars(0, tb_alu);
    end

    // Task: Apply operation and check result
    task apply_and_check;
        input [3:0]        op;
        input [WIDTH-1:0]  a, b;
        input [WIDTH-1:0]  expected;
        input [63:0]       test_name; // 8-char name
        begin
            test_num = test_num + 1;
            @(negedge clk);
            opcode    = op;
            operand_a = a;
            operand_b = b;
            @(posedge clk);
            @(posedge clk); // Wait for registered output
            #1;
            if (result === expected) begin
                $display("[PASS] Test %0d: %s | A=%h B=%h => Result=%h",
                         test_num, test_name, a, b, result);
                pass_count = pass_count + 1;
            end else begin
                $display("[FAIL] Test %0d: %s | A=%h B=%h => Result=%h (expected %h)",
                         test_num, test_name, a, b, result, expected);
                fail_count = fail_count + 1;
            end
        end
    endtask

    // Main test sequence
    initial begin
        $display("");
        $display("╔══════════════════════════════════════════════════╗");
        $display("║          VeriFlow ALU Testbench v1.0            ║");
        $display("╠══════════════════════════════════════════════════╣");
        $display("║  Testing %0d-bit ALU with 10 operations          ║", WIDTH);
        $display("╚══════════════════════════════════════════════════╝");
        $display("");

        // Initialize
        rst_n     = 0;
        operand_a = 0;
        operand_b = 0;
        opcode    = 0;

        // Reset sequence
        repeat(3) @(posedge clk);
        rst_n = 1;
        @(posedge clk);

        $display("--- Addition Tests ---");
        apply_and_check(4'b0000, 8'h05, 8'h03, 8'h08, "ADD     ");
        apply_and_check(4'b0000, 8'hFF, 8'h01, 8'h00, "ADD_OVF ");
        apply_and_check(4'b0000, 8'h00, 8'h00, 8'h00, "ADD_ZERO");

        $display("--- Subtraction Tests ---");
        apply_and_check(4'b0001, 8'h0A, 8'h03, 8'h07, "SUB     ");
        apply_and_check(4'b0001, 8'h05, 8'h05, 8'h00, "SUB_ZERO");
        apply_and_check(4'b0001, 8'h03, 8'h0A, 8'hF9, "SUB_NEG ");

        $display("--- Logic Tests ---");
        apply_and_check(4'b0010, 8'hF0, 8'h0F, 8'h00, "AND     ");
        apply_and_check(4'b0011, 8'hF0, 8'h0F, 8'hFF, "OR      ");
        apply_and_check(4'b0100, 8'hAA, 8'h55, 8'hFF, "XOR     ");
        apply_and_check(4'b0101, 8'hAA, 8'h00, 8'h55, "NOT     ");

        $display("--- Shift Tests ---");
        apply_and_check(4'b0110, 8'h01, 8'h03, 8'h08, "SHL     ");
        apply_and_check(4'b0111, 8'h80, 8'h03, 8'h10, "SHR     ");

        $display("--- Multiply Test ---");
        apply_and_check(4'b1000, 8'h03, 8'h04, 8'h0C, "MUL     ");

        // Summary
        $display("");
        $display("╔══════════════════════════════════════════════════╗");
        $display("║                 TEST SUMMARY                    ║");
        $display("╠══════════════════════════════════════════════════╣");
        $display("║  Total:  %0d                                     ", pass_count + fail_count);
        $display("║  Passed: %0d                                     ", pass_count);
        $display("║  Failed: %0d                                     ", fail_count);
        if (fail_count == 0)
            $display("║  Status: ✅ ALL TESTS PASSED                    ║");
        else
            $display("║  Status: ❌ SOME TESTS FAILED                   ║");
        $display("╚══════════════════════════════════════════════════╝");
        $display("");

        if (fail_count > 0) begin
            $display("SIMULATION RESULT: FAIL");
            $finish(1);
        end else begin
            $display("SIMULATION RESULT: PASS");
            $finish(0);
        end
    end

    // Timeout watchdog
    initial begin
        #100000;
        $display("[ERROR] Simulation timeout!");
        $finish(1);
    end

endmodule
