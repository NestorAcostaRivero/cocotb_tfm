from pyuvm import uvm_driver, ConfigDB
from pifo_seq_item import PifoSeqItem
from pifo_utils import PifoBfm


class PifoDriver(uvm_driver):
    def build_phase(self):
        self.bfm = PifoBfm()
        try:
            self.expected_fifo = ConfigDB().get(self, "", "EXPECTED_FIFO")
        except Exception:
            self.expected_fifo = None

    async def run_phase(self):
        await self.bfm.reset()
        self.bfm.start_bfm()
        while True:
            item = await self.seq_item_port.get_next_item()

            if item.rank is not None and item.meta is not None:
                # Inserción
                await self.bfm.insert(item.rank, item.meta)
                if self.expected_fifo:
                    self.expected_fifo.write(item)
            else:
                # Eliminación
                await self.bfm.remove()

            self.seq_item_port.item_done()