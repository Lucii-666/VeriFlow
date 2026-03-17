// =============================================================================
// VeriFlow - Shift Register
// =============================================================================
// Configurable shift register with parallel load and serial/parallel output.
// =============================================================================

module shift_register #(
    parameter WIDTH = 8
)(
    input  wire                clk,
    input  wire                rst_n,
    input  wire                enable,
    input  wire                load,           // Parallel load
    input  wire                direction,      // 1 = left, 0 = right
    input  wire                serial_in,
    input  wire [WIDTH-1:0]    parallel_in,
    output wire                serial_out,
    output wire [WIDTH-1:0]    parallel_out
);

    reg [WIDTH-1:0] shift_reg;

    assign parallel_out = shift_reg;
    assign serial_out   = direction ? shift_reg[WIDTH-1] : shift_reg[0];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            shift_reg <= {WIDTH{1'b0}};
        end else if (load) begin
            shift_reg <= parallel_in;
        end else if (enable) begin
            if (direction) begin
                // Shift left: MSB out, serial_in at LSB
                shift_reg <= {shift_reg[WIDTH-2:0], serial_in};
            end else begin
                // Shift right: LSB out, serial_in at MSB
                shift_reg <= {serial_in, shift_reg[WIDTH-1:1]};
            end
        end
    end

endmodule
