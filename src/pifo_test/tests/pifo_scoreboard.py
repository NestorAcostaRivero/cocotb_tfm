from pyuvm import uvm_component, uvm_tlm_analysis_fifo, ConfigDB
from pifo_seq_item import PifoSeqItem


class PifoScoreboard(uvm_component):
    def build_phase(self):
        self.expected_fifo = uvm_tlm_analysis_fifo("expected_fifo", self)
        self.actual_fifo = uvm_tlm_analysis_fifo("actual_fifo", self)

    async def run_phase(self):
        try:
            self.errors = ConfigDB().get(self, "", "CREATE_ERRORS")
        except Exception:
            self.errors = False

        expected_items = []
        passed = True

        # Recolectamos todos los esperados (inserciones)
        while self.expected_fifo.can_get():
            _, item = self.expected_fifo.try_get()
            expected_items.append(item)

        # Ordenamos por prioridad: menor rank = mayor prioridad
        expected_items.sort(key=lambda item: item.rank)

        # Comparamos contra lo que realmente salió
        for expected in expected_items:
            _, actual = self.actual_fifo.try_get()
            if (expected.meta != actual.result_meta or
                expected.rank != actual.result_rank):
                self.logger.error(f"FAILED: Expected meta={expected.meta}, "
                                  f"rank={expected.rank} | Got meta={actual.result_meta}, "
                                  f"rank={actual.result_rank}")
                passed = False
            else:
                self.logger.info(f"PASSED: meta={actual.result_meta}, rank={actual.result_rank}")

        assert passed, "Scoreboard found mismatches"