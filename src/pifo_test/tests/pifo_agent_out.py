from pyuvm import uvm_component, uvm_root
from pifo_driver import PifoDriverRemove
from pifo_monitor_out import PifoMonitorOut
from pifo_sequencer import PifoSequencer
import logging

if not uvm_root().logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    uvm_root().logger.addHandler(handler)

uvm_root().logger.setLevel(logging.INFO)



class PifoAgentOut(uvm_component):

    def __init__(self, name, parent):
        super().__init__(name, parent)

    def build_phase(self):
        self.driver = PifoDriverRemove("driver", self)
        self.monitor = PifoMonitorOut("monitor_out", self)
        self.sequencer = PifoSequencer("sequencer", self)

    def connect_phase(self):
        # Conectar el driver al sequencer (si es activo)
        self.driver.seq_item_port.connect(self.sequencer.seq_item_export)
        uvm_root().logger.info(f"AgentOut created")
