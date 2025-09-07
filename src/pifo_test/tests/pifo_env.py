from pyuvm import uvm_env, uvm_sequencer, ConfigDB
from pifo_scoreboard import PifoScoreboard
from pifo_agent import PifoAgentIn, PifoAgentOut


class PifoEnv(uvm_env):
    def build_phase(self):
        self.agent_in = PifoAgentIn("agent_in", self)
        self.agent_out = PifoAgentOut("agent_out", self)
        self.scoreboard = PifoScoreboard("scoreboard", self)

    def connect_phase(self):

        # Conectar monitores al scoreboard
        self.agent_in.monitor.ap.connect(self.scoreboard.in_pifo.analysis_export)

        self.agent_out.monitor.ap.connect(self.scoreboard.out_pifo.analysis_export)