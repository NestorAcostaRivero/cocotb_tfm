import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly, NextTimeStep, FallingEdge
from cocotb_bus.drivers import BusDriver
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db
from cocotb_bus.monitors import BusMonitor
import os
import random


def sb_fn(actual_value):
    global expected_value
    assert actual_value == expected_value.pop(0), "Scoreboard Matching Failed"


@CoverPoint("top.a",  # noqa F405
            xf=lambda x, y: x,
            bins=[0, 1]
            )
@CoverPoint("top.b",  # noqa F405
            xf=lambda x, y: y,
            bins=[0, 1]
            )
@CoverCross("top.cross.ab",
            items=["top.a",
                   "top.b"
                   ]
            )
def ab_cover(a, b):
    pass


@CoverPoint("top.prot.a.current",  # noqa F405
            xf=lambda x: x['current'],
            bins=['Idle', 'Rdy', 'Txn'],
            )
@CoverPoint("top.prot.a.previous",  # noqa F405
            xf=lambda x: x['previous'],
            bins=['Idle', 'Rdy', 'Txn'],
            )
@CoverCross("top.cross.a_prot.cross",
            items=["top.prot.a.previous",
                   "top.prot.a.current"
                   ],
            ign_bins=[('Rdy', 'Idle')]
            )
def a_prot_cover(txn):
    pass

@cocotb.test()
async def fifo_test(dut):
    global expected_value
    expected_value = []
    dut.reset.value = 1
    await Timer(1, 'ns')
    dut.reset.value = 0
    await Timer(1, 'ns')
    await RisingEdge(dut.clk)
    dut.reset.value = 1
    ent_drv = InputDriver(dut, 'ent', dut.clk)
    # IO_Monitor(dut, 'a', dut.CLK, callback=a_prot_cover)
    bdrv = InputDriver(dut, 'b', dut.clk)
    OutputDriver(dut, 'sal', dut.clk, sb_fn)

    for i in range(20):
        a = random.randint(0, 1)
        b = random.randint(0, 1)
        expected_value.append(a | b)
        ent_drv.append(a)
        ab_cover(a, b)
    while len(expected_value) > 0:
        await Timer(2, 'ns')


class InputDriver(BusDriver):

    _signals = ['push', 'input']

    def __init__(self, dut, name, clk):
        BusDriver.__init__(self, dut, name, clk)
        self.clk = clk

    async def _driver_send(self, value, sync=True):
        for i in range(random.randint(0, 20)):
            await RisingEdge(self.clk)
        await self._wait_for_signal(self.bus.push) 
        self.bus.input.value = value
        await ReadOnly()
        await RisingEdge(self.clk)
        await NextTimeStep()


class IO_Monitor(BusMonitor):
    _signals = ['rdy', 'en', 'data']

    async def _monitor_recv(self):
        fallingedge = FallingEdge(self.clock)
        rdonly = ReadOnly()
        phases = {
            0: 'Idle',
            1: 'Rdy',
            3: 'Txn'
        }
        prev = 'Idle'
        while True:
            await fallingedge
            await rdonly
            txn = (self.bus.en.value << 1) | self.bus.rdy.value
            self._recv({'previous': prev, 'current': phases[txn]})
            prev = phases[txn]


class OutputDriver(BusDriver):
    _signals = ['pop', 'out']

    def __init__(self, dut, name, clk, sb_callback):
        BusDriver.__init__(self, dut, name, clk)
        self.clk = clk
        self.callback = sb_callback
        self.append(0)

    async def _driver_send(self, value, sync=True):
        while True:
            for i in range(random.randint(0, 20)):
                await RisingEdge(self.clk)
            await self._wait_for_signal(self.bus.pop)
            await ReadOnly()
            self.callback(self.bus.out.value)
            await RisingEdge(self.clk)
            await NextTimeStep()
            self.bus.en.value = 0
