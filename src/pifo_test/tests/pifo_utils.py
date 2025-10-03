import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Event
from cocotb.queue import QueueEmpty, Queue
from cocotb.handle import SimHandleBase
from pyuvm import utility_classes, uvm_root



def get_int(signal: SimHandleBase) -> int:
    try:
        return int(signal.value)
    except ValueError:
        cocotb.log.warning(f"Invalid signal value {signal.value}, defaulting to 0")
        return 0

class PifoBfm(metaclass=utility_classes.Singleton): #Solo hay una única instancia
    def __init__(self):
        self.dut = cocotb.top
        self.insert_queue = Queue()
        self.remove_queue = Queue()
        self.in_mon_queue = Queue()
        self.out_mon_queue = Queue()
        self.driver_insert_signal = Queue()
        self.driver_remove_signal = Queue()
        self.advice_insert_remove = Queue()

    async def reset(self):
        await FallingEdge(self.dut.clk)
        self.dut.rst.value = 1
        self.dut.insert.value = 0
        self.dut.remove.value = 0
        self.dut.rank_in.value = 0
        self.dut.meta_in.value = 0
        await FallingEdge(self.dut.clk)
        self.dut.rst.value = 0
        await FallingEdge(self.dut.clk)


    async def insert(self, rank, meta, insert, remove, timestamp):
        await self.insert_queue.put((rank, meta, insert, remove, timestamp))
        

    async def remove(self, rank, meta, insert, remove, timestamp):
        await self.remove_queue.put((rank, meta, insert, remove, timestamp))

    async def get_inserted(self):
        return await self.in_mon_queue.get()

    async def get_out(self):
        return await self.out_mon_queue.get()

    async def get_driver_insert_signal(self):
        return await self.driver_insert_signal.get()

    async def get_driver_remove_signal(self):
        return await self.driver_remove_signal.get()
    
    async def get_advice_insert_remove(self):
        return await self.advice_insert_remove.get()



    async def insert_bfm(self):
        while True:
            await FallingEdge(self.dut.clk)
            try:
                if not self.insert_queue.empty():
                    rank, meta, insert, remove, timestamp = self.insert_queue.get_nowait() # siguiente elemento de la cola sin esperar (no frena el bucle ni bloquea procesos)
                    uvm_root().logger.info(f"[Insert_BFM] Insert: rank={rank}, meta={meta}")
                    self.dut.rank_in.value = rank
                    self.dut.meta_in.value = meta
                    self.dut.insert.value = insert
                    self.in_mon_queue.put_nowait((rank, meta, insert, remove, timestamp))
                    await FallingEdge(self.dut.clk)
                    self.dut.insert.value = 0
                    self.advice_insert_remove.put_nowait((insert)) #Inserto en la cola
                    await FallingEdge(self.dut.clk)
                    self.driver_insert_signal.put_nowait((rank, meta, insert, remove, timestamp))
                    try:
                        self.advice_insert_remove.get_nowait() #Saco de la cola
                    except QueueEmpty:
                        uvm_root().logger.info(f"COLA DE AVISO INSERT Y REMOVE VACIA!!")
            except QueueEmpty:
                uvm_root().logger.info(f"ENTRE EN LA EXEPTION!")
                self.dut.insert.value = 0
            


    async def remove_bfm(self):
        while True:
            await FallingEdge(self.dut.clk)
            try:
                if get_int(self.dut.remove) == 0:
                    
                    rank, meta, insert, remove, timestamp = self.remove_queue.get_nowait()
                    self.dut.remove.value = remove
                    rank = get_int(self.dut.rank_out)
                    meta = get_int(self.dut.meta_out)
                    self.out_mon_queue.put_nowait((rank, meta, insert, remove, timestamp))
                    await FallingEdge(self.dut.clk)
                    self.dut.remove.value = 0
                    await FallingEdge(self.dut.clk)
                    self.driver_remove_signal.put_nowait((rank, meta, insert, remove, timestamp))
                else:
                    self.dut.remove.value = 0
            except QueueEmpty:
                self.dut.remove.value = 0
            


    def start_bfm(self):
        cocotb.start_soon(self.insert_bfm())
        cocotb.start_soon(self.remove_bfm())
