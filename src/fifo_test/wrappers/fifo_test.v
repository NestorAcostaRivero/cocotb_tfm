module fifo_test;
    reg clk;
    reg reset;
    reg push;
    reg pop;
    reg [15:0] in;
    wire [15:0] out;
    wire empty, almostempty, full, almostfull;
    wire [4:0] num;

    synchronous_fifo dut (
        .clk(clk),
        .reset(reset),
        .push(push),
        .in(in),
        .pop(pop),
        .out(out),
        .empty(empty),
        .almostempty(almostempty),
        .full(full),
        .almostfull(almostfull),
        .num(num)
    );
endmodule
