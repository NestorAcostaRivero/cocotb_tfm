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
        self.expected_fifo = uvm_tlm_analysis_fifo("expected_fifo", self)
        self.actual_fifo = uvm_tlm_analysis_fifo("actual_fifo", self)
        self.expected_get_port = uvm_get_port("expected_get_port", self)
        self.actual_get_port = uvm_get_port("actual_get_port", self)

    def connect_phase(self):
        self.expected_get_port.connect(self.expected_fifo.get_export)
        self.actual_get_port.connect(self.actual_fifo.get_export)

    def check_phase(self):
        try:
            self.errors = ConfigDB().get(self, "", "CREATE_ERRORS")
        except UVMConfigItemNotFound:
            self.errors = False

        expected_items = []
        actual_items = []
        passed = True
        
        while self.expected_get_port.can_get():
            _, expected = self.expected_get_port.try_get()
            expected_items.append(expected)
        

        while self.actual_get_port.can_get():
            _, actual = self.actual_get_port.try_get()
            actual_items.append(actual)
        
        uvm_root().logger.info(f"[Scoreboard] Expected list: {[ (i.rank, i.meta) for i in expected_items ]}")
        uvm_root().logger.info(f"[Scoreboard] Actual list:   {[ (i.result_rank, i.result_meta) for i in actual_items ]}")

        for expected, actual in zip(expected_items, actual_items):
            if (expected.meta != actual.result_meta or expected.rank != actual.result_rank):
                uvm_root().logger.error(
                    f"[Scoreboard] MISMATCH → Expected rank={expected.rank}, meta={expected.meta} | Got rank={actual.result_rank}, meta={actual.result_meta}")
                passed = False
            else:
                uuvm_root().logger.info(
                    f"[Scoreboard] MATCH → Expected rank={expected.rank}, meta={expected.meta} | Actual rank={actual.result_rank}, meta={actual.result_meta}")

        if not passed:
            assert False, "Scoreboard found mismatches"
