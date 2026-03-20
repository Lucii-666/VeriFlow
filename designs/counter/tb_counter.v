// =============================================================================
// VeriFlow - Counter Testbench
// =============================================================================

`timescale 1ns / 1ps

module tb_counter;

    parameter WIDTH = 8;

    reg                  clk;
    reg                  rst_n;
    reg                  enable;
    reg                  up_down;
    reg                  load;
    reg  [WIDTH-1:0]     load_value;
    wire [WIDTH-1:0]     count;
    wire                 max_reached;
    wire                 min_reached;

    integer pass_count = 0;
    integer fail_count = 0;
    integer test_num   = 0;

    counter #(.WIDTH(WIDTH)) dut (
        .clk         (clk),
        .rst_n       (rst_n),
        .enable      (enable),
        .up_down     (up_down),
        .load        (load),
        .load_value  (load_value),
        .count       (count),
        .max_reached (max_reached),
        .min_reached (min_reached)
    );

    initial clk = 0;
    always #5 clk = ~clk;

    initial begin
        $dumpfile("counter_waveform.vcd");
        $dumpvars(0, tb_counter);
    end

    task check_count;
        input [WIDTH-1:0] expected;
        input [63:0]      test_name;
        begin
            test_num = test_num + 1;
            #1;
            if (count === expected) begin
                $display("[PASS] Test %0d: %s | Count=%0d (expected %0d)",
                         test_num, test_name, count, expected);
                pass_count = pass_count + 1;
            end else begin
                $display("[FAIL] Test %0d: %s | Count=%0d (expected %0d)",
                         test_num, test_name, count, expected);
                fail_count = fail_count + 1;
            end
        end
    endtask

    initial begin
        $display("");
        $display("╔══════════════════════════════════════════════════╗");
        $display("║        VeriFlow Counter Testbench v1.0          ║");
        $display("╚══════════════════════════════════════════════════╝");
        $display("");

        rst_n      = 0;
        enable     = 0;
        up_down    = 1;
        load       = 0;
        load_value = 0;

        // Reset
        repeat(3) @(posedge clk);
        rst_n = 1;
        @(posedge clk);

        $display("--- Reset Test ---");
        check_count(8'd0, "RESET   ");

        $display("--- Count Up Tests ---");
        enable = 1; up_down = 1;
        @(posedge clk); check_count(8'd1, "UP_1    ");
        @(posedge clk); check_count(8'd2, "UP_2    ");
        @(posedge clk); check_count(8'd3, "UP_3    ");

        $display("--- Count Down Tests ---");
        up_down = 0;
        @(posedge clk); check_count(8'd2, "DOWN_1  ");
        @(posedge clk); check_count(8'd1, "DOWN_2  ");

        $display("--- Enable Control ---");
        enable = 0;
        @(posedge clk); check_count(8'd1, "DISABLE ");
        @(posedge clk); check_count(8'd1, "DISABLE2");

        $display("--- Load Test ---");
        load = 1; load_value = 8'hAB;
        @(posedge clk);
        load = 0;
        check_count(8'hAB, "LOAD    ");

        $display("--- Max Reached Test ---");
        load = 1; load_value = 8'hFE;
        @(posedge clk);
        load = 0; enable = 1; up_down = 1;
        @(posedge clk);
        check_count(8'hFF, "MAX     ");
        if (max_reached) begin
            $display("[PASS] max_reached flag asserted");
            pass_count = pass_count + 1;
        end else begin
            $display("[FAIL] max_reached flag NOT asserted");
            fail_count = fail_count + 1;
        end

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
            $finish;
        end else begin
            $display("SIMULATION RESULT: PASS");
            $finish;
        end
    end

    initial begin
        #100000;
        $display("[ERROR] Simulation timeout!");
        $finish(1);
    end

endmodule
