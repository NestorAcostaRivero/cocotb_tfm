from pyuvm import uvm_test, ConfigDB
from pifo_env import PifoEnv
from pifo_seq_item import PifoInsertSeq
import pyuvm
import cocotb
from cocotb.triggers import Timer



@pyuvm.test()
class PifoBasicTest(uvm_test):
    def build_phase(self):
        # Crear entorno de verificación
        self.env = PifoEnv("env", self)

        
        # Crear secuencia de inserción
        self.seq = PifoInsertSeq("insert_seq", num_items=5)

    async def run_phase(self):
        # Registrar el expected_fifo en ConfigDB para el driver
        ConfigDB().set(None, "*", "EXPECTED_FIFO", self.env.scoreboard.expected_fifo)


        self.raise_objection() # informa que la prueba sigue en ejecución
        seqr = ConfigDB().get(None, "", "SEQR")

        await Timer(20, units="ns")  # da tiempo tras el reset

        await self.seq.start(seqr)

        await Timer(100, units="ns")  # espera a que DUT saque la salida

        self.drop_objection() # dice a pyuvm que puede terminar cuando todo lo demás acabe

