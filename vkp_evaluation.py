"""Kennzahlen, Verdikt-Logik und das Messraster (vorberechnet in vkp_precomputed.json, erzeugt von generate_precomputed.py)."""

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import vkp_algorithm as A
import vkp_constants as C
from vkp_scenario import Instance, mess_seed, quelle_instanz, zufallsinstanz

PRECOMPUTED = Path(__file__).resolve().parent / "vkp_precomputed.json"
SCHLUESSEL_LISTE = tuple(sorted(C.SCHLUESSEL))
REGEL_LISTE = tuple(sorted(C.REGELN))


@dataclass(frozen=True)
class Settings:
    quelle: int = 0
    n_index: int = 0
    seed: int = C.DEFAULT_SEED
    schluessel: int = 1
    regel: int = 0


@dataclass(frozen=True)
class Analysis:
    inst: Instance
    order: tuple          # Teilenummern in der Reihenfolge, in der gepackt wird
    bins: tuple           # Behälter als Tupel von Teilenummern
    count: int
    liefer: int           # Behälterzahl in Lieferreihenfolge mit derselben Regel
    schranke: int
    opt: object           # exaktes Optimum (int) oder None bei mehr als OPT_LIMIT Teilen
    tabelle: tuple        # tabelle[schluessel][regel] = Behälterzahl, 7 x 3
    settings: Settings


def tabelle(inst: Instance) -> tuple:
    """Behälterzahl für jede Kombination aus Schlüssel (Zeile) und Regel (Spalte)."""
    return tuple(tuple(A.anzahl(inst.items, k, r, inst.cap) for r in REGEL_LISTE) for k in SCHLUESSEL_LISTE)


def analyse(s: Settings) -> Analysis:
    inst = quelle_instanz(s.quelle, C.N_WERTE[s.n_index], s.seed)
    order = A.reihenfolge(inst.items, s.schluessel)
    bins = A.pack(inst.items, order, inst.cap, s.regel)
    assert A.container_pruefen(inst.items, bins, inst.cap)
    tab = tabelle(inst)
    return Analysis(inst, tuple(order), tuple(tuple(b) for b in bins), len(bins), tab[0][s.regel], A.schranke(inst.items, inst.cap),
                    A.optimum(inst.items, inst.cap, C.OPT_LIMIT), tab, s)


# ------------------------------------------------------------------------------------------------------------------------------------------
# Verdikte (reine Funktionen: (Art, Text))


def verdict_aktuell(a: Analysis) -> tuple[str, str]:
    """Verdikt zur gewählten Kombination: Behälterzahl gegen die Lieferreihenfolge (gleiche Regel) und gegen das exakte Optimum."""
    s = a.settings
    schluessel = C.SCHLUESSEL_MIT[s.schluessel]
    regel = C.REGEL_KURZ[s.regel]
    if a.opt is None:
        opt_teil = f" Das Optimum ist bei dieser Teilezahl nicht berechnet; die Schranke ist {a.schranke}."
    elif a.count == a.opt:
        opt_teil = f" Das ist das Optimum (die Schranke allein ergäbe {a.schranke})."
    else:
        opt_teil = f" Das Optimum ist **{a.opt}**: {a.count - a.opt} zu viel."
    if s.schluessel == 0:
        return "info", f"In der Lieferreihenfolge mit {regel} brauchen die Teile **{a.count}** Behälter." + opt_teil
    kopf = f"Nach {schluessel} sortiert und mit {regel} gesetzt brauchen die Teile **{a.count}** Behälter, in Lieferreihenfolge {a.liefer}."
    if a.count > a.liefer:
        return "warning", kopf + f" Sortieren schadet hier um {a.count - a.liefer}." + opt_teil
    if a.count < a.liefer:
        return "success", kopf + f" Sortieren spart hier {a.liefer - a.count}." + opt_teil
    return "info", kopf + " Sortieren ändert hier nichts." + opt_teil


def spannen(t: tuple) -> tuple[int, int]:
    """(regel, schluessel) der 7 x 3 Tabelle: größter Unterschied zwischen den Regeln innerhalb einer Zeile; größter Unterschied zwischen den Schlüsseln innerhalb einer Spalte."""
    regel = max(max(z) - min(z) for z in t)
    schluessel = max(max(t[k][r] for k in range(len(t))) - min(t[k][r] for k in range(len(t))) for r in range(len(t[0])))
    return regel, schluessel


def verdict_tabelle(a: Analysis) -> tuple[str, str]:
    """Kernfrage: Was verändert die Behälterzahl mehr, der Schlüssel oder die Regel? Gezählt über die ganze 7 x 3 Tabelle dieser Instanz."""
    regel, schluessel = spannen(a.tabelle)
    teil = (f"Zwischen den drei Regeln unterscheidet sich die Behälterzahl bei gleichem Schlüssel um höchstens **{regel}**; "
            f"zwischen den sieben Schlüsseln bei gleicher Regel um bis zu **{schluessel}**.")
    if schluessel > regel:
        return "success", teil + " Hier zählt der Schlüssel mehr als die Regel."
    if schluessel == regel:
        return "info", teil + " Beide wirken hier gleich stark."
    return "warning", teil + " Hier wirkt die Regel stärker als der Schlüssel."


# ------------------------------------------------------------------------------------------------------------------------------------------
# Messraster


def optima_n12(zusammenhang: int, n_index: int) -> list:
    """Exaktes Optimum jeder Instanz einer Zelle mit höchstens OPT_LIMIT Teilen (Aufzählung aller Teilmengen)."""
    n = C.MESS_N[n_index]
    return [A.optimum(zufallsinstanz(zusammenhang, n, mess_seed(zusammenhang, n_index, j)).items, C.CAP, C.OPT_LIMIT) for j in range(C.INSTANZEN)]


def messzelle(zusammenhang: int, n_index: int, opt: list | None = None) -> dict:
    """Rechnet eine Zelle des Messrasters frisch: Summen (ganze Zahlen, damit der Vergleich exakt ist) über INSTANZEN feste Instanzen.

    ueber_schranke[k][r] = Summe über alle Instanzen von (Behälter mit Schlüssel k und Regel r minus Schranke). Mit `opt` (Optimum je Instanz, -1 = nicht entschieden) zusätzlich,
    nur über die entschiedenen Instanzen: ueber_opt[k] (First Fit, Summe von Behälter minus Optimum), trifft_opt[k] (Zahl der Instanzen mit Behälter gleich Optimum),
    opt_minus_schranke (Summe), opt_ueber_schranke (Zahl der Instanzen mit Optimum über der Schranke), entschieden. besser[k] und schlechter[k]: Zahl der Instanzen,
    in denen First Fit mit Schlüssel k weniger bzw. mehr Behälter braucht als in Lieferreihenfolge."""
    n = C.MESS_N[n_index]
    ks = [str(k) for k in SCHLUESSEL_LISTE]
    out = {"ueber_schranke": {k: {str(r): 0 for r in REGEL_LISTE} for k in ks}, "besser": dict.fromkeys(ks, 0), "schlechter": dict.fromkeys(ks, 0)}
    if opt is not None:
        out.update({"entschieden": 0, "ueber_opt": dict.fromkeys(ks, 0), "trifft_opt": dict.fromkeys(ks, 0), "opt_minus_schranke": 0, "opt_ueber_schranke": 0})
    for j in range(C.INSTANZEN):
        inst = zufallsinstanz(zusammenhang, n, mess_seed(zusammenhang, n_index, j))
        s = A.schranke(inst.items, inst.cap)
        t = tabelle(inst)
        for k in SCHLUESSEL_LISTE:
            for r in REGEL_LISTE:
                out["ueber_schranke"][str(k)][str(r)] += t[k][r] - s
            out["besser"][str(k)] += t[k][0] < t[0][0]
            out["schlechter"][str(k)] += t[k][0] > t[0][0]
        if opt is not None and opt[j] >= 0:
            out["entschieden"] += 1
            out["opt_minus_schranke"] += opt[j] - s
            out["opt_ueber_schranke"] += opt[j] > s
            for k in SCHLUESSEL_LISTE:
                out["ueber_opt"][str(k)] += t[k][0] - opt[j]
                out["trifft_opt"][str(k)] += t[k][0] == opt[j]
    return out


@lru_cache(maxsize=1)
def vorberechnet() -> dict:
    return json.loads(PRECOMPUTED.read_text(encoding="utf-8"))


def zelle_schluessel(zusammenhang: int, n_index: int) -> str:
    return f"{zusammenhang}|{C.MESS_N[n_index]}"


def zeile(zusammenhang: int, n_index: int, daten: dict | None = None) -> dict:
    """Mittelwerte und Anteile einer Zelle aus den vorberechneten Summen."""
    daten = daten or vorberechnet()
    z = daten["zellen"][zelle_schluessel(zusammenhang, n_index)]
    k = daten["instanzen"]
    ks = [str(x) for x in SCHLUESSEL_LISTE]
    exakt = "entschieden" in z
    e = z.get("entschieden", 0)
    return {
        "zusammenhang": zusammenhang,
        "name": C.ZUSAMMENHAENGE[zusammenhang],
        "n": C.MESS_N[n_index],
        "instanzen": k,
        "exakt": exakt,
        "entschieden": e,
        "offen": (k - e) if exakt else 0,
        "mittel_schranke": {int(s): {int(r): v / k for r, v in z["ueber_schranke"][s].items()} for s in ks},
        "mittel_opt": {int(s): (z["ueber_opt"][s] / e if e else None) for s in ks} if exakt else None,
        "anteil_opt": {int(s): (100.0 * z["trifft_opt"][s] / e if e else None) for s in ks} if exakt else None,
        "opt_minus_schranke": (z["opt_minus_schranke"] / e if e else None) if exakt else None,
        "opt_ueber_schranke": z.get("opt_ueber_schranke", 0),
        "besser": {int(s): z["besser"][s] for s in ks},
        "schlechter": {int(s): z["schlechter"][s] for s in ks},
    }


def referenz(z: dict) -> tuple[str, dict]:
    """(Name der Vergleichsbasis, Mittel je Schlüssel für First Fit): das Optimum, wo es für mindestens eine Instanz der Zelle bekannt ist, sonst die Schranke."""
    if z["exakt"] and z["entschieden"]:
        return "dem Optimum", dict(z["mittel_opt"])
    return "der Schranke", {k: z["mittel_schranke"][k][0] for k in z["mittel_schranke"]}


def verdict_messung(z: dict) -> tuple[str, str]:
    """Verdikt zur gewählten Zelle: Sortieren nach nur einem Maß gegen die Lieferreihenfolge, in Behältern über der Vergleichsbasis (auf zwei Stellen gerundet verglichen)."""
    basis, m = referenz(z)
    gerundet = {k: round(v, 2) for k, v in m.items()}
    liste = ", ".join(f"{C.SCHLUESSEL_KURZ[k]} {gerundet[k]:.2f}" for k in SCHLUESSEL_LISTE)
    kopf = f"Für {C.ZUSAMMENHANG_LANG[z['zusammenhang']]} mit n = {z['n']} Teilen liegt First Fit im Mittel so weit über {basis} ({z['entschieden'] if basis == 'dem Optimum' else z['instanzen']} Instanzen): {liste}."
    beste = min(gerundet.values())
    namen = [C.SCHLUESSEL_KURZ[k] for k in SCHLUESSEL_LISTE if gerundet[k] == beste]
    fuss = f" Am besten ist {' und '.join(namen)} mit {beste:.2f}."
    if basis == "dem Optimum" and z["offen"]:
        fuss += f" {z['offen']} von {z['instanzen']} Instanzen sind nicht entschieden und fehlen im Mittel."
    if basis == "der Schranke" and z["zusammenhang"] == 3 and z["n"] >= 20:
        fuss += " Bei gegenläufigen Maßen ist die Schranke ab etwa 20 Teilen locker: Lesen Sie nur die Rangfolge der Schlüssel, nicht den Abstand."
    liefer = gerundet[0]
    ein = [gerundet[k] for k in C.EINZELMASS]
    if all(x > liefer for x in ein):
        return "warning", kopf + " Nach nur einem der beiden Maße zu sortieren ist hier **schlechter als gar nicht zu sortieren**." + fuss
    if all(x < liefer for x in ein):
        return "success", kopf + " Nach nur einem der beiden Maße zu sortieren **hilft** hier gegenüber der Lieferreihenfolge." + fuss
    return "info", kopf + " Nach nur einem Maß zu sortieren ist hier nicht in beiden Fällen besser oder schlechter als die Lieferreihenfolge." + fuss


def spannweiten(z: dict) -> tuple[float, float]:
    """(Regel, Schlüssel) in Behältern über der Schranke, auf zwei Stellen gerundet: größter Unterschied zwischen den drei Regeln bei gleichem Schlüssel; größter Unterschied
    zwischen den sieben Schlüsseln bei gleicher Regel."""
    m = z["mittel_schranke"]
    wert = {k: {r: round(m[k][r], 2) for r in REGEL_LISTE} for k in SCHLUESSEL_LISTE}
    regel = max(max(wert[k].values()) - min(wert[k].values()) for k in SCHLUESSEL_LISTE)
    schluessel = max(max(wert[k][r] for k in SCHLUESSEL_LISTE) - min(wert[k][r] for k in SCHLUESSEL_LISTE) for r in REGEL_LISTE)
    return regel, schluessel


def verdict_regeln(z: dict) -> tuple[str, str]:
    """Verdikt zu Experiment 2: Spannweite zwischen den Regeln gegen Spannweite zwischen den Schlüsseln, in Behältern über der Schranke, auf zwei Stellen gerundet."""
    regel, schluessel = spannweiten(z)
    teil = (f"Für {C.ZUSAMMENHANG_LANG[z['zusammenhang']]} mit n = {z['n']} Teilen unterscheiden sich die drei Regeln bei gleichem Schlüssel um höchstens **{regel:.2f}** Behälter, "
            f"die sieben Schlüssel bei gleicher Regel um bis zu **{schluessel:.2f}**.")
    if schluessel > regel:
        return "success", teil + " Der Schlüssel entscheidet hier mehr als die Regel."
    if schluessel == regel:
        return "info", teil + " Beide wirken hier gleich stark."
    return "warning", teil + " Hier wirkt die Regel stärker als der Schlüssel."


def schranke_zeilen(daten: dict | None = None) -> list:
    """Experiment 3: Optimum minus Schranke für alle Zellen mit Optimum (n = 12 und 20, drei Zusammenhänge)."""
    zeilen = []
    for zus in sorted(C.ZUSAMMENHAENGE):
        for ni, n in enumerate(C.MESS_N):
            if n in C.EXAKT_N:
                z = zeile(zus, ni, daten)
                zeilen.append({"zusammenhang": zus, "n": n, "entschieden": z["entschieden"], "offen": z["offen"], "instanzen": z["instanzen"],
                               "mittel": z["opt_minus_schranke"], "ueber": z["opt_ueber_schranke"]})
    return zeilen


def verdict_schranke(zeilen: list) -> tuple[str, str]:
    """Verdikt zu Experiment 3: in welcher Zeile ist die Schranke am lockersten (größter mittlerer Abstand zum Optimum, auf zwei Stellen gerundet)."""
    gueltig = [z for z in zeilen if z["mittel"] is not None]
    if not gueltig:
        return "info", "Es gibt keine Zelle mit bekanntem Optimum."
    grosse = max(gueltig, key=lambda z: (round(z["mittel"], 2), -z["n"]))
    return "info", (f"Am lockersten ist die Schranke bei {C.ZUSAMMENHANG_DAT[grosse['zusammenhang']]} mit n = {grosse['n']} Teilen: Das Optimum liegt im Mittel um **{grosse['mittel']:.2f}** über ihr "
                    f"und in {grosse['ueber']} von {grosse['entschieden']} entschiedenen Instanzen darüber ({grosse['offen']} von {grosse['instanzen']} nicht entschieden). "
                    "Wo das Optimum fehlt (n = 50 und 200), lässt sich die Lockerheit nicht messen; dort zählt nur die Rangfolge der Schlüssel.")
