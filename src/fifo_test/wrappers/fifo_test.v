module fifo_test # (parameter DWIDTH=16, AWIDTH=4, DEPTH=16)(
    output reg clk,
    input reset,
    input push,
    input [DWIDTH-1:0] data_in,  // Cambiado de 'in' a 'data_in'
    input pop,
    output [DWIDTH-1:0] out,
    output empty,
    output almostempty,
    output full,
    output almostfull,
    output reg [AWIDTH:0] num
);

synchronous_fifo dut (
    .clk(clk),
    .reset(reset),
    .push(push),
    .in(data_in),  // Conectado al nuevo nombre
    .pop(pop),
    .out(out),
    .empty(empty),
    .almostempty(almostempty),
    .full(full),
    .almostfull(almostfull),
    .num(num)
);

initial begin
    $dumpfile("fifo_sim.vcd");
    $dumpvars(0, fifo_test);  
    clk = 0;
    forever #5 clk = ~clk;
end

endmodule