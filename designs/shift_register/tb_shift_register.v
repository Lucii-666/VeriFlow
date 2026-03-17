// =============================================================================
// VeriFlow - Shift Register Testbench
// =============================================================================

`timescale 1ns / 1ps

module tb_shift_register;

    parameter WIDTH = 8;

    reg                  clk;
    reg                  rst_n;
    reg                  enable;
    reg                  load;
    reg                  direction;
    reg                  serial_in;
    reg  [WIDTH-1:0]     parallel_in;
    wire                 serial_out;
    wire [WIDTH-1:0]     parallel_out;

    integer pass_count = 0;
    integer fail_count = 0;
    integer test_num   = 0;

    shift_register #(.WIDTH(WIDTH)) dut (
        .clk          (clk),
        .rst_n        (rst_n),
        .enable       (enable),
        .load         (load),
        .direction    (direction),
        .serial_in    (serial_in),
        .parallel_in  (parallel_in),
        .serial_out   (serial_out),
        .parallel_out (parallel_out)
    );

    initial clk = 0;
    always #5 clk = ~clk;

    initial begin
        $dumpfile("shift_register_waveform.vcd");
        $dumpvars(0, tb_shift_register);
    end

    task check_output;
        input [WIDTH-1:0] expected;
        input [63:0]      test_name;
        begin
            test_num = test_num + 1;
            #1;
            if (parallel_out === expected) begin
                $display("[PASS] Test %0d: %s | Out=0x%h",
                         test_num, test_name, parallel_out);
                pass_count = pass_count + 1;
            end else begin
                $display("[FAIL] Test %0d: %s | Out=0x%h (expected 0x%h)",
                         test_num, test_name, parallel_out, expected);
                fail_count = fail_count + 1;
            end
        end
    endtask

    initial begin
        $display("");
        $display("╔══════════════════════════════════════════════════╗");
        $display("║     VeriFlow Shift Register Testbench v1.0      ║");
        $display("╚══════════════════════════════════════════════════╝");
        $display("");

        rst_n       = 0;
        enable      = 0;
        load        = 0;
        direction   = 1;
        serial_in   = 0;
        parallel_in = 0;

        repeat(3) @(posedge clk);
        rst_n = 1;
        @(posedge clk);

        $display("--- Reset Test ---");
        check_output(8'h00, "RESET   ");

        $display("--- Parallel Load ---");
        load = 1; parallel_in = 8'hA5;
        @(posedge clk);
        load = 0;
        check_output(8'hA5, "LOAD    ");

        $display("--- Shift Left Tests ---");
        direction = 1; enable = 1; serial_in = 0;
        @(posedge clk); check_output(8'h4A, "SHL_1   ");
        @(posedge clk); check_output(8'h94, "SHL_2   ");

        $display("--- Shift Left with serial_in=1 ---");
        serial_in = 1;
        @(posedge clk); check_output(8'h29, "SHL_S1  ");

        $display("--- Reload & Shift Right ---");
        enable = 0; load = 1; parallel_in = 8'hA5;
        @(posedge clk);
        load = 0;

        direction = 0; enable = 1; serial_in = 0;
        @(posedge clk); check_output(8'h52, "SHR_1   ");
        @(posedge clk); check_output(8'h29, "SHR_2   ");

        $display("--- Shift Right with serial_in=1 ---");
        serial_in = 1;
        @(posedge clk); check_output(8'h94, "SHR_S1  ");

        $display("--- Enable Control ---");
        enable = 0;
        @(posedge clk); check_output(8'h94, "DISABLE ");

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

        if (fail_count > 0) begin
            $display("SIMULATION RESULT: FAIL");
            $finish(1);
        end else begin
            $display("SIMULATION RESULT: PASS");
            $finish(0);
        end
    end

    initial begin
        #100000;
        $display("[ERROR] Simulation timeout!");
        $finish(1);
    end

endmodule
