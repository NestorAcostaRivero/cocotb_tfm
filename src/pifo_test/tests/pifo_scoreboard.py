from pyuvm import (
    uvm_component, uvm_tlm_analysis_fifo, ConfigDB, UVMConfigItemNotFound,
    uvm_root
)
from pifo_seq_item import PifoSeqItem
import logging
from pifo_GR import PIFO
from pifo_utils import PifoBfm
from cocotb.triggers import RisingEdge, FallingEdge, Event

if not uvm_root().logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    uvm_root().logger.addHandler(handler)

uvm_root().logger.setLevel(logging.INFO)


class PifoScoreboard(uvm_component):
    def build_phase(self):
        self.pifo = PIFO()
        self.bfm = PifoBfm()
        self.in_pifo = uvm_tlm_analysis_fifo("in_pifo", self)
        self.out_pifo = uvm_tlm_analysis_fifo("out_pifo", self)

    def connect_phase(self):
        try:
            self.errors = ConfigDB().get(self, "", "CREATE_ERRORS")
        except UVMConfigItemNotFound:
            self.errors = False

    async def run_phase(self):
        while True:
            # Esperamos por una transacción de insert o remove (lo que esté listo)
            await self._process_next()

    async def _process_next(self):
        # Esperar hasta que haya algo en cualquiera de las dos FIFOs
        while not (self.in_pifo.can_get() or self.out_pifo.can_get()):
            await FallingEdge(self.bfm.dut.clk)  # Esperar un pequeño tiempo si ambas están vacías

        if self.out_pifo.can_get():
            _, item = self.out_pifo.try_get()
            if item.remove:
                uvm_root().logger.info(
                    f"[Scoreboard] REMOVE @ {item.timestamp}ns rank={item.rank} meta={item.meta}"
                )
                removed_item = self.pifo.remove()
                if removed_item is None:
                    raise AssertionError(
                        f"[Scoreboard ERROR] @{item.timestamp}ns: "
                        f"DUT removed ({item.rank},{item.meta}) pero GR está vacía"
                    )

                rank_exp, meta_exp = removed_item
                if rank_exp != item.rank or meta_exp != item.meta:
                    raise AssertionError(
                        f"[Scoreboard MISMATCH @{item.timestamp}ns] "
                        f"Esperado ({rank_exp}, {meta_exp}) pero DUT dio "
                        f"({item.rank}, {item.meta})"
                    )

                uvm_root().logger.info(
                    f"[Scoreboard MATCH @{item.timestamp}ns] rank={item.rank}, meta={item.meta}"
                )

        if self.in_pifo.can_get():
            _, item = self.in_pifo.try_get()
            if item.insert:
                self.pifo.insert(item.rank, item.meta)
                uvm_root().logger.info(
                    f"[Scoreboard] INSERT @ {item.timestamp}ns rank={item.rank} meta={item.meta}"
                )

        

    def final_phase(self):
        uvm_root().logger.info(
            f"[Scoreboard] Estado final GR: {[(r, m) for r, m in self.pifo]}"
        )