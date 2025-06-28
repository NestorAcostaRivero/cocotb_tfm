from pyuvm import uvm_driver, uvm_tlm_analysis_fifo, ConfigDB, uvm_analysis_port
from pifo_seq_item import PifoSeqItem
from pifo_utils import PifoBfm


class PifoDriver(uvm_driver):
    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)
    
    def start_of_simulation_phase(self):
        self.bfm = PifoBfm()

    async def launch_tb(self):
        await self.bfm.reset()
        self.bfm.start_bfm()

    async def run_phase(self):
        await self.launch_tb()
        while True:
            item = await self.seq_item_port.get_next_item()

            if item.rank is not None and item.meta is not None:
                # Inserción
                await self.bfm.insert(item.rank, item.meta)
                if self.ap:
                    self.ap.write(item)
            else:
                # Eliminación
                await self.bfm.remove()

            self.seq_item_port.item_done()