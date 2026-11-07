"""Ganzzahliges Programm (scipy.optimize.milp) für das exakte Optimum bei 20 Teilen: nur für Generator und Tests, nie für die App.

Zuordnungsmodell: x[i, b] = 1, wenn Teil i in Behälter b liegt; y[b] = 1, wenn Behälter b benutzt wird; Behälter werden der Reihe nach benutzt (y[b] >= y[b+1])."""


def optimum_ilp(items, cap: int, obergrenze: int, untergrenze: int, zeitlimit: float):
    """Kleinste Behälterzahl zwischen Untergrenze und Obergrenze (Obergrenze = eine gefundene Packung); None, wenn das Zeitlimit erreicht wird, ohne dass das Optimum bewiesen ist."""
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, milp

    if obergrenze == untergrenze:
        return obergrenze
    n, B = len(items), obergrenze
    nv = n * B + B
    c = np.zeros(nv)
    c[n * B:] = 1
    zeilen, lo, hi = [], [], []
    for i in range(n):
        r = np.zeros(nv)
        r[i * B:(i + 1) * B] = 1
        zeilen.append(r)
        lo.append(1)
        hi.append(1)
    for dim in (0, 1):
        for b in range(B):
            r = np.zeros(nv)
            for i in range(n):
                r[i * B + b] = items[i][dim]
            r[n * B + b] = -cap
            zeilen.append(r)
            lo.append(-np.inf)
            hi.append(0)
    for b in range(B - 1):
        r = np.zeros(nv)
        r[n * B + b] = -1
        r[n * B + b + 1] = 1
        zeilen.append(r)
        lo.append(-np.inf)
        hi.append(0)
    res = milp(c, constraints=LinearConstraint(np.array(zeilen), lo, hi), integrality=np.ones(nv), bounds=Bounds(0, 1), options={"time_limit": zeitlimit})
    if res.status != 0 or res.x is None:
        return None
    return int(round(res.fun))
