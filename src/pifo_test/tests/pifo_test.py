from pyuvm import uvm_test, ConfigDB
from pifo_env import PifoEnv
from pifo_seq_item import TestPifoInsertSeq
import pyuvm
import cocotb




@pyuvm.test()
class PifoBasicTest(uvm_test):
    def build_phase(self):
        # Crear entorno de verificación
        self.env = PifoEnv("env", self)
    
    def end_of_elaboration_phase(self):
        # Crear secuencia de inserción
        self.testPifoInsert = TestPifoInsertSeq.create("test_insert_seq")

    async def run_phase(self):

        self.raise_objection() # informa que la prueba sigue en ejecución

        await self.testPifoInsert.start()

        self.drop_objection() # dice a pyuvm que puede terminar cuando todo lo demás acabe

