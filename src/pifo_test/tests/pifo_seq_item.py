from pyuvm import uvm_sequence, uvm_sequence_item, ConfigDB
import random
from cocotb.triggers import Timer

# Sequence item
class PifoSeqItem(uvm_sequence_item):
    def __init__(self, name, rank=None, meta=None, insert=None, remove=None, delay=None, timestamp=None):
        super().__init__(name)
        self.rank = rank
        self.meta = meta
        self.insert = insert
        self.remove = remove
        self.delay = delay
        self.timestamp = timestamp
    