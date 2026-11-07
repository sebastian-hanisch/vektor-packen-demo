"""Verdikte (reine Funktionen in vkp_evaluation.py) an von Hand gesetzten Werten: jede Schwelle und jede Zahl im Text steht hier (DEMO-PLAYBOOK §12).

Die Analysen und Zellen werden von Hand gebaut, nicht aus Seeds gerechnet."""

import pytest

import vkp_constants as C
import vkp_evaluation as ev
from vkp_scenario import Instance


def _analyse(schluessel, regel, count, liefer, schranke, opt, tabelle=None):
    tab = tabelle or tuple(tuple(5 for _ in range(3)) for _ in range(7))
    return ev.Analysis(Instance(((5, 5),), 10), (0,), ((0,),), count, liefer, schranke, opt, tab, ev.Settings(0, 0, 7, schluessel, regel))


# --- verdict_aktuell -----------------------------------------------------------------------------------------------------------------------


def test_aktuell_schadet_ist_eine_warnung_mit_dem_unterschied_und_dem_optimum():
    kind, text = ev.verdict_aktuell(_analyse(1, 0, 6, 4, 4, 4))
    assert kind == "warning"
    assert "Nach dem Volumen sortiert und mit First Fit gesetzt brauchen die Teile **6** Behälter, in Lieferreihenfolge 4." in text
    assert "Sortieren schadet hier um 2." in text and "Das Optimum ist **4**: 2 zu viel." in text


def test_aktuell_spart_ist_ein_erfolg_und_nennt_das_optimum():
    kind, text = ev.verdict_aktuell(_analyse(4, 1, 4, 5, 3, 4))
    assert kind == "success"
    assert "Nach der Summe sortiert und mit Best Fit gesetzt brauchen die Teile **4** Behälter, in Lieferreihenfolge 5." in text
    assert "Sortieren spart hier 1." in text and "Das ist das Optimum (die Schranke allein ergäbe 3)." in text


def test_aktuell_gleich_ist_info():
    kind, text = ev.verdict_aktuell(_analyse(2, 2, 5, 5, 5, 5))
    assert kind == "info" and "Sortieren ändert hier nichts." in text and "Sortieren schadet" not in text and "Sortieren spart" not in text


def test_aktuell_ohne_optimum_nennt_die_schranke():
    kind, text = ev.verdict_aktuell(_analyse(3, 0, 30, 28, 24, None))
    assert kind == "warning" and "Sortieren schadet hier um 2." in text
    assert "Das Optimum ist bei dieser Teilezahl nicht berechnet; die Schranke ist 24." in text


def test_aktuell_lieferreihenfolge_ist_info_ohne_vergleich():
    kind, text = ev.verdict_aktuell(_analyse(0, 0, 4, 4, 4, 4))
    assert kind == "info" and "In der Lieferreihenfolge mit First Fit brauchen die Teile **4** Behälter." in text and "Sortieren schadet" not in text


@pytest.mark.parametrize("schluessel,wort", [(1, "dem Volumen"), (2, "dem Gewicht"), (3, "dem größeren Maß"), (4, "der Summe"), (5, "der Länge"), (6, "der normierten Summe")])
def test_aktuell_nennt_den_schluessel(schluessel, wort):
    assert f"Nach {wort} sortiert" in ev.verdict_aktuell(_analyse(schluessel, 0, 5, 4, 4, 4))[1]


# --- spannen und verdict_tabelle -----------------------------------------------------------------------------------------------------------


def _tab(zeilen):
    return tuple(tuple(z) for z in zeilen)


def test_spannen_regel_und_schluessel():
    t = _tab([(4, 4, 4), (6, 6, 7), (5, 5, 5), (5, 5, 5), (4, 4, 4), (5, 5, 5), (4, 4, 4)])
    assert ev.spannen(t) == (1, 3)       # Regeln: Zeile 2 (6, 6, 7) -> 1; Schlüssel: Spalte 3 (7 gegen 4) -> 3, Spalte 1 (6 gegen 4) -> 2


def test_verdict_tabelle_schluessel_staerker_ist_erfolg():
    t = _tab([(4, 4, 4), (6, 6, 7), (5, 5, 5), (5, 5, 5), (4, 4, 4), (5, 5, 5), (4, 4, 4)])
    kind, text = ev.verdict_tabelle(_analyse(1, 0, 6, 4, 4, 4, t))
    assert kind == "success" and "höchstens **1**" in text and "bis zu **3**" in text and "Hier zählt der Schlüssel mehr als die Regel." in text


def test_verdict_tabelle_gleich_stark_ist_info():
    t = _tab([(4, 4, 5), (4, 4, 4), (4, 4, 4), (4, 4, 4), (4, 4, 4), (4, 4, 4), (4, 4, 4)])
    kind, text = ev.verdict_tabelle(_analyse(1, 0, 4, 4, 4, 4, t))
    assert kind == "info" and "höchstens **1**" in text and "bis zu **1**" in text and "Beide wirken hier gleich stark." in text


def test_verdict_tabelle_regel_staerker_ist_warnung():
    # Die Regel ist nur stärker, wenn eine Zeile weiter streut als jede Spalte.
    t = _tab([(4, 4, 4)] * 7)
    assert ev.spannen(t) == (0, 0)
    # (3, 5, 4) in einer Zeile: Regelspanne 2; in jeder Spalte steht sonst 4: Spaltenspannen 1, 1, 0
    t = _tab([(3, 5, 4), (4, 4, 4), (4, 4, 4), (4, 4, 4), (4, 4, 4), (4, 4, 4), (4, 4, 4)])
    assert ev.spannen(t) == (2, 1)
    kind, text = ev.verdict_tabelle(_analyse(1, 0, 4, 4, 4, 4, t))
    assert kind == "warning" and "höchstens **2**" in text and "bis zu **1**" in text and "Hier wirkt die Regel stärker als der Schlüssel." in text


# --- verdict_messung, referenz -------------------------------------------------------------------------------------------------------------


def _zelle(mittel, zusammenhang=3, n=20, exakt=True, entschieden=100, instanzen=100):
    """mittel: {Schlüssel: Wert} sowohl als Mittel über dem Optimum als auch (First Fit) über der Schranke."""
    m_schr = {k: {0: v, 1: v + 0.5, 2: v + 1.0} for k, v in mittel.items()}
    return {"zusammenhang": zusammenhang, "name": C.ZUSAMMENHAENGE[zusammenhang], "n": n, "instanzen": instanzen, "exakt": exakt, "entschieden": entschieden if exakt else 0,
            "offen": (instanzen - entschieden) if exakt else 0, "mittel_schranke": m_schr, "mittel_opt": dict(mittel) if exakt and entschieden else None,
            "anteil_opt": None, "opt_minus_schranke": None, "opt_ueber_schranke": 0, "besser": dict.fromkeys(mittel, 0), "schlechter": dict.fromkeys(mittel, 0)}


MITTEL_SCHADET = {0: 0.30, 1: 1.03, 2: 1.11, 3: 0.54, 4: 0.19, 5: 0.43, 6: 0.65}
MITTEL_HILFT = {0: 0.80, 1: 0.37, 2: 0.37, 3: 0.30, 4: 0.28, 5: 0.28, 6: 0.28}


def test_referenz_nimmt_das_optimum_wenn_bekannt_sonst_die_schranke():
    basis, m = ev.referenz(_zelle(MITTEL_SCHADET))
    assert basis == "dem Optimum" and m == MITTEL_SCHADET
    basis, m = ev.referenz(_zelle(MITTEL_SCHADET, n=50, exakt=False))
    assert basis == "der Schranke" and m == MITTEL_SCHADET
    basis, m = ev.referenz(_zelle(MITTEL_SCHADET, entschieden=0))
    assert basis == "der Schranke"


def test_messung_schadet_ist_warnung_und_nennt_alle_zahlen_und_den_besten():
    kind, text = ev.verdict_messung(_zelle(MITTEL_SCHADET))
    assert kind == "warning"
    assert "Für gegenläufige Maße mit n = 20 Teilen liegt First Fit im Mittel so weit über dem Optimum (100 Instanzen):" in text
    assert "Lieferung 0.30, Volumen 1.03, Gewicht 1.11, Maximum 0.54, Summe 0.19, Länge 0.43, normiert 0.65." in text
    assert "**schlechter als gar nicht zu sortieren**" in text and "Am besten ist Summe mit 0.19." in text


def test_messung_hilft_ist_erfolg():
    kind, text = ev.verdict_messung(_zelle(MITTEL_HILFT, zusammenhang=2, n=12))
    assert kind == "success" and "Nach nur einem der beiden Maße zu sortieren **hilft** hier" in text
    assert "Am besten ist Summe und Länge und normiert mit 0.28." in text


def test_messung_gemischt_ist_info():
    m = dict(MITTEL_SCHADET)
    m[1] = 0.20            # Volumen besser als Lieferung, Gewicht schlechter
    kind, text = ev.verdict_messung(_zelle(m))
    assert kind == "info" and "nicht in beiden Fällen besser oder schlechter" in text


def test_messung_vergleicht_die_auf_zwei_stellen_gerundeten_werte():
    m = dict(MITTEL_SCHADET)
    m[1] = 0.3004          # angezeigt 0.30, gleich der Lieferung: nicht schlechter
    m[2] = 1.11
    kind, text = ev.verdict_messung(_zelle(m))
    assert kind == "info" and "Volumen 0.30" in text


def test_messung_nennt_nicht_entschiedene_instanzen():
    kind, text = ev.verdict_messung(_zelle(MITTEL_SCHADET, entschieden=96))
    assert "4 von 100 Instanzen sind nicht entschieden und fehlen im Mittel." in text and "(96 Instanzen)" in text


def test_messung_warnt_vor_der_lockeren_schranke_bei_gegenlaeufigen_maßen_ab_zwanzig():
    for n, soll in ((12, False), (20, True), (50, True), (200, True)):
        text = ev.verdict_messung(_zelle(MITTEL_SCHADET, zusammenhang=3, n=n, exakt=False))[1]
        assert ("Lesen Sie nur die Rangfolge der Schlüssel, nicht den Abstand." in text) == soll, n
    text = ev.verdict_messung(_zelle(MITTEL_SCHADET, zusammenhang=1, n=50, exakt=False))[1]
    assert "Rangfolge" not in text and "über der Schranke (100 Instanzen)" in text


# --- verdict_regeln ------------------------------------------------------------------------------------------------------------------------


def test_regeln_schluessel_staerker_ist_erfolg_mit_beiden_spannweiten():
    z = _zelle(MITTEL_SCHADET)                 # Regeln: je Zeile 0, 0,5, 1,0 -> Spanne 1,00; Schlüssel: Spalte 0 von 0,19 bis 1,11 -> 0,92, Spalte 2 ebenso 0,92
    z["mittel_schranke"] = {k: {0: v, 1: v, 2: v + 0.1} for k, v in MITTEL_SCHADET.items()}
    kind, text = ev.verdict_regeln(z)
    assert kind == "success" and "um höchstens **0.10** Behälter" in text and "um bis zu **0.92**" in text and "Der Schlüssel entscheidet hier mehr als die Regel." in text
    assert "gegenläufige Maße mit n = 20 Teilen" in text


def test_regeln_gleich_ist_info():
    z = _zelle({k: 1.0 for k in range(7)})
    z["mittel_schranke"] = {k: {0: 1.0, 1: 1.0, 2: 1.0} for k in range(7)}
    kind, text = ev.verdict_regeln(z)
    assert kind == "info" and "höchstens **0.00**" in text and "bis zu **0.00**" in text and "Beide wirken hier gleich stark." in text


def test_regeln_regel_staerker_ist_warnung():
    z = _zelle({k: 1.0 for k in range(7)})
    z["mittel_schranke"] = {k: {0: 1.0, 1: 1.0, 2: 1.0} for k in range(7)}
    z["mittel_schranke"][3] = {0: 1.0, 1: 2.0, 2: 0.5}      # Regelspanne 1,50; Schlüsselspannen der Spalten: 0, 1,00, 0,50
    kind, text = ev.verdict_regeln(z)
    assert kind == "warning" and "höchstens **1.50**" in text and "bis zu **1.00**" in text and "Hier wirkt die Regel stärker als der Schlüssel." in text


# --- Experiment 3 --------------------------------------------------------------------------------------------------------------------------


def test_schranke_verdikt_nennt_die_lockerste_zeile():
    zeilen = [{"zusammenhang": 1, "n": 12, "entschieden": 100, "offen": 0, "instanzen": 100, "mittel": 0.10, "ueber": 10},
              {"zusammenhang": 3, "n": 20, "entschieden": 97, "offen": 3, "instanzen": 100, "mittel": 0.62, "ueber": 60},
              {"zusammenhang": 3, "n": 12, "entschieden": 100, "offen": 0, "instanzen": 100, "mittel": 0.05, "ueber": 5}]
    kind, text = ev.verdict_schranke(zeilen)
    assert kind == "info"
    assert "Am lockersten ist die Schranke bei gegenläufigen Maßen mit n = 20 Teilen: Das Optimum liegt im Mittel um **0.62** über ihr und in 60 von 97 entschiedenen Instanzen darüber (3 von 100 nicht entschieden)." in text


def test_schranke_verdikt_ohne_optimum():
    kind, text = ev.verdict_schranke([{"zusammenhang": 1, "n": 20, "entschieden": 0, "offen": 100, "instanzen": 100, "mittel": None, "ueber": 0}])
    assert kind == "info" and text == "Es gibt keine Zelle mit bekanntem Optimum."
