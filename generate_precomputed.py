"""Erzeugt vkp_precomputed.json: das Messraster (drei Zusammenhänge der beiden Maße × Teilezahlen 12, 20, 50, 200 × 100 feste Instanzen).

    python generate_precomputed.py            # rechnet alles neu (bei 12 Teilen Aufzählung aller Teilmengen, bei 20 Teilen ein ganzzahliges Programm mit Zeitlimit; etwa 30 bis 60 Minuten)
    python generate_precomputed.py --retry-u  # rechnet nur die bei 20 Teilen nicht entschiedenen Instanzen (Optimum -1) mit dem Zeitlimit der Konstanten noch einmal
    python generate_precomputed.py --keep-opt # behält die gespeicherten Optima (auch die bei 20 Teilen) und rechnet nur die Behälterzahlen neu (nach einer Änderung an Schlüsseln oder Regeln)
    python generate_precomputed.py --check    # rechnet das Schnelle nach (alle Zellen ohne die 20er Optima, dazu die 12er Optima) und vergleicht mit der Datei

Das Optimum bei 12 Teilen kommt aus der Aufzählung aller Teilmengen (`vkp_algorithm.optimum`), bei 20 Teilen aus `scipy.optimize.milp` (`dev/ilp.py`) mit Zeitlimit C.ILP_ZEITLIMIT;
die Zahl der nicht entschiedenen Instanzen hängt von der Rechenzeit ab, die Datei hält den Stand dieses Laufs fest (Optimum -1 = nicht entschieden)."""

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import vkp_algorithm as A
import vkp_constants as C
import vkp_evaluation as ev
from vkp_scenario import mess_seed, zufallsinstanz


def _ilp(args):
    """Ein Optimum per ganzzahligem Programm: (zusammenhang, n_index, j) -> Optimum oder -1."""
    from dev.ilp import optimum_ilp

    zus, ni, j = args
    inst = zufallsinstanz(zus, C.MESS_N[ni], mess_seed(zus, ni, j))
    untergrenze = A.schranke(inst.items, inst.cap)
    obergrenze = min(A.anzahl(inst.items, k, r, inst.cap) for k in ev.SCHLUESSEL_LISTE for r in ev.REGEL_LISTE)
    wert = optimum_ilp(inst.items, inst.cap, obergrenze, untergrenze, C.ILP_ZEITLIMIT)
    return -1 if wert is None else wert


def optima(zus: int, ni: int, pool, alt: list | None = None, behalten: bool = False) -> list:
    """Optimum je Instanz der Zelle (-1 = nicht entschieden). Mit `alt` werden nur die Instanzen mit -1 neu gerechnet."""
    if C.MESS_N[ni] <= C.OPT_LIMIT:
        return ev.optima_n12(zus, ni)
    if behalten:
        return list(alt)
    offene = [j for j in range(C.INSTANZEN) if alt is None or alt[j] < 0]
    neu = dict(zip(offene, pool.map(_ilp, [(zus, ni, j) for j in offene])))
    return [neu.get(j, alt[j] if alt else -1) for j in range(C.INSTANZEN)]


def erzeugen(retry_u: bool = False, behalten: bool = False) -> dict:
    alt = ev.vorberechnet() if (retry_u or behalten) else None
    daten = {"instanzen": C.INSTANZEN, "cap": C.CAP, "ilp_zeitlimit": C.ILP_ZEITLIMIT, "zellen": {}}
    arbeiter = max(1, min(3, (os.cpu_count() or 2) - 1))
    with ProcessPoolExecutor(arbeiter) as pool:
        for zus in sorted(C.ZUSAMMENHAENGE):
            for ni, n in enumerate(C.MESS_N):
                t = time.perf_counter()
                schl = ev.zelle_schluessel(zus, ni)
                if n in C.EXAKT_N:
                    opt = optima(zus, ni, pool, alt["zellen"][schl]["opt"] if alt else None, behalten)
                    zelle = ev.messzelle(zus, ni, opt)
                    zelle["opt"] = opt
                    info = f"entschieden {zelle['entschieden']} von {C.INSTANZEN}"
                else:
                    zelle = ev.messzelle(zus, ni)
                    info = ""
                daten["zellen"][schl] = zelle
                print(f"{schl}: {time.perf_counter() - t:.0f} s  {info}", flush=True)
    return daten


def pruefen() -> int:
    gespeichert = ev.vorberechnet()
    schlecht = 0
    for zus in sorted(C.ZUSAMMENHAENGE):
        for ni, n in enumerate(C.MESS_N):
            schl = ev.zelle_schluessel(zus, ni)
            z = gespeichert["zellen"][schl]
            if n <= C.OPT_LIMIT:
                frisch = ev.messzelle(zus, ni, ev.optima_n12(zus, ni))
                frisch["opt"] = ev.optima_n12(zus, ni)
            elif n in C.EXAKT_N:
                frisch = ev.messzelle(zus, ni, z["opt"])
                frisch["opt"] = z["opt"]
            else:
                frisch = ev.messzelle(zus, ni)
            if frisch != z:
                schlecht += 1
                print("ABWEICHUNG", schl)
    print("gleich" if not schlecht else f"{schlecht} Abweichungen")
    return 1 if schlecht else 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(pruefen())
    daten = erzeugen("--retry-u" in sys.argv, "--keep-opt" in sys.argv)
    ev.PRECOMPUTED.write_text(json.dumps(daten, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("geschrieben:", ev.PRECOMPUTED.name)
