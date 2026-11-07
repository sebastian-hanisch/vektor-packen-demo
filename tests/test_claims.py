"""Jede Zahl der README und der App-Texte, nachgerechnet (DEMO-PLAYBOOK §4 und §11a).

* Das vorberechnete Raster (vkp_precomputed.json): jede der 12 Zellen frisch gerechnet; die Optima bei 12 Teilen frisch aus der Aufzählung, bei 20 Teilen aus der Datei
  (eine Stichprobe wird mit dem ganzzahligen Programm nachgerechnet).
* Die Befunde der README werden aus denselben Auswertungsfunktionen wie in der App berechnet und als Text in der README gesucht.
* Der Text des Expanders „Annahmen, Grenzen und bekannte Probleme“ steht wörtlich in der README.
Dezimalzahlen stehen in der README mit Komma, in der App mit Punkt."""

import itertools
from pathlib import Path

import pytest

import vkp_algorithm as A
import vkp_constants as C
import vkp_evaluation as ev
from vkp_scenario import mess_seed, zufallsinstanz

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
APP = (ROOT / "app.py").read_text(encoding="utf-8")
ZELLEN = list(itertools.product(sorted(C.ZUSAMMENHAENGE), range(len(C.MESS_N))))


def de(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def alle():
    return {(zus, ni): ev.zeile(zus, ni) for zus, ni in ZELLEN}


def test_raster_hat_alle_zellen_und_die_parameter():
    daten = ev.vorberechnet()
    assert daten["instanzen"] == C.INSTANZEN == 100 and daten["cap"] == C.CAP == 100 and daten["ilp_zeitlimit"] == C.ILP_ZEITLIMIT == 60.0
    assert set(daten["zellen"]) == {ev.zelle_schluessel(zus, ni) for zus, ni in ZELLEN} and len(ZELLEN) == 12
    for (zus, ni), n in ((k, C.MESS_N[k[1]]) for k in ZELLEN):
        z = daten["zellen"][ev.zelle_schluessel(zus, ni)]
        assert ("opt" in z) == (n in C.EXAKT_N)
        if "opt" in z:
            assert len(z["opt"]) == 100


@pytest.mark.parametrize("zus,ni", ZELLEN)
def test_jede_zelle_stimmt_mit_frischer_rechnung(zus, ni):
    gespeichert = ev.vorberechnet()["zellen"][ev.zelle_schluessel(zus, ni)]
    n = C.MESS_N[ni]
    if n <= C.OPT_LIMIT:
        opt = ev.optima_n12(zus, ni)
        assert opt == gespeichert["opt"]
        frisch = ev.messzelle(zus, ni, opt)
        frisch["opt"] = opt
    elif n in C.EXAKT_N:
        frisch = ev.messzelle(zus, ni, gespeichert["opt"])
        frisch["opt"] = gespeichert["opt"]
    else:
        frisch = ev.messzelle(zus, ni)
    assert frisch == gespeichert


STICHPROBE_20 = {1: (42, 58), 2: (0, 1), 3: (58, 2)}     # je zwei Instanzen, die das ganzzahlige Programm schnell entscheidet (bei 1 und 3 mit Optimum über der Schranke)


@pytest.mark.parametrize("zus", sorted(C.ZUSAMMENHAENGE))
def test_stichprobe_der_optima_bei_20_teilen_stimmt_mit_dem_ganzzahligen_programm_ueberein(zus):
    pytest.importorskip("scipy")
    from dev.ilp import optimum_ilp

    ni = C.MESS_N.index(20)
    opt = ev.vorberechnet()["zellen"][ev.zelle_schluessel(zus, ni)]["opt"]
    for j in STICHPROBE_20[zus]:
        inst = zufallsinstanz(zus, 20, mess_seed(zus, ni, j))
        ober = min(A.anzahl(inst.items, k, r, inst.cap) for k in range(7) for r in range(3))
        untergrenze = A.schranke(inst.items, inst.cap)
        assert optimum_ilp(inst.items, inst.cap, ober, untergrenze, 60.0) == opt[j] >= untergrenze, (zus, j)
        if zus != 2:
            assert opt[j] > untergrenze, (zus, j)


# --- Tabellen der README -------------------------------------------------------------------------------------------------------------------


def test_readme_tabellen_geben_jede_zeile_wieder():
    from dev.readme_bauen import tabellen

    for tabelle in tabellen():
        for zeile in tabelle.split("\n"):
            assert zeile in README, zeile


# --- Befunde der README --------------------------------------------------------------------------------------------------------------------


def test_handbeispiel_in_der_readme():
    from vkp_scenario import handbeispiel

    inst = handbeispiel()
    zahlen = [A.anzahl(inst.items, k, 0, inst.cap) for k in range(7)]
    assert zahlen == [4, 6, 5, 5, 4, 5, 4]
    assert "Summe der Volumen 329, der Gewichte 346, Schranke 4, Optimum 4" in README
    assert "in Lieferreihenfolge **4** Behälter, nach dem Volumen **6**, nach dem Gewicht **5**, nach dem Maximum **5**, nach der Summe **4**, nach der Länge **5**, nach der normierten Summe **4**" in README
    assert "braucht als gar nicht zu sortieren" in README and zahlen[1] - zahlen[0] == 2


def test_sortieren_nach_einem_mass_schadet_in_acht_von_zwoelf_zellen():
    art = {k: ev.verdict_messung(z)[0] for k, z in alle().items()}
    schadet = {k for k, a in art.items() if a == "warning"}
    hilft = {k for k, a in art.items() if a == "success"}
    assert len(schadet) == 8 and all(zus in (1, 3) for zus, _ in schadet)
    assert len(hilft) == 4 and all(zus == 2 for zus, _ in hilft) and len(art) == 12
    assert "In **8 von 12** Zellen (alle mit unabhängigen oder gegenläufigen Maßen)" in README and "in den **4** Zellen mit gleichlaufenden Maßen niedriger" in README


def test_optimum_getroffen_bei_gegenlaeufigen_massen():
    z12, z20 = ev.zeile(3, 0), ev.zeile(3, 1)
    assert [round(z12["anteil_opt"][k]) for k in (1, 2, 0, 4)] == [16, 19, 50, 58] and z12["entschieden"] == 100
    assert [round(z20["anteil_opt"][k]) for k in (1, 2, 0, 4)] == [7, 8, 71, 79] and z20["entschieden"] == 98
    assert "nach Volumen in 16 %, nach Gewicht in 19 %, in Lieferreihenfolge in 50 % und nach der Summe in 58 % der 100 Instanzen" in README
    assert "bei 20 Teilen in 7 %, 8 %, 71 % und 79 % der 98 entschiedenen" in README


def test_summe_ist_fast_immer_am_besten_aber_gegenlaeufig_kaum_besser_als_die_lieferung():
    abstaende = []
    for z in alle().values():
        _, m = ev.referenz(z)
        g = {k: round(v, 2) for k, v in m.items()}
        abstaende.append(round(g[4] - min(g.values()), 2))
    assert max(abstaende) == pytest.approx(0.02) and any(a > 0 for a in abstaende)
    assert "höchstens **0,02** über dem besten Schlüssel der Zelle" in README and "ist aber nicht in jeder Zelle der beste" in README
    z = ev.zeile(3, 3)
    assert de(z["mittel_schranke"][4][0]) == "10,58" and de(z["mittel_schranke"][0][0]) == "10,85" and (z["besser"][4], z["schlechter"][4]) == (38, 17)
    assert "mit 10,58 gegen 10,85 nur wenig besser als die Lieferreihenfolge (besser in 38, schlechter in 17 von 100 Instanzen)" in README


def test_regel_gegen_schluessel_in_allen_zellen():
    spannen = {k: ev.spannweiten(z) for k, z in alle().items()}
    assert all(schluessel > regel for regel, schluessel in spannen.values()) and len(spannen) == 12
    assert round(max(r for r, _ in spannen.values()), 2) == 0.93
    assert round(min(s for _, s in spannen.values()), 2) == 0.08 and round(max(s for _, s in spannen.values()), 2) == 10.50
    assert "In allen **12** Zellen ist der Unterschied zwischen den sieben Schlüsseln" in README
    assert "die Regeln unterscheiden sich um höchstens **0,93** Behälter, die Schlüssel um **0,08** bis **10,50**" in README


def test_schranke_ist_nur_bei_gegenlaeufigen_massen_und_20_teilen_locker():
    zeilen = ev.schranke_zeilen()
    assert len(zeilen) == 6
    locker = [r for r in zeilen if (r["zusammenhang"], r["n"]) == (3, 20)][0]
    rest = [r for r in zeilen if r is not locker]
    assert round(max(r["mittel"] for r in rest), 2) == 0.07 and round(locker["mittel"], 2) == 0.63 and (locker["ueber"], locker["entschieden"]) == (62, 98)
    assert "im Mittel höchstens 0,07 über ihr, nur bei gegenläufigen Maßen und 20 Teilen um **0,63** (in 62 von 98 entschiedenen Instanzen darüber)" in README


def test_gleichstaende_bei_gegenlaeufigen_massen():
    ni = C.MESS_N.index(200)
    stabil, volumen = 0, 0
    summen = set()
    for j in range(C.INSTANZEN):
        inst = zufallsinstanz(3, 200, mess_seed(3, ni, j))
        s = A.schranke(inst.items, inst.cap)
        stabil += len(A.pack(inst.items, A.reihenfolge(inst.items, 4), inst.cap, 0)) - s
        volumen += len(A.pack(inst.items, A.reihenfolge(inst.items, 4, "volumen"), inst.cap, 0)) - s
        summen |= {v + w for v, w in inst.items}
    assert de(stabil / 100) == "10,58" and de(volumen / 100) == "12,46"
    assert "brauchen 200 Teile im Schlüssel Summe im Mittel 12,46 statt 10,58 Behälter über der Schranke" in README
    assert "12,46 statt 10,58 Behälter über der Schranke" in APP
    # „fast konstant (50 bis 60)“: über alle gegenläufigen Instanzen des Rasters
    alle_summen = {v + w for ni2, n in enumerate(C.MESS_N) for j in range(C.INSTANZEN) for v, w in zufallsinstanz(3, n, mess_seed(3, ni2, j)).items}
    assert min(alle_summen) == 50 and max(alle_summen) == 60 and "(50 bis 60)" in README


def test_nicht_entschiedene_instanzen_bei_20_teilen():
    offen = {zus: ev.zeile(zus, C.MESS_N.index(20))["offen"] for zus in sorted(C.ZUSAMMENHAENGE)}
    assert offen == {1: 0, 2: 0, 3: 2} and sum(offen.values()) == 2
    assert "**2** von 300 (beide bei gegenläufigen Maßen)" in README


def test_zellen_mit_zwoelf_teilen_sind_alle_entschieden():
    for zus in sorted(C.ZUSAMMENHAENGE):
        assert ev.zeile(zus, 0)["offen"] == 0 and ev.zeile(zus, 0)["entschieden"] == 100


# --- Beispiele und Texte --------------------------------------------------------------------------------------------------------------------


def test_annahmen_text_der_app_steht_woertlich_in_der_readme():
    assert C.ASSUMPTIONS_MARKDOWN in README


def test_zahlen_im_annahmen_text_sind_die_der_konstanten():
    t = C.ASSUMPTIONS_MARKDOWN
    assert f"ganzzahlig, {C.LO} bis {C.HI}" in t and f"Kapazität {C.CAP}" in t and f"{C.INSTANZEN} Instanzen" in t and f"bis {C.OPT_LIMIT} Teile" in t and "bei 20 Teilen" in t


def test_die_grenzen_der_app_nennen_die_zahlen_der_konstanten():
    assert f"Werten von {C.LO} bis {C.HI}" in APP and "Maße gleichverteilt von {C.LO} bis {C.HI}" in APP


def test_readme_nennt_die_zusammenhaenge_wie_der_code():
    assert f"Gewicht ≈ {C.GEGENLAUF_SUMME} − Volumen ± {C.RAUSCHEN}" in README and f"Gewicht = Volumen ± {C.RAUSCHEN}" in README
    assert f"{C.ILP_ZEITLIMIT:.0f} Sekunden Zeitlimit je Instanz" in README
    assert "drei Zusammenhänge × vier Teilezahlen (12, 20, 50, 200) × **100 feste Instanzen**" in README and C.MESS_N == (12, 20, 50, 200)
