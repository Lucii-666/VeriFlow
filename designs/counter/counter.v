// =============================================================================
// VeriFlow - Configurable Binary Counter
// =============================================================================
// A clean up/down counter with enable and load functionality.
// =============================================================================

module counter #(
    parameter WIDTH = 8
)(
    input  wire                clk,
    input  wire                rst_n,
    input  wire                enable,
    input  wire                up_down,    // 1 = count up, 0 = count down
    input  wire                load,
    input  wire [WIDTH-1:0]    load_value,
    output reg  [WIDTH-1:0]    count,
    output wire                max_reached,
    output wire                min_reached
);

    assign max_reached = (count == {WIDTH{1'b1}});
    assign min_reached = (count == {WIDTH{1'b0}});

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            count <= {WIDTH{1'b0}};
        end else if (load) begin
            count <= load_value;
        end else if (enable) begin
            if (up_down)
                count <= count + 1'b1;
            else
                count <= count - 1'b1;
        end
    end

endmodule
