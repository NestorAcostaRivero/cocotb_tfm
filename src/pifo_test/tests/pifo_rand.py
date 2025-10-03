import vsc
from vsc import RandState
from pifo_seq_item import PifoSeqItem   # ajusta el import si tu ruta es distinta

@vsc.randobj
class _VscPifoTxn:
    def __init__(self):
        
        self.rank   = vsc.rand_uint16_t()   
        self.meta   = vsc.rand_bit_t(12)   
        self.insert = vsc.rand_bit_t()
        self.remove = vsc.rand_bit_t()
        self.delay  = vsc.rand_uint16_t()

    @vsc.constraint
    def c_ranges(self):
        self.delay <= 10

    @vsc.constraint
    def c_ops(self):
        self.insert.inside(vsc.rangelist(0, 1))
        self.remove.inside(vsc.rangelist(0, 1))
        self.insert != self.remove

    @vsc.constraint
    def c_bias(self):
        # Más inserts que removes (2:1)
        vsc.dist(self.insert, [
            vsc.weight(1, 2),
            vsc.weight(0, 1),
        ])


    def to_item(self, name="it"):
        return PifoSeqItem(
            name=name,
            rank=int(self.rank),
            meta=int(self.meta),
            insert=bool(self.insert),
            remove=bool(self.remove),
            delay=int(self.delay),
            timestamp=None
        )

class PyvscGenerator:
    def __init__(self, seed=None):
        self._txn = _VscPifoTxn()
        if seed is not None:
            rs = RandState.mkFromSeed(int(seed))
            self._txn.set_randstate(rs)

    def next_item(self, name="it"):
        self._txn.randomize()
        return self._txn.to_item(name)
