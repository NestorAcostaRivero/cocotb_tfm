from pyuvm import uvm_driver, uvm_tlm_analysis_fifo, ConfigDB, uvm_analysis_port, uvm_root
from pifo_seq_item import PifoSeqItem
from pifo_utils import PifoBfm
from cocotb.triggers import RisingEdge, FallingEdge


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
                uvm_root().logger.info(f"[PifoDriver] Insert: rank={item.rank}, meta={item.meta}")
                await self.bfm.insert(item.rank, item.meta)
                await self.bfm.get_inserted()

            else:
                # Eliminación
                await self.bfm.remove()

            self.seq_item_port.item_done()