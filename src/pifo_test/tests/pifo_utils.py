import cocotb
from cocotb.triggers import RisingEdge
from cocotb.queue import QueueEmpty, Queue
from cocotb.handle import SimHandleBase
from pyuvm import utility_classes

def get_int(signal: SimHandleBase) -> int:
    try:
        return int(signal.value)
    except ValueError:
        cocotb.log.warning(f"Invalid signal value {signal.value}, defaulting to 0")
        return 0

class PifoBfm(metaclass=utility_classes.Singleton):
    def __init__(self):
        self.dut = cocotb.top
        self.insert_queue = Queue()
        self.remove_queue = Queue()
        self.insert_mon_queue = Queue()
        self.remove_mon_queue = Queue()

    async def reset(self):
        self.dut.rst.value = 1
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 0
        await RisingEdge(self.dut.clk)

    async def insert(self, rank, meta):
        await self.insert_queue.put((rank, meta))

    async def remove(self):
        await self.remove_queue.put(True)

    async def get_inserted(self):
        return await self.insert_mon_queue.get()

    async def get_removed(self):
        return await self.remove_mon_queue.get()

    async def insert_bfm(self):
        while True:
            await RisingEdge(self.dut.clk)
            try:
                if get_int(self.dut.full) == 0:
                    rank, meta = self.insert_queue.get_nowait()
                    self.dut.rank_in.value = rank
                    self.dut.meta_in.value = meta
                    self.dut.insert.value = 1
                    self.insert_mon_queue.put_nowait((rank, meta))
                else:
                    self.dut.insert.value = 0
            except QueueEmpty:
                self.dut.insert.value = 0
            

    async def remove_bfm(self):
        while True:
            await RisingEdge(self.dut.clk)
            try:
                if get_int(self.dut.empty) == 0:
                    _ = self.remove_queue.get_nowait()
                    self.dut.remove.value = 1
                else:
                    self.dut.remove.value = 0
            except QueueEmpty:
                self.dut.remove.value = 0

    async def monitor_bfm(self):
        prev_valid = 0
        while True:
            await RisingEdge(self.dut.clk)
            valid = get_int(self.dut.valid_out)
            if valid and not prev_valid:
                rank = get_int(self.dut.rank_out)
                meta = get_int(self.dut.meta_out)
                self.remove_mon_queue.put_nowait((rank, meta))
            prev_valid = valid

    def start_bfm(self):
        cocotb.start_soon(self.insert_bfm())
        cocotb.start_soon(self.remove_bfm())
        cocotb.start_soon(self.monitor_bfm())
