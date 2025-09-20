# pifo_cov_vsc.py
import vsc

class PifoCovVSC:
    def __init__(self):
        # Variables muestreadas y categorías derivadas
        self._op    = 0   # 1 = insert, 0 = remove
        self._rank  = 0   # valor crudo (16-bit)
        self._meta  = 0   # valor crudo (12-bit)
        self._rcls  = 0   # rank class: 0/1/2
        self._mcls  = 0   # meta class: 0/1/2/3

        # Helpers de categorización (evita bins por rango nativos)
        def rank_class():
            r = int(self._rank)
            if r <= 255:         # low
                return 0
            elif r <= 4095:      # mid
                return 1
            else:                # hi
                return 2

        def meta_class():
            m = int(self._meta)
            if m <= 255:         # q0
                return 0
            elif m <= 1023:      # q1
                return 1
            elif m <= 2047:      # q2
                return 2
            else:                # q3 (hasta 4095)
                return 3

        @vsc.covergroup
        class _Cg(object):
            def __init__(self, parent: "PifoCovVSC"):
                # Coverpoint: operación (0/1)
                self.cp_op = vsc.coverpoint(
                    lambda: parent._op,
                    bins=dict(
                        rem=vsc.bin(0),
                        ins=vsc.bin(1),
                    )
                )

                # Coverpoint: clase de rank (0/1/2)
                self.cp_rcls = vsc.coverpoint(
                    lambda: parent._rcls,
                    bins=dict(
                        low=vsc.bin(0),
                        mid=vsc.bin(1),
                        hi=vsc.bin(2),
                    )
                )

                # Coverpoint: clase de meta (0/1/2/3)
                self.cp_mcls = vsc.coverpoint(
                    lambda: parent._mcls,
                    bins=dict(
                        q0=vsc.bin(0),
                        q1=vsc.bin(1),
                        q2=vsc.bin(2),
                        q3=vsc.bin(3),
                    )
                )

                # Cross: op × clase de rank (pasa como lista)
                self.cr_op_rcls = vsc.cross([self.cp_op, self.cp_rcls])

                # (opcional) otro cross:
                # self.cr_op_rcls_mcls = vsc.cross([self.cp_op, self.cp_rcls, self.cp_mcls])

        self._rank_class_fn = rank_class
        self._meta_class_fn = meta_class
        self.cg = _Cg(self)

    def sample_item(self, it):
        """Llamar una vez por transacción generada (warm-up y bucle principal)."""
        self._op   = 1 if it.insert else 0
        self._rank = int(it.rank or 0)
        self._meta = int(it.meta or 0)
        # Actualiza categorías derivadas
        self._rcls = int(self._rank_class_fn())
        self._mcls = int(self._meta_class_fn())
        # Muestra
        self.cg.sample()

    def report(self):
        """Imprime un resumen de cobertura (si la API lo soporta)."""
        try:
            pct = self.cg.get_coverage()
            print(f"[COVERAGE] PyVSC total: {pct:.1f}%")
        except Exception:
            print("[COVERAGE] PyVSC: muestreado (porcentaje no disponible en esta versión).")
