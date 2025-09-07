from pyuvm import uvm_component, uvm_analysis_port, uvm_root
from pifo_utils import PifoBfm
from pifo_seq_item import PifoSeqItem
from cocotb.handle import SimHandleBase


def get_int(signal: SimHandleBase) -> int:
        try:
            return int(signal.value)
        except ValueError:
            cocotb.log.warning(f"Invalid signal value {signal.value}, defaulting to 0")
            return 0


class PifoMonitorIn(uvm_component):
    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)
        self.bfm = PifoBfm()

    async def run_phase(self):
        while True:
            rank, meta, insert, remove, timestamp = await self.bfm.get_inserted()
            item = PifoSeqItem("monitored_item", rank=None, meta=None)
            item.rank = rank
            item.meta = meta
            item.insert = insert
            item.remove = remove
            item.timestamp = timestamp

            uvm_root().logger.info(f"[Monitor_IN] Captured result rank={rank}, meta={meta}")
            self.ap.write(item) 



class PifoMonitorOut(uvm_component):
    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)
        self.bfm = PifoBfm()

    async def run_phase(self):
        while True:
            rank, meta, insert, remove, timestamp = await self.bfm.get_out()
            if(get_int(self.bfm.dut.valid_out) == 1 and remove):
                item = PifoSeqItem("monitored_item", rank=None, meta=None)
                item.rank = rank
                item.meta = meta
                item.insert = False
                item.remove = True
                item.timestamp = timestamp
                uvm_root().logger.info(f"[Monitor_OUT] Captured result rank={item.rank}, meta={item.meta}, insert={item.insert}, remove={item.remove}")
                self.ap.write(item) 