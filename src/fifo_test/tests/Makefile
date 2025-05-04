SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/../rtl/synchronous_fifo.v
VERILOG_SOURCES += $(PWD)/../rtl/ram.v
VERILOG_SOURCES += $(PWD)/../wrappers/fifo_test.v
TOPLEVEL = fifo_test

all: simple classes

simple:
	$(MAKE) sim MODULE=simple_fifo_test TOPLEVEL=fifo_test


classes:
	$(MAKE) sim MODULE=fifo_test_with_classes TOPLEVEL=fifo_test


include $(shell cocotb-config --makefiles)/Makefile.sim
