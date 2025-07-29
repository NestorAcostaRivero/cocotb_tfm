from pyuvm import uvm_driver, uvm_tlm_analysis_fifo, ConfigDB, uvm_analysis_port, uvm_root
from pifo_seq_item import PifoSeqItem
from pifo_utils import PifoBfm
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb.utils import get_sim_time

# Driver para insertar datos

class PifoDriverInsert(uvm_driver):
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

            # Inserción
            uvm_root().logger.info(f"[Insert Driver] Insert: rank={item.rank}, meta={item.meta}")
            sim_time = get_sim_time(units="ns")
            item.timestamp = sim_time
            await self.bfm.insert(item.rank, item.meta, item.insert, item.remove, item.timestamp)
            self.seq_item_port.item_done()

            await self.bfm.get_driver_insert_signal()

# Driver para hacer un remove

class PifoDriverRemove(uvm_driver):
    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)
    
    def start_of_simulation_phase(self):
        self.bfm = PifoBfm()

    async def launch_tb(self):
        await self.bfm.reset()

    async def run_phase(self):
        await self.launch_tb()
        while True:

            item = await self.seq_item_port.get_next_item()
            uvm_root().logger.info(f"[Remove Driver] Remove: remove={item.remove}")
            sim_time = get_sim_time(units="ns")
            item.timestamp = sim_time
            await self.bfm.remove(item.rank, item.meta, item.insert, item.remove, item.timestamp)
            
            self.seq_item_port.item_done()

            await self.bfm.get_driver_remove_signal()
