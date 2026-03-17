// =============================================================================
// VeriFlow - 8-bit Arithmetic Logic Unit (ALU)
// =============================================================================
// A clean, verified ALU design supporting basic arithmetic and logic operations.
// This serves as a reference design for the VeriFlow CI/CD pipeline.
// =============================================================================

module alu #(
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

    // Opcode definitions
    localparam OP_ADD  = 4'b0000;
    localparam OP_SUB  = 4'b0001;
    localparam OP_AND  = 4'b0010;
    localparam OP_OR   = 4'b0011;
    localparam OP_XOR  = 4'b0100;
    localparam OP_NOT  = 4'b0101;
    localparam OP_SHL  = 4'b0110;  // Shift left
    localparam OP_SHR  = 4'b0111;  // Shift right
    localparam OP_MUL  = 4'b1000;  // Multiply (lower bits)
    localparam OP_CMP  = 4'b1001;  // Compare

    reg [WIDTH:0] temp_result;

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
                    temp_result   = {1'b0, operand_a} + {1'b0, operand_b};
                    result        <= temp_result[WIDTH-1:0];
                    carry_out     <= temp_result[WIDTH];
                    overflow_flag <= (operand_a[WIDTH-1] == operand_b[WIDTH-1]) &&
                                    (temp_result[WIDTH-1] != operand_a[WIDTH-1]);
                end

                OP_SUB: begin
                    temp_result   = {1'b0, operand_a} - {1'b0, operand_b};
                    result        <= temp_result[WIDTH-1:0];
                    carry_out     <= temp_result[WIDTH];  // Borrow
                    overflow_flag <= (operand_a[WIDTH-1] != operand_b[WIDTH-1]) &&
                                    (temp_result[WIDTH-1] != operand_a[WIDTH-1]);
                end

                OP_AND: result <= operand_a & operand_b;
                OP_OR:  result <= operand_a | operand_b;
                OP_XOR: result <= operand_a ^ operand_b;
                OP_NOT: result <= ~operand_a;
                OP_SHL: result <= operand_a << operand_b[2:0];
                OP_SHR: result <= operand_a >> operand_b[2:0];

                OP_MUL: begin
                    result <= operand_a[3:0] * operand_b[3:0];
                end

                OP_CMP: begin
                    if (operand_a == operand_b)
                        result <= {WIDTH{1'b0}};
                    else if (operand_a > operand_b)
                        result <= {{(WIDTH-1){1'b0}}, 1'b1};
                    else
                        result <= {WIDTH{1'b1}};
                end

                default: result <= {WIDTH{1'b0}};
            endcase

            // Zero flag
            zero_flag <= (result == {WIDTH{1'b0}});
        end
    end

endmodule
