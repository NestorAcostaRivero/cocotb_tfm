import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly, NextTimeStep, FallingEdge
from cocotb.clock import Clock
from cocotb_bus.drivers import BusDriver
from cocotb_bus.monitors import BusMonitor
import random
import logging

class FifoScoreboard:
    def __init__(self, dut):
        self.expected_values = []
        self.dut = dut
    
    def append(self, value):
        self.expected_values.append(value)
        self.dut._log.info(f"Added to scoreboard: {value}")
    
    def check(self, actual_value):
        if not self.expected_values:
            self.dut._log.error("No more expected values!")
            return
            
        expected = self.expected_values.pop(0)
        assert actual_value == expected, f"Scoreboard error: Expected {expected}, got {actual_value}"
        self.dut._log.info(f"Verified: {actual_value} == {expected}")

@cocotb.test()
async def fifo_test_with_classes(dut):
    # Se prepara el log
    dut._log.setLevel(logging.INFO)
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start()) #corrutina del reloj para que se ejecute concurrentemente con el test
    
    # Inicialización
    dut.reset.value = 1
    dut.push.value = 0
    dut.pop.value = 0
    dut.data_in.value = 0

    # Instancia del scoreboard
    sb = FifoScoreboard(dut)

    # Instancia del PushDriver
    pd = PushDriver(dut, '', dut.clk)
    pop = PopDriver(dut, '', dut.clk, sb)
    
    # Se desactiva el reset tras detectar tres ciclos de reset
    for _ in range(3):
        await RisingEdge(dut.clk)
    dut.reset.value = 0
    await RisingEdge(dut.clk)
    
    # Se generan diez datos aleatorios para la fifo
    test_data = [random.randint(0, 65535) for _ in range(10)]  
    for data in test_data:
        sb.append(data) #Cada uno de estos datos es introducido en el array expected_values del scoreboard
    
    # Push de datos
    for data in test_data:
        await RisingEdge(dut.clk)
        pd.append(data)  
        await RisingEdge(dut.clk)
        
    # Pop de datos 
    for expected in test_data:
        await RisingEdge(dut.clk)
        pop.append(expected)
        

    while int(dut.empty) == 0:
        await RisingEdge(dut.clk)
    
    # Checkeo final
    assert dut.empty.value == 1, "FIFO should be empty after all pops"
    dut._log.info("Test completed successfully")

########### DEFINICIÓN DE DRIVERS ###########

class PushDriver(BusDriver):
    _signals = ['push', 'data_in']

    def __init__(self, dut, name, clk):
        BusDriver.__init__(self, dut, name, clk)
        self.dut = dut
        self.bus.push.value = 0
        self.bus.data_in.value = 0
        self.clk = clk
    
    async def _driver_send(self, value, sync=True):
        self.dut._log.info("PUSH")
        self.bus.data_in.value = value
        self.bus.push.value = 1
        await RisingEdge(self.clk)
        self.bus.push.value = 0
        
        

class PopDriver(BusDriver):
    _signals = ['pop', 'out']

    def __init__(self, dut, name, clk, sb_callback):
        BusDriver.__init__(self, dut, name, clk)
        self.dut = dut
        self.bus.pop.value = 0
        self.bus.out.value = 0
        self.callback = sb_callback
        self.clk = clk
    
    async def _driver_send(self, value, sync=True):
        self.dut._log.info("POP")
        await RisingEdge(self.clk)
        self.bus.pop.value = 1
        await RisingEdge(self.clk)
        self.callback.check(self.bus.out.value.integer)
        self.bus.pop.value = 0
        await RisingEdge(self.clk)
        await NextTimeStep()
        
        
       