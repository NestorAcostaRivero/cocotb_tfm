from pyuvm import uvm_sequence, uvm_sequence_item, ConfigDB
import random
from cocotb.triggers import Timer
from pifo_seq_item import PifoSeqItem

# Secuencias
class PifoInsertSeq(uvm_sequence):
    def __init__(self, name="PifoInsertSeq", num_items=10):
        super().__init__(name)
        self.num_items = num_items
        
    async def body(self):
        for _ in range(self.num_items):
            rank = random.randint(0, 255)
            meta = random.randint(0, 4095)
            item = PifoSeqItem("insert_item", rank, meta, True, False)

            await self.start_item(item)
            await self.finish_item(item)


class PifoRemoveSeq(uvm_sequence):
    def __init__(self, name="PifoRemoveSeq", num_items=10):
        super().__init__(name)
        self.num_items = num_items

    async def body(self):
        for _ in range(self.num_items):
            item = PifoSeqItem("remove_item")
            item.rank = None  # no importa en este caso
            item.meta = None
            item.insert = False
            item.remove = True
            await self.start_item(item)
            await self.finish_item(item)


class InsertRemoveSeq(uvm_sequence):
    async def body(self):
        insert_seq = PifoInsertSeq("insert", num_items=5)
        remove_seq = PifoRemoveSeq("remove", num_items=5)
        seqr_insert = ConfigDB().get(None, "", "SEQR_INSERT")
        seqr_remove = ConfigDB().get(None, "", "SEQR_REMOVE")
        await insert_seq.start(seqr_insert)
        await remove_seq.start(seqr_remove)


class TestPifoInsertSeq(uvm_sequence):

    async def body(self):
        insert_seq = PifoInsertSeq("insert", num_items=5)
        seqr_insert = ConfigDB().get(None, "", "SEQR_INSERT")
        await insert_seq.start(seqr_insert)
