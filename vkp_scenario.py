"""Instanzen: das Handbeispiel und Zufallsinstanzen für App und Messraster."""

import random
from dataclasses import dataclass

import vkp_constants as C


@dataclass(frozen=True)
class Instance:
    items: tuple          # Teile als (Volumen, Gewicht) in Lieferreihenfolge, ganzzahlig und positiv
    cap: int = C.CAP      # Kapazität eines Behälters in jedem der beiden Maße

    def __post_init__(self):
        if self.cap <= 0:
            raise ValueError("Kapazität muss positiv sein")
        for t in self.items:
            if len(t) != 2 or any((not isinstance(x, int)) or x <= 0 or x > self.cap for x in t):
                raise ValueError(f"Teil {t!r} ungültig (zwei ganze Maße, je 1 bis {self.cap})")

    @property
    def n(self) -> int:
        return len(self.items)


def handbeispiel() -> Instance:
    return Instance(tuple(C.HANDBEISPIEL), C.CAP)


def mess_seed(zusammenhang: int, n_index: int, j: int) -> int:
    """Fester Seed der j-ten Instanz einer Zelle des Messrasters (Zusammenhang 1 bis 3, Index der Teilezahl); stabil über Läufe und Rechner."""
    return 1_000_000 * zusammenhang + 1_000 * (n_index + 1) + j


def zufallsinstanz(zusammenhang: int, n: int, seed: int, cap: int = C.CAP) -> Instance:
    """n Teile. Das Volumen ist gleichverteilt (ganzzahlig, LO bis HI). Das Gewicht ist je nach Zusammenhang
    1 unabhängig gleichverteilt, 2 gleich dem Volumen plus eine Abweichung von höchstens RAUSCHEN, 3 gleich GEGENLAUF_SUMME minus Volumen plus eine Abweichung von höchstens RAUSCHEN,
    jeweils auf LO bis HI begrenzt."""
    if zusammenhang not in C.ZUSAMMENHAENGE:
        raise ValueError(f"Zusammenhang {zusammenhang!r} unbekannt")
    rng = random.Random(seed)
    items = []
    for _ in range(n):
        v = rng.randint(C.LO, C.HI)
        if zusammenhang == 1:
            w = rng.randint(C.LO, C.HI)
        elif zusammenhang == 2:
            w = min(C.HI, max(C.LO, v + rng.randint(-C.RAUSCHEN, C.RAUSCHEN)))
        else:
            w = min(C.HI, max(C.LO, C.GEGENLAUF_SUMME - v + rng.randint(-C.RAUSCHEN, C.RAUSCHEN)))
        items.append((v, w))
    return Instance(tuple(items), cap)


def quelle_instanz(quelle: int, n: int, seed: int) -> Instance:
    """Instanz der App: Quelle 0 = Handbeispiel (n und seed ohne Wirkung), 1 bis 3 = Zufallsinstanz."""
    if quelle == 0:
        return handbeispiel()
    return zufallsinstanz(quelle, n, seed)
