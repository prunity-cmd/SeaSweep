// -----------------------------------------------------------------------------
// tb_sonar_chain.v  -  feeds a simulated ping through matched_filter ->
// envelope_decim and dumps both outputs for comparison with the Python model.
//
// Inputs  : vectors/input.hex   (signed 12-bit ADC samples, one per line)
//           vectors/coeffs.hex  (signed 12-bit taps)
//           vectors/tb_params.vh (`define NSAMP ..., written by export script)
// Outputs : vectors/rtl_mf.txt  (FIR output, decimal, one per line)
//           vectors/rtl_env.txt (envelope output, decimal, one per line)
// -----------------------------------------------------------------------------
`timescale 1ns/1ps
`include "vectors/tb_params.vh"

module tb_sonar_chain;
    localparam DW = 12, AW = 32, N = 128, D = 8;

    reg clk = 0, rst = 1, in_valid = 0;
    reg signed [DW-1:0] x = 0;
    reg signed [DW-1:0] mem [0:`NSAMP-1];

    wire              mf_valid, env_valid;
    wire signed [AW-1:0] y;
    wire        [AW-1:0] env;

    matched_filter #(.N(N), .DW(DW), .AW(AW), .COEF_FILE("vectors/coeffs.hex"))
        u_mf (.clk(clk), .rst(rst), .in_valid(in_valid), .x(x),
              .out_valid(mf_valid), .y(y));

    envelope_decim #(.AW(AW), .D(D))
        u_env (.clk(clk), .rst(rst), .in_valid(mf_valid), .y(y),
               .out_valid(env_valid), .env(env));

    always #5 clk = ~clk;                   // 100 MHz simulation clock

    integer f_mf, f_env, k;
    initial begin
        $readmemh("vectors/input.hex", mem);
        f_mf  = $fopen("vectors/rtl_mf.txt", "w");
        f_env = $fopen("vectors/rtl_env.txt", "w");
        repeat (4) @(posedge clk);
        rst <= 0;
        for (k = 0; k < `NSAMP; k = k + 1) begin
            @(posedge clk);
            x        <= mem[k];
            in_valid <= 1'b1;
        end
        @(posedge clk);
        in_valid <= 1'b0;
        repeat (8) @(posedge clk);
        $fclose(f_mf);
        $fclose(f_env);
        $display("Simulated %0d samples.", `NSAMP);
        $finish;
    end

    always @(posedge clk) begin
        if (mf_valid)  $fwrite(f_mf,  "%0d\n", y);
        if (env_valid) $fwrite(f_env, "%0d\n", env);
    end
endmodule
