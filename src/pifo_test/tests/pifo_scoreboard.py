from pyuvm import uvm_component, uvm_tlm_analysis_fifo, ConfigDB, uvm_get_port, UVMConfigItemNotFound, uvm_root
from pifo_seq_item import PifoSeqItem
import logging
from pifo_GR import PIFO

if not uvm_root().logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    uvm_root().logger.addHandler(handler)

uvm_root().logger.setLevel(logging.INFO)


class PifoScoreboard(uvm_component):
    def build_phase(self):
        self.pifo = PIFO()
        self.in_pifo = uvm_tlm_analysis_fifo("in_pifo", self)
        self.out_pifo = uvm_tlm_analysis_fifo("out_pifo", self)

        
    def check_phase(self):
        try:
            self.errors = ConfigDB().get(self, "", "CREATE_ERRORS")
        except UVMConfigItemNotFound:
            self.errors = False

        transacciones = []
        passed = True
        
        while self.in_pifo.can_get() or self.out_pifo.can_get():
            uvm_root().logger.info(f"in_pifo={self.in_pifo.can_get()}, out_pifo={self.out_pifo.can_get()}")
            if self.in_pifo.can_get(): 
                _, item = self.in_pifo.try_get()
                transacciones.append(item)
                uvm_root().logger.info(f"{item.rank, item.meta, item.insert, item.remove, item.timestamp}")

            if self.out_pifo.can_get():
                _, actual = self.out_pifo.try_get()
                transacciones.append(actual)

        # Ordenar por timestamp (ascendente)
        transacciones.sort(key=lambda x: (x.timestamp, 0 if x.remove else 1))

        
        for t in transacciones:
            if t.insert:
                # INSERT → solo actualiza GR
                uvm_root().logger.info(
                    f"[Scoreboard] INSERT @ {t.timestamp}ns rank={t.rank} meta={t.meta}"
                )
                self.pifo.insert(t.rank, t.meta)

            elif t.remove:
                # REMOVE → validar contra GR
                uvm_root().logger.info(
                    f"[Scoreboard] REMOVE @ {t.timestamp}ns rank={t.rank} meta={t.meta}"
                )

                removed_item = self.pifo.remove()
                if removed_item is None:
                    raise AssertionError(
                        f"[Scoreboard ERROR] @{t.timestamp}ns: DUT removed {t.rank},{t.meta} but GR queue is empty!"
                    )

                rank_expected, meta_expected = removed_item

                # Assert que DUT == GR
                assert rank_expected == t.rank and meta_expected == t.meta, (
                    f"[Scoreboard MISMATCH @{t.timestamp}ns] "
                    f"Expected rank={rank_expected}, meta={meta_expected} "
                    f"but DUT gave rank={t.rank}, meta={t.meta}"
                )

                uvm_root().logger.info(
                    f"[Scoreboard MATCH @{t.timestamp}ns] rank={t.rank}, meta={t.meta}"
                )

        # (opcional) estado final del GR
        uvm_root().logger.info(
            f"[Scoreboard] Estado final GR={[(i[0], i[1]) for i in self.pifo]}"
        )







