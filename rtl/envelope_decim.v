// -----------------------------------------------------------------------------
// envelope_decim.v  -  rectify + peak-hold decimation
//
// env[m] = max(|y[mD]|, |y[mD+1]|, ..., |y[mD+D-1]|)
//
// A cheap envelope detector: absolute value followed by a block maximum over
// D samples. It reduces the data rate by D before the Raspberry Pi, which is
// what lets the Pi stay idle most of the time. Peak hold (rather than
// averaging) preserves small, strong reflectors such as metal debris.
// -----------------------------------------------------------------------------
`timescale 1ns/1ps

module envelope_decim #(
    parameter AW = 32,
    parameter D  = 8                        // decimation factor
) (
    input  wire                 clk,
    input  wire                 rst,
    input  wire                 in_valid,
    input  wire signed [AW-1:0] y,
    output reg                  out_valid,
    output reg         [AW-1:0] env
);

    wire [AW-1:0] mag = y[AW-1] ? (~y + 1'b1) : y;

    reg [AW-1:0]          peak;
    reg [$clog2(D)-1:0]   cnt;

    always @(posedge clk) begin
        if (rst) begin
            peak      <= {AW{1'b0}};
            cnt       <= 0;
            env       <= {AW{1'b0}};
            out_valid <= 1'b0;
        end else begin
            out_valid <= 1'b0;
            if (in_valid) begin
                if (cnt == D-1) begin
                    env       <= (mag > peak) ? mag : peak;
                    out_valid <= 1'b1;
                    peak      <= {AW{1'b0}};
                    cnt       <= 0;
                end else begin
                    peak <= (mag > peak) ? mag : peak;
                    cnt  <= cnt + 1'b1;
                end
            end
        end
    end

endmodule
