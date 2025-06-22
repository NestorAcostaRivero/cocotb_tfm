TOPLEVEL_LANG = verilog

VERILOG_SOURCES = $(PWD)/../rtl/pifo_reg.v 
VERILOG_SOURCES += $(PWD)/../wrappers/pifo_reg_wrapper.v
TOPLEVEL = pifo_reg_wrapper
MODULE = pifo_test
SIM = icarus

IVERILOG_FLAGS += -Wno-timescale -Wno-fatal

include $(shell cocotb-config --makefiles)/Makefile.sim


