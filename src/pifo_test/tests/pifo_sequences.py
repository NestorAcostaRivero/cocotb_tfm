from pyuvm import uvm_sequence, uvm_sequence_item, ConfigDB
import random
from cocotb.triggers import Timer
from pifo_seq_item import PifoSeqItem
import asyncio
import cocotb

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

class RemoveWhenEmpty(uvm_sequence):
    async def body(self):
        remove_seq = PifoRemoveSeq("remove", num_items=1)
        seqr_remove = ConfigDB().get(None, "", "SEQR_REMOVE")
        await remove_seq.start(seqr_remove)

class InsertAndRemoveSameCycleWhenEmpty(uvm_sequence):
    async def body(self):
        insert_seq = PifoInsertSeq("insert", num_items=1)
        remove_seq = PifoRemoveSeq("remove", num_items=1)
        seqr_insert = ConfigDB().get(None, "", "SEQR_INSERT")
        seqr_remove = ConfigDB().get(None, "", "SEQR_REMOVE")

        # Iniciar las secuencias concurrentemente con cocotb
        insert_task = cocotb.start_soon(insert_seq.start(seqr_insert))
        remove_task = cocotb.start_soon(remove_seq.start(seqr_remove))

        # Esperar a que ambas terminen
        await insert_task
        await remove_task

class SingleInsertSeq(uvm_sequence):
    def __init__(self, item, name="SingleInsertSeq"):
        super().__init__(name)
        self.item = item

    async def body(self):
        await self.start_item(self.item)
        await self.finish_item(self.item)

class Write2FullAndMaxPrio(uvm_sequence):
    async def body(self):
        seqr_insert = ConfigDB().get(None, "", "SEQR_INSERT")
        seqr_remove = ConfigDB().get(None, "", "SEQR_REMOVE")

        # Paso 1: llenar el PIFO
        fill_seq = PifoInsertSeq("fill", num_items=16)
        await fill_seq.start(seqr_insert)

        # Paso 2: insertar item de máxima prioridad
        max_prio_item = PifoSeqItem("max_prio_item", rank=0, meta=random.randint(0, 4095), insert=True, remove=False)
        max_prio_seq = SingleInsertSeq(max_prio_item)
        await max_prio_seq.start(seqr_insert)

        # Paso 3: remove
        remove_seq = PifoRemoveSeq("remove", num_items=1)
        await remove_seq.start(seqr_remove)

class Write2FullAndMinPrio(uvm_sequence):
    async def body(self):
        seqr_insert = ConfigDB().get(None, "", "SEQR_INSERT")
        seqr_remove = ConfigDB().get(None, "", "SEQR_REMOVE")

        # Paso 1: llenar el PIFO con 16 elementos aleatorios
        fill_seq = PifoInsertSeq("fill", num_items=16)
        await fill_seq.start(seqr_insert)

        # Paso 2: insertar ítem con la prioridad más baja (rank=255)
        min_prio_item = PifoSeqItem("min_prio_item", rank=255, meta=random.randint(0, 4095), insert=True, remove=False)
        min_prio_seq = SingleInsertSeq(min_prio_item)
        await min_prio_seq.start(seqr_insert)

        # Paso 3: hacer 16 removes 
        remove_seq = PifoRemoveSeq("remove", num_items=16)
        await remove_seq.start(seqr_remove)

class InsertSamePriorityDifferentMeta(uvm_sequence):
    async def body(self):
        seqr_insert = ConfigDB().get(None, "", "SEQR_INSERT")
        seqr_remove = ConfigDB().get(None, "", "SEQR_REMOVE")

        # Paso 1: Insertar 5 ítems aleatorios
        prefill_seq = PifoInsertSeq("prefill", num_items=5)
        await prefill_seq.start(seqr_insert)

        # Paso 2: Insertar dos ítems con mismo rank pero distinto meta
        common_rank = 100  
        meta1 = 123
        meta2 = 456

        item1 = PifoSeqItem("same_rank_item1", rank=common_rank, meta=meta1, insert=True, remove=False)
        item2 = PifoSeqItem("same_rank_item2", rank=common_rank, meta=meta2, insert=True, remove=False)

        await SingleInsertSeq(item1).start(seqr_insert)
        await SingleInsertSeq(item2).start(seqr_insert)

        # Paso 3: Hacer 7 removes
        remove_seq = PifoRemoveSeq("remove", num_items=7)
        await remove_seq.start(seqr_remove)