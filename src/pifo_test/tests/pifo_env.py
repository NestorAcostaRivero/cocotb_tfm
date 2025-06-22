from pyuvm import uvm_env, uvm_sequencer, ConfigDB
from pifo_driver import PifoDriver
from pifo_monitor import PifoMonitor
from pifo_scoreboard import PifoScoreboard


class PifoEnv(uvm_env):
    def build_phase(self):
        # Crear componentes
        self.seqr = uvm_sequencer("seqr", self)
        self.driver = PifoDriver.create("driver", self)
        self.monitor = PifoMonitor("monitor", self)
        self.scoreboard = PifoScoreboard("scoreboard", self)

        # Guardar el sequencer en ConfigDB
        ConfigDB().set(None, "*", "SEQR", self.seqr)
        

    def connect_phase(self):
        # Conexiones del driver al sequencer
        self.driver.seq_item_port.connect(self.seqr.seq_item_export)

        # Conectar monitor al scoreboard
        self.monitor.ap.connect(self.scoreboard.actual_fifo.analysis_export)
