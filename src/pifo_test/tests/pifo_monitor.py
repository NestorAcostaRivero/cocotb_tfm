from pyuvm import uvm_component, uvm_analysis_port
from pifo_utils import PifoBfm
from pifo_seq_item import PifoSeqItem


class PifoMonitor(uvm_component):
    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)
        self.bfm = PifoBfm()

    async def run_phase(self):
        while True:
            rank, meta = await self.bfm.get_removed()
            item = PifoSeqItem("monitored_item", rank=None, meta=None)
            item.result_rank = rank
            item.result_meta = meta
            self.logger.debug(f"MONITOR: Captured result rank={rank}, meta={meta}")
            self.ap.write(item)