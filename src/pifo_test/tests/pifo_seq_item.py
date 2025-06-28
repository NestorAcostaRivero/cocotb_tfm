from pyuvm import uvm_sequence, uvm_sequence_item, ConfigDB
import random

# Sequence item
class PifoSeqItem(uvm_sequence_item):
    def __init__(self, name, rank=None, meta=None):
        super().__init__(name)
        self.rank = rank
        self.meta = meta
        self.result_rank = None
        self.result_meta = None

# Secuencias
class PifoInsertSeq(uvm_sequence):
    def __init__(self, name="PifoInsertSeq", num_items=10):
        super().__init__(name)
        self.num_items = num_items
        
    async def body(self):
        for _ in range(self.num_items):
            rank = random.randint(0, 255)
            meta = random.randint(0, 4095)
            item = PifoSeqItem("insert_item", rank, meta)

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
            await self.start_item(item)
            await self.finish_item(item)

# Tests

class PifoFullTestSeq(uvm_sequence):
    async def body(self):
        insert_seq = PifoInsertSeq("insert", num_items=5)
        remove_seq = PifoRemoveSeq("remove", num_items=5)
        seqr = ConfigDB().get(None, "", "SEQR")
        await insert_seq.start(seqr)
        await remove_seq.start(seqr)


class TestPifoInsertSeq(uvm_sequence):

    async def body(self):
        insert_seq = PifoInsertSeq("insert", num_items=5)
        seqr = ConfigDB().get(None, "", "SEQR")
        await insert_seq.start(seqr)