from pyuvm import uvm_sequencer
from pifo_seq_item import PifoSeqItem  

class PifoSequencer(uvm_sequencer):
    def __init__(self, name, parent):
        super().__init__(name, parent)
