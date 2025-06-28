from pyuvm import uvm_component, uvm_tlm_analysis_fifo, ConfigDB, uvm_get_port
from pifo_seq_item import PifoSeqItem


class PifoScoreboard(uvm_component):
    def build_phase(self):
        self.expected_fifo = uvm_tlm_analysis_fifo("expected_fifo", self)
        self.actual_fifo = uvm_tlm_analysis_fifo("actual_fifo", self)
        self.expected_get_port = uvm_get_port("expected_get_port", self)
        self.actual_get_port = uvm_get_port("actual_get_port", self)
        self.expected_export = self.expected_fifo.analysis_export
        self.actual_export = self.actual_fifo.analysis_export

    def connect_phase(self):
        self.expected_get_port.connect(self.expected_fifo.get_export)
        self.actual_get_port.connect(self.actual_fifo.get_export)

    async def check_phase(self):
        try:
            self.errors = ConfigDB().get(self, "", "CREATE_ERRORS")
        except UVMConfigItemNotFound:
            self.errors = False

        expected_items = []
        passed = True

        # Recolectamos todos los esperados (inserciones)
        while self.expected_get_port.can_get():
            _, item = self.expected_get_port.try_get()
            expected_items.append(item)

        # Ordenamos por prioridad: menor rank = mayor prioridad
        expected_items.sort(key=lambda item: item.rank)

        # Comparamos contra lo que realmente salió
        for expected in expected_items:
            _, actual = self.actual_get_port.try_get()
            if (expected.meta != actual.result_meta or
                expected.rank != actual.result_rank):
                uvm_root().logger.info("Hola")
                passed = False
            else:
                uvm_root().logger.info("Adiós")

        assert passed, "Scoreboard found mismatches"