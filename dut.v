`timescale 1ns/1ps

module dut (
    input              clk,          // Clock input
    input              rst,          // Reset input

    input  [511:0]     input_pin,    // 512-bit input pin (not used in DUT logic)
    output reg [511:0] output_pin,   // 512-bit output pin

    // 4 lanes (128 bits each) - used only for observation in the testbench
    input  [127:0]     lane_0,
    input  [127:0]     lane_1,
    input  [127:0]     lane_2,
    input  [127:0]     lane_3,

    // "lane_*_out" are also just pins so that we can see split data in GTKWave
    input  [127:0]     lane_0_out,
    input  [127:0]     lane_1_out,
    input  [127:0]     lane_2_out,
    input  [127:0]     lane_3_out
);
    wire [511:0] constant_value = {128'h1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef,128'h1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef,128'h1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef,128'h1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef};
    // 128-bit block (32 hex chars = 128 bits)
    // localparam [127:0] CONST_128 =
        // 128'h1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef;

    // 512-bit constant made of 4 identical 128-bit blocks
    // wire [511:0] constant_value = {CONST_128, CONST_128, CONST_128, CONST_128};

    // Sequential logic for output_pin generation
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            // Reset the output_pin to 0 on reset
            output_pin <= 512'b0;
        end else begin
            // Generate the constant 512-bit value every cycle
            output_pin <= constant_value;
        end
    end

    // Dumpfile for GTKWave (optional, cocotb-test also creates waves)
    initial begin
        $dumpfile("dut.vcd");
        $dumpvars(0, dut);
    end

endmodule
