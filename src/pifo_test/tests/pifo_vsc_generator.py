import random
from pifo_seq_item import PifoSeqItem

class DirectedGenerator:
    def __init__(self, pattern="enqueue-heavy"):
        self.pattern = pattern

    def next_item(self, name="it"):
        if self.pattern == "enqueue-heavy":
            insert = 1; remove = 0
        else:
            insert = random.choice([0,1]); remove = 1-insert

        rank  = random.randint(0, 1000) if insert else 0
        meta  = random.randint(0, 255)
        delay = random.randint(0, 5)
        return PifoSeqItem(name, rank, meta, insert, remove, delay, timestamp=None)
