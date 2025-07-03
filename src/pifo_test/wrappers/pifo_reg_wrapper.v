module pifo_reg_wrapper (
    output reg clk,
    input rst,

    input insert,
    input [15:0] rank_in,
    input [11:0] meta_in,

    input remove,

    output valid_out,
    output [15:0] rank_out,
    output [11:0] meta_out,
    output empty,
    output full,

    output max_valid_out,
    output [15:0] max_rank_out,
    output [11:0] max_meta_out,
    output [4:0] num_entries
);

pifo_reg dut (
    .clk(clk),
    .rst(rst),
    .insert(insert),
    .rank_in(rank_in),
    .meta_in(meta_in),
    .remove(remove),
    .valid_out(valid_out),
    .rank_out(rank_out),
    .meta_out(meta_out),
    .max_valid_out(max_valid_out),   
    .max_rank_out(max_rank_out),
    .max_meta_out(max_meta_out),
    .num_entries(num_entries),
    .empty(empty),
    .full(full)
);


endmodule
