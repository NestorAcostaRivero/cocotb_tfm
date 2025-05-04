import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly, First
from cocotb.clock import Clock
import random
import logging

class FifoScoreboard:
    def __init__(self):
        self.expected_values = []
        self.log = logging.getLogger("Scoreboard")
    
    def append(self, value):
        self.expected_values.append(value)
        self.log.info(f"Added to scoreboard: {value}")
    
    def check(self, actual_value):
        if not self.expected_values:
            self.log.error("No more expected values!")
            return
            
        expected = self.expected_values.pop(0)
        assert actual_value == expected, f"Scoreboard error: Expected {expected}, got {actual_value}"
        self.log.info(f"Verified: {actual_value} == {expected}")

@cocotb.test()
async def simple_fifo_test(dut):
    # Se prepara el log
    dut._log.setLevel(logging.INFO)
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start()) #corrutina del reloj para que se ejecute concurrentemente con el test
    
    # Inicialización
    dut.reset.value = 1
    dut.push.value = 0
    dut.pop.value = 0
    dut.data_in.value = 0
    
    # Se desactiva el reset tras detectar dos flanso de reloj
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await RisingEdge(dut.clk)
    
    # Instancia del scoreboard
    sb = FifoScoreboard()
    
    # Se generan diez datos aleatorios para la fifo
    test_data = [random.randint(0, 65535) for _ in range(10)]  
    for data in test_data:
        sb.append(data) #Cada uno de estos datos es introducido en el array expected_values del scoreboard
    
    # Push de datos
    for data in test_data:
        dut.data_in.value = data
        dut.push.value = 1
        await RisingEdge(dut.clk)
        dut.push.value = 0
        await RisingEdge(dut.clk)
    
    # Pop y verificación de los datos sacados
    for expected in test_data:
        dut.pop.value = 1
        await RisingEdge(dut.clk)
        sb.check(dut.out.value.integer)
        dut.pop.value = 0
        await RisingEdge(dut.clk)
    
    # Checkeo final
    assert dut.empty.value == 1, "FIFO should be empty after all pops"
    dut._log.info("Test completed successfully")
    await Timer(100, 'ns')  # Small delay to finish