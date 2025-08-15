from pyuvm import uvm_test, ConfigDB, uvm_root
from pifo_env import PifoEnv
from pifo_sequences import InsertRemoveSeq, RemoveWhenEmpty, InsertAndRemoveSameCycleWhenEmpty, Write2FullAndMaxPrio, Write2FullAndMinPrio, InsertSamePriorityDifferentMeta
import pyuvm
import cocotb
import logging
from cocotb.triggers import Timer 


if not uvm_root().logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    uvm_root().logger.addHandler(handler)

uvm_root().logger.setLevel(logging.INFO)



@pyuvm.test()
class PifoBasicTest(uvm_test):
    def build_phase(self):
        # Crear entorno de verificación
        self.env = PifoEnv("env", self)
    
    def end_of_elaboration_phase(self):
        # Crear secuencia de inserción
        self.testPifo = InsertSamePriorityDifferentMeta.create("test_seq")
        ConfigDB().set(None, "", "SEQR_INSERT", self.env.agent_in.sequencer)
        ConfigDB().set(None, "", "SEQR_REMOVE", self.env.agent_out.sequencer)

    async def run_phase(self):

        self.raise_objection() # informa que la prueba sigue en ejecución

        await self.testPifo.start()
        
        self.drop_objection() # dice a pyuvm que puede terminar cuando todo lo demás acabeS