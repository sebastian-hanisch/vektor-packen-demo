"""Kern an der Mini-Instanz von Hand und am Handbeispiel der App (DEMO-PLAYBOOK §1b).

Handrechnung Mini-Instanz (Kapazität 10 in beiden Maßen; Teile 0: (6, 2), 1: (2, 7), 2: (5, 5), 3: (4, 3), 4: (3, 4); Summe der Volumen 20, der Gewichte 21, Schranke 3):
  First Fit, Lieferreihenfolge:  0 -> B1 (6, 2); 1 -> B1 (8, 9); 2 -> B1 wäre (13, 14), also B2 (5, 5); 3 -> B1 (12) nein, B2 (9, 8); 4 -> B1 (11) nein, B2 (12) nein, B3.
                                 => [[0, 1], [2, 3], [4]]
  nach Volumen (Reihenfolge 0, 2, 3, 4, 1): 0 -> B1 (6, 2); 2 -> B1 (11) nein, B2 (5, 5); 3 -> B1 (10, 5); 4 -> B1 (13) nein, B2 (8, 9); 1 -> B1 (12) nein, B2 (10, 16) nein, B3.
                                 => [[0, 3], [2, 4], [1]]
  nach Gewicht (Reihenfolge 1, 2, 4, 3, 0): 1 -> B1 (2, 7); 2 -> B1 (12) nein, B2 (5, 5); 4 -> B1 (11) nein, B2 (8, 9); 3 -> B1 (6, 10); 0 -> B1 (12) nein, B2 (14) nein, B3.
                                 => [[1, 3], [2, 4], [0]]
  nach der Summe (Summen 8, 9, 10, 7, 7; Reihenfolge 2, 1, 0, 3, 4, wobei 3 vor 4 kommt, weil bei Gleichstand die Lieferreihenfolge bleibt):
                                 2 -> B1 (5, 5); 1 -> B1 (12) nein, B2 (2, 7); 0 -> B1 (11) nein, B2 (8, 9); 3 -> B1 (9, 8); 4 -> B1 (12) nein, B2 (11) nein, B3.
                                 => [[2, 3], [1, 0], [4]]
"""

import pytest

import vkp_algorithm as A
import vkp_constants as C
import vkp_evaluation as ev
from vkp_scenario import handbeispiel


def _ff(inst, schluessel):
    return A.pack(inst.items, A.reihenfolge(inst.items, schluessel), inst.cap, 0)


def test_first_fit_in_lieferreihenfolge_auf_der_mini_instanz(mini):
    assert _ff(mini, 0) == [[0, 1], [2, 3], [4]]


def test_first_fit_nach_volumen_auf_der_mini_instanz(mini):
    assert A.reihenfolge(mini.items, 1) == [0, 2, 3, 4, 1]
    assert _ff(mini, 1) == [[0, 3], [2, 4], [1]]


def test_first_fit_nach_gewicht_auf_der_mini_instanz(mini):
    assert A.reihenfolge(mini.items, 2) == [1, 2, 4, 3, 0]
    assert _ff(mini, 2) == [[1, 3], [2, 4], [0]]


def test_first_fit_nach_der_summe_auf_der_mini_instanz(mini):
    assert A.reihenfolge(mini.items, 4) == [2, 1, 0, 3, 4]
    assert _ff(mini, 4) == [[2, 3], [1, 0], [4]]


def test_weitere_schluessel_auf_der_mini_instanz(mini):
    # Maximum: 6, 7, 5, 4, 4 -> 1, 0, 2, dann 3 und 4 gleich (4): Gleichstand, die Lieferreihenfolge bleibt, also 3 vor 4
    assert A.reihenfolge(mini.items, 3) == [1, 0, 2, 3, 4]
    # Länge²: 40, 53, 50, 25, 25 -> 1, 2, 0, dann 3 vor 4 (Gleichstand, Lieferreihenfolge)
    assert A.reihenfolge(mini.items, 5) == [1, 2, 0, 3, 4]
    # normiert: v * 21 + w * 20 -> 166, 182, 205, 144, 143
    assert A.schluessel_wert(mini.items, 6) == [6 * 21 + 2 * 20, 2 * 21 + 7 * 20, 5 * 21 + 5 * 20, 4 * 21 + 3 * 20, 3 * 21 + 4 * 20]
    assert A.reihenfolge(mini.items, 6) == [2, 1, 0, 3, 4]


def test_schranke_und_optimum_der_mini_instanz(mini):
    assert A.schranke(mini.items, mini.cap) == 3
    assert A.optimum(mini.items, mini.cap) == 3


def test_best_fit_waehlt_den_vollsten_behaelter_nach_der_restsumme():
    # B1 = (5, 3), B2 = (6, 5) (B1 + B2 passt nicht: Volumen 11); das Teil (2, 2) passt in beide. First Fit nimmt B1 (7, 5): Rest 3 + 5 = 8; B2 (8, 7) hätte Rest 2 + 3 = 5.
    items = ((5, 3), (6, 5), (2, 2))
    assert A.pack(items, [0, 1, 2], 10, 0) == [[0, 2], [1]]
    assert A.pack(items, [0, 1, 2], 10, 1) == [[0], [1, 2]]


def test_skalarprodukt_waehlt_nicht_unbedingt_den_vollsten_behaelter():
    # B1 = (9, 1), B2 = (4, 4); das Teil (1, 2) passt in beide. Best Fit: B1 hat Rest 0 + 7 = 7, B2 hat Rest 5 + 4 = 9 -> B1. Skalarprodukt: B1 9*1 + 1*2 = 11, B2 4*1 + 4*2 = 12 -> B2.
    items = ((9, 1), (4, 4), (1, 2))
    assert A.pack(items, [0, 1, 2], 10, 0) == [[0, 2], [1]]
    assert A.pack(items, [0, 1, 2], 10, 1) == [[0, 2], [1]]
    assert A.pack(items, [0, 1, 2], 10, 2) == [[0], [1, 2]]


# --- das Handbeispiel der App (Phase-0-Rechnung, von Hand nachgerechnet) --------------------------------------------------------------------------


def _lasten(inst, bins):
    return [(sum(inst.items[i][0] for i in b), sum(inst.items[i][1] for i in b)) for b in bins]


def test_handbeispiel_summen_und_schranke():
    inst = handbeispiel()
    assert sum(v for v, _ in inst.items) == 329 and sum(w for _, w in inst.items) == 346
    assert A.schranke(inst.items, inst.cap) == 4 and A.optimum(inst.items, inst.cap) == 4


def test_handbeispiel_lieferreihenfolge_vier_behaelter():
    """Von Hand: (22,35)+(23,35) in B1; (24,35) -> B2 (Gewicht sonst 105); (42,13) -> B1 (87, 83); (37,23) -> B2; (22,36) -> B2 (83, 94); (28,30) -> B3; (30,22) -> B3; (24,35) -> B3 (82, 87);
    (49,9), (15,36), (13,37) -> B4 (77, 82)."""
    inst = handbeispiel()
    bins = _ff(inst, 0)
    assert bins == [[0, 1, 3], [2, 4, 5], [6, 7, 8], [9, 10, 11]]
    assert _lasten(inst, bins) == [(87, 83), (83, 94), (82, 87), (77, 82)]


def test_handbeispiel_nach_volumen_sechs_behaelter():
    """Von Hand (Reihenfolge 49, 42, 37, 30, 28, 24, 24, 23, 22 (Teil 0), 22 (Teil 5), 15, 13): B1 (49,9)+(42,13) = (91, 22); B2 (37,23)+(30,22)+(28,30) = (95, 75); B3 (24,35) zweimal = (48, 70);
    (23,35) passt nirgends (Gewicht), B4 (23,35)+(22,35) = (45, 70); (22,36) passt nirgends, B5 (22,36)+(15,36) = (37, 72); (13,37) passt nirgends, B6."""
    inst = handbeispiel()
    bins = _ff(inst, 1)
    assert _lasten(inst, bins) == [(91, 22), (95, 75), (48, 70), (45, 70), (37, 72), (13, 37)]
    assert A.container_pruefen(inst.items, bins, inst.cap)


def test_handbeispiel_alle_schluessel_mit_first_fit():
    inst = handbeispiel()
    assert [A.anzahl(inst.items, k, 0, inst.cap) for k in range(7)] == [4, 6, 5, 5, 4, 5, 4]    # Lieferung, Volumen, Gewicht, Maximum, Summe, Länge, normiert


def test_handbeispiel_nach_der_summe_vier_behaelter():
    """Von Hand (Summen 60, 59, 59, dann 58 für Teil 1, 5, 6, 9 in Lieferreihenfolge, 57, 55, 52, 51, 50): B1 (37,23)+(24,35)+(24,35) = (85, 93); B2 (23,35)+(22,36)+(49,9) = (94, 80);
    B3 (28,30)+(22,35)+(42,13) = (92, 78); B4 (30,22)+(15,36)+(13,37) = (58, 95)."""
    inst = handbeispiel()
    bins = _ff(inst, 4)
    assert len(bins) == 4 and A.container_pruefen(inst.items, bins, inst.cap)
    assert _lasten(inst, bins) == [(85, 93), (94, 80), (92, 78), (58, 95)]


def test_alle_ergebnisse_des_handbeispiels_sind_zulaessige_packungen():
    inst = handbeispiel()
    for k in C.SCHLUESSEL:
        for r in C.REGELN:
            bins = A.pack(inst.items, A.reihenfolge(inst.items, k), inst.cap, r)
            assert A.container_pruefen(inst.items, bins, inst.cap), (k, r)


def test_container_pruefer_erkennt_fehler():
    items = ((6, 2), (5, 5), (4, 3))
    assert A.container_pruefen(items, [[0, 2], [1]], 10)
    assert not A.container_pruefen(items, [[0, 1], [2]], 10)        # Volumen 11 > 10
    assert not A.container_pruefen(((2, 6), (2, 5)), [[0, 1]], 10)  # Gewicht 11 > 10
    assert not A.container_pruefen(items, [[0, 2], [1], [1]], 10)   # Teil 1 doppelt
    assert not A.container_pruefen(items, [[0, 2]], 10)             # Teil 1 fehlt
    assert not A.container_pruefen(items, [[0, 2], [1], []], 10)    # leerer Behälter


@pytest.mark.parametrize("regel", [0, 1, 2])
def test_analyse_stimmt_mit_dem_kern_ueberein(regel):
    a = ev.analyse(ev.Settings(0, 0, 7, 1, regel))
    assert a.count == len(a.bins) == A.anzahl(a.inst.items, 1, regel, a.inst.cap)
    assert a.liefer == A.anzahl(a.inst.items, 0, regel, a.inst.cap)
