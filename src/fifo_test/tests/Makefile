SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/../rtl/synchronous_fifo.v
VERILOG_SOURCES += $(PWD)/../rtl/ram.v
VERILOG_SOURCES += $(PWD)/../wrappers/fifo_test.v
all: fifo
fifo:
	rm -rf sim_build
	$(MAKE) sim MODULE=fifo_test TOPLEVEL=synchronous_fifo
include $(shell cocotb-config --makefiles)/Makefile.sim
