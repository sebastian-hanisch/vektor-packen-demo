"""Orakel-Tests (DEMO-PLAYBOOK §12): jede Kernroutine gegen einen anderen Rechenweg, feste Seeds, zusammen unter 10 Sekunden.

  Optimum (Mengenpartitions-DP)            gegen  (a) Aufzählung aller Zerlegungen der Teilemenge in Behälter (n <= 7),
                                                  (b) ein ganzzahliges Programm (scipy.optimize.milp, dev/ilp.py; n <= 8).
  Regeln (First Fit, Best Fit, Skalarprodukt) gegen eine bewusst naive Zweitumsetzung (Teile als Listen, Lasten jedes Mal neu summiert).
  Sortierschlüssel                         gegen  eine Zweitumsetzung mit Brüchen (Fraction) für die normierte Summe.
  Eigenschaften:  Behälterzahl >= Optimum >= Schranke (n <= 10); Vertauschen von Volumen und Gewicht; gemeinsames Skalieren; Eingabereihenfolge;
                  bei v = w für alle Teile gleicht die Packung der eindimensionalen (FFD).
"""

import itertools
import random
from fractions import Fraction

import pytest

import vkp_algorithm as A


def instanzen(anzahl, n_lo, n_hi, cap_lo=6, cap_hi=30, seed0=0):
    for seed in range(seed0, seed0 + anzahl):
        rng = random.Random(seed)
        cap = rng.randint(cap_lo, cap_hi)
        n = rng.randint(n_lo, n_hi)
        yield cap, tuple((rng.randint(1, cap), rng.randint(1, cap)) for _ in range(n))


# --- Orakel für das Optimum -------------------------------------------------------------------------------------------------------------------


def optimum_aufzaehlung(items, cap):
    """Kleinste Behälterzahl durch Aufzählung aller Zerlegungen: Teil i kommt in einen vorhandenen Behälter oder in einen neuen."""
    n = len(items)
    if n == 0:
        return 0
    best = n

    def rec(i, lasten):
        nonlocal best
        if len(lasten) >= best:
            return
        if i == n:
            best = len(lasten)
            return
        v, w = items[i]
        for b in range(len(lasten)):
            if lasten[b][0] + v <= cap and lasten[b][1] + w <= cap:
                lasten[b][0] += v
                lasten[b][1] += w
                rec(i + 1, lasten)
                lasten[b][0] -= v
                lasten[b][1] -= w
        lasten.append([v, w])
        rec(i + 1, lasten)
        lasten.pop()

    rec(0, [])
    return best


@pytest.mark.parametrize("cap,items", list(instanzen(40, 1, 7, seed0=0)))
def test_optimum_gegen_aufzaehlung(cap, items):
    assert A.optimum(items, cap) == optimum_aufzaehlung(items, cap)


def test_optimum_gegen_ganzzahliges_programm():
    pytest.importorskip("scipy")
    from dev.ilp import optimum_ilp

    for cap, items in instanzen(8, 5, 8, seed0=100):
        opt = A.optimum(items, cap)
        ober = min(A.anzahl(items, k, 0, cap) for k in range(7))
        unter = A.schranke(items, cap)
        assert optimum_ilp(items, cap, ober, unter, 30.0) == opt, (cap, items)


# --- Orakel für die Regeln ---------------------------------------------------------------------------------------------------------------------


def pack_naiv(items, order, cap, regel):
    """Zweitumsetzung: jeder Behälter ist eine Liste von Teilen; alle Größen werden bei jedem Schritt neu aus den Listen summiert."""
    behaelter = []
    for i in order:
        v, w = items[i]
        kandidaten = []
        for b, liste in enumerate(behaelter):
            lv = sum(items[j][0] for j in liste)
            lw = sum(items[j][1] for j in liste)
            if lv + v <= cap and lw + w <= cap:
                kandidaten.append((b, lv, lw))
        if not kandidaten:
            behaelter.append([i])
            continue
        if regel == 0:
            wahl = min(kandidaten)[0]
        elif regel == 1:
            wahl = min(kandidaten, key=lambda t: ((cap - t[1] - v) + (cap - t[2] - w), t[0]))[0]
        else:
            wahl = min(kandidaten, key=lambda t: (-(t[1] * v + t[2] * w), t[0]))[0]
        behaelter[wahl].append(i)
    return behaelter


@pytest.mark.parametrize("regel", [0, 1, 2])
def test_regeln_gegen_die_naive_zweitumsetzung(regel):
    for cap, items in instanzen(40, 1, 25, cap_lo=10, cap_hi=100, seed0=300):
        for schluessel in (0, 1, 4):
            order = A.reihenfolge(items, schluessel)
            assert A.pack(items, order, cap, regel) == pack_naiv(items, order, cap, regel), (cap, items, schluessel)


def test_normierte_summe_gegen_brueche():
    for cap, items in instanzen(30, 2, 20, cap_lo=10, cap_hi=100, seed0=500):
        sv, sw = sum(v for v, _ in items), sum(w for _, w in items)
        brueche = [Fraction(v, sv) + Fraction(w, sw) for v, w in items]
        ganz = A.schluessel_wert(items, 6)
        n = len(items)
        for i in range(n):
            for j in range(n):
                assert (ganz[i] < ganz[j]) == (brueche[i] < brueche[j]) and (ganz[i] == ganz[j]) == (brueche[i] == brueche[j])


# --- Eigenschaften -----------------------------------------------------------------------------------------------------------------------------


def test_behaelterzahl_nie_unter_optimum_und_optimum_nie_unter_schranke():
    for cap, items in instanzen(60, 1, 10, seed0=700):
        opt = A.optimum(items, cap)
        assert opt >= A.schranke(items, cap)
        for k in range(7):
            for r in range(3):
                assert A.anzahl(items, k, r, cap) >= opt, (cap, items, k, r)


def test_vertauschen_von_volumen_und_gewicht():
    """Schlüssel Volumen und Gewicht tauschen ihre Ergebnisse; Maximum, Summe, Länge und normierte Summe sowie die Schranke bleiben gleich (die Schlüssel sind in beiden Maßen
    symmetrisch, Gleichstände bleiben in der Lieferreihenfolge, die Regeln sind symmetrisch)."""
    tausch = {0: 0, 1: 2, 2: 1, 3: 3, 4: 4, 5: 5, 6: 6}
    for cap, items in instanzen(60, 1, 15, cap_lo=20, cap_hi=200, seed0=900):
        gedreht = tuple((w, v) for v, w in items)
        assert A.schranke(gedreht, cap) == A.schranke(items, cap)
        for k in range(7):
            for r in range(3):
                assert A.anzahl(gedreht, tausch[k], r, cap) == A.anzahl(items, k, r, cap), (cap, items, k, r)


def test_gemeinsames_skalieren_aendert_die_behaelterzahl_nicht():
    for cap, items in instanzen(30, 1, 15, cap_lo=10, cap_hi=40, seed0=1100):
        grosse = tuple((3 * v, 3 * w) for v, w in items)
        for k in range(7):
            for r in range(3):
                assert A.anzahl(grosse, k, r, 3 * cap) == A.anzahl(items, k, r, cap), (cap, items, k, r)
        assert A.optimum(grosse, 3 * cap) == A.optimum(items, cap)


def test_eingabereihenfolge_aendert_die_sortierten_schluessel_ohne_gleichstand_nicht():
    """Ohne Gleichstände im Schlüssel liegt die Reihenfolge fest; die Zerlegung in Behälter (als Menge von Mengen von Teilen) hängt dann nicht von der Eingabereihenfolge ab."""
    rng = random.Random(1300)
    geprueft = 0
    for cap, items in instanzen(60, 2, 15, cap_lo=50, cap_hi=300, seed0=1300):
        gemischt = list(items)
        rng.shuffle(gemischt)
        for k in range(1, 7):
            if len(set(A.schluessel_wert(items, k))) < len(items):
                continue
            geprueft += 1
            for r in range(3):
                a = A.pack(items, A.reihenfolge(items, k), cap, r)
                b = A.pack(tuple(gemischt), A.reihenfolge(tuple(gemischt), k), cap, r)
                assert sorted(sorted(items[i] for i in x) for x in a) == sorted(sorted(gemischt[i] for i in x) for x in b), (cap, items, k, r)
    assert geprueft >= 100            # der Test prüft wirklich etwas


def test_bei_gleichen_maßen_ist_es_das_eindimensionale_ffd():
    """Teile mit v = w: Sortieren nach Volumen mit First Fit ist First Fit Decreasing mit Kapazität cap (unabhängige Zweitumsetzung)."""
    for cap, items in instanzen(30, 1, 25, cap_lo=10, cap_hi=100, seed0=1500):
        groessen = [v for v, _ in items]
        eindim = tuple((g, g) for g in groessen)
        folge = sorted(groessen, reverse=True)
        container = []
        for g in folge:
            for c in container:
                if sum(c) + g <= cap:
                    c.append(g)
                    break
            else:
                container.append([g])
        assert A.anzahl(eindim, 1, 0, cap) == len(container), (cap, groessen)


def test_konstruierte_instanz_zwei_maße_optimum_bekannt():
    """Vier Teile (6, 1), (1, 6), (3, 4), (4, 3) in Kapazität (10, 10): Zerlegung {(6,1),(4,3)} und {(1,6),(3,4)} mit Lasten (10, 4) und (4, 10) ist zulässig, also Optimum 2 (Schranke 2)."""
    items = ((6, 1), (1, 6), (3, 4), (4, 3))
    assert A.optimum(items, 10) == 2 == A.schranke(items, 10)
    assert A.container_pruefen(items, [[0, 3], [1, 2]], 10)
