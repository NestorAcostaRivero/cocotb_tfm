from pyuvm import uvm_component, uvm_tlm_analysis_fifo, ConfigDB, uvm_get_port, UVMConfigItemNotFound, uvm_root
from pifo_seq_item import PifoSeqItem
import logging

if not uvm_root().logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    uvm_root().logger.addHandler(handler)

uvm_root().logger.setLevel(logging.INFO)


class PifoScoreboard(uvm_component):
    def build_phase(self):
        self.in_fifo = uvm_tlm_analysis_fifo("in_fifo", self)
        self.out_fifo = uvm_tlm_analysis_fifo("out_fifo", self)

    def check_phase(self):
        try:
            self.errors = ConfigDB().get(self, "", "CREATE_ERRORS")
        except UVMConfigItemNotFound:
            self.errors = False

        expected_items = []
        actual_items = []
        passed = True
        
        while self.in_fifo.can_get():
            _, expected = self.in_fifo.try_get()
            expected_items.append(expected)
        

        while self.out_fifo.can_get():
            _, actual = self.out_fifo.try_get()
            actual_items.append(actual)
        
        uvm_root().logger.info(f"[Scoreboard] Expected list: {[ (i.result_rank, i.result_meta) for i in expected_items ]}")
        uvm_root().logger.info(f"[Scoreboard] Actual list:   {[ (i.result_rank, i.result_meta) for i in actual_items ]}")

        for expected, actual in zip(expected_items, actual_items):
            if (expected.meta != actual.result_meta or expected.rank != actual.result_rank):
                uvm_root().logger.error(
                    f"[Scoreboard] MISMATCH → Expected rank={expected.rank}, meta={expected.meta} | Got rank={actual.result_rank}, meta={actual.result_meta}")
                passed = False
            else:
                uvm_root().logger.info(
                    f"[Scoreboard] MATCH → Expected rank={expected.rank}, meta={expected.meta} | Actual rank={actual.result_rank}, meta={actual.result_meta}")

        if not passed:
            assert False, "Scoreboard found mismatches"
