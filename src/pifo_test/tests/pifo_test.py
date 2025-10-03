from pyuvm import uvm_test, ConfigDB, uvm_root
from pifo_env import PifoEnv
from pifo_sequences import InsertRemoveSeq, RemoveWhenEmpty, InsertAndRemoveSameCycleWhenEmpty, Write2FullAndMaxPrio, Write2FullAndMinPrio, InsertSamePriorityDifferentMeta, PifoRandomSeq
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
        self.testPifo = PifoRandomSeq.create("same_prio_diferent_meta")
        self.testPifo.num_txns = 60

        ConfigDB().set(None, "", "SEQR_INSERT", self.env.agent_in.sequencer)
        ConfigDB().set(None, "", "SEQR_REMOVE", self.env.agent_out.sequencer)

        ConfigDB().set(None, "", "USE_PYVSC", True)   # True = usar PyVSC, False = estímulo clásico
        ConfigDB().set(None, "", "PYVSC_SEED", 41)    # fija semilla para reproducibilidad


    async def run_phase(self):

        self.raise_objection() # informa que la prueba sigue en ejecución

        await self.testPifo.start()
        
        self.drop_objection() # dice a pyuvm que puede terminar cuando todo lo demás acabeS