"""Packen: zwei Grenzen, Volumen und Gewicht - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 14 der Reihe „Packen: Reihenfolge und Platzierungsregel“. Jedes Teil hat zwei Maße und der Behälter zwei Grenzen: Wonach sortiert man dann?
Das Messraster (vorberechnet in vkp_precomputed.json) zeigt die Antwort an je 100 Zufallsinstanzen.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import vkp_constants as C
from vkp_evaluation import (
    REGEL_LISTE,
    SCHLUESSEL_LISTE,
    Settings,
    analyse,
    referenz,
    schranke_zeilen,
    verdict_aktuell,
    verdict_messung,
    verdict_regeln,
    verdict_schranke,
    verdict_tabelle,
    zeile,
)
from vkp_layout import dunkles_design, kopf_css
from vkp_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from vkp_visualization import build_behaelter, build_messung, build_punktwolke

st.set_page_config(page_title="Packen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in vkp_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧩 Zwei Grenzen: Volumen und Gewicht")
st.markdown(
    """
Jedes Teil hat zwei Maße, **Volumen** und **Gewicht**, und jeder Behälter hat für beide eine Grenze. Wer nur eine Größe kennt, sortiert „das größte zuerst“. Bei zwei Maßen gibt es dieses „größte“ nicht mehr: Man muss erst aus den beiden Zahlen **einen Sortierschlüssel** machen. Die Demo zeigt an zwölf Teilen und an einem Messraster aus je 100 Zufallsinstanzen, wie viel an dieser Wahl hängt und wie viel an der Regel, in welchen Behälter ein Teil kommt.

Weiter unten: der Abschnitt **🔬 Experimente**, **🚧 Wo die Annahmen enden**, der Expander **⚠️ Annahmen, Grenzen und bekannte Probleme** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert Packen mit zwei Grenzen", expanded=True):
    st.markdown(
        """
1. **Schlüssel wählen:** Aus Volumen und Gewicht eines Teils wird eine Sortierzahl, etwa nur das Volumen, nur das Gewicht, das größere der beiden, die Summe. Die Teile werden nach ihr absteigend gepackt, oder in der Lieferreihenfolge, wenn nicht sortiert wird.
2. **Regel anwenden, Teil für Teil:** *First Fit* nimmt den ersten Behälter, in dem das Teil in **beiden** Maßen noch Platz hat; *Best Fit* den passenden Behälter, in dem danach die Summe der freien Reste am kleinsten ist; *Skalarprodukt* den passenden Behälter mit dem größten Wert „Last mal Last“ in beiden Maßen. Passt das Teil nirgends hin, wird ein neuer Behälter geöffnet.
3. **Wo die Wirkung sitzt:** Das Kästchen *Kernfrage* unten zählt, was die Behälterzahl mehr verändert, der Schlüssel oder die Regel.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Teile**")
    quelle = st.selectbox("Instanz", list(C.QUELLEN), format_func=C.QUELLEN.get, key="quelle_select",
                          help="Das Handbeispiel hat zwölf feste Teile. Die anderen drei sind Zufallsinstanzen; sie unterscheiden sich im Zusammenhang der beiden Maße.")
    n_index = st.selectbox("Zahl der Teile (nur Zufallsinstanzen)", list(range(len(C.N_WERTE))), format_func=lambda i: str(C.N_WERTE[i]), key="n_select",
                           help="Bis 12 Teile wird das Optimum exakt berechnet.")
    seed = st.number_input("Startzahl der Zufallsinstanz", *bounds("seed_input"), key="seed_input", step=1,
                           help="Wirkt nur bei den Zufallsinstanzen.")
    st.button("🎲 Neue Zufallsinstanz würfeln", width="stretch", on_click=randomize_seed)
    st.markdown("**Packen**")
    schluessel = st.selectbox("Sortierschlüssel", list(C.SCHLUESSEL), format_func=C.SCHLUESSEL.get, key="schluessel_select",
                              help="Wonach die Teile sortiert werden, absteigend. „Lieferreihenfolge“ sortiert nicht.")
    regel = st.selectbox("Regel: in welchen Behälter?", list(C.REGELN), format_func=C.REGELN.get, key="regel_select",
                         help="Wohin das nächste Teil kommt.")

sync_query_params({"quelle_select": int(quelle), "n_select": int(n_index), "seed_input": int(seed), "schluessel_select": int(schluessel), "regel_select": int(regel)})

settings = Settings(int(quelle), int(n_index), int(seed), int(schluessel), int(regel))
a = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3 = st.columns(3)
# Delta immer als „mein Wert minus Referenz“; die Farbe regelt delta_color="inverse" (Vorzeichen-Falle, DEMO-PLAYBOOK §2).
if a.opt is not None:
    m1.metric("Behälter (gewählte Kombination)", a.count, delta=a.count - a.opt, delta_color="inverse", help="Delta: gewählte Behälterzahl minus Optimum.")
    m2.metric("Optimum (exakt berechnet)", a.opt, delta="Referenz", delta_color="off")
else:
    m1.metric("Behälter (gewählte Kombination)", a.count)
    m2.metric("Optimum", "nicht berechnet", delta="mehr als %d Teile" % C.OPT_LIMIT, delta_color="off")
m3.metric("Untere Schranke", a.schranke, delta="das Größere der beiden Summen durch die Kapazität, aufgerundet", delta_color="off")
sv, sw = sum(v for v, _ in a.inst.items), sum(w for _, w in a.inst.items)
st.caption(f"{a.inst.n} Teile, Summe der Volumen {sv}, Summe der Gewichte {sw}, Kapazität {a.inst.cap} in jedem Maß. In Lieferreihenfolge brauchen sie mit der gewählten Regel {a.liefer} Behälter.")
st.markdown("**So liegen die Teile:** Volumen gegen Gewicht, die Farbe zeigt den Behälter.")
st.plotly_chart(build_punktwolke(a.inst.items, a.bins), width="stretch", key="wolke_chart")
st.markdown("**So voll sind die Behälter:** je Behälter die Last an Volumen und an Gewicht.")
st.plotly_chart(build_behaelter(a.inst.items, a.bins, a.inst.cap), width="stretch", key="main_chart")
st.caption("Grün: Last an Volumen, ocker: Last an Gewicht, rot gestrichelt: Kapazität. Ein Behälter ist voll, sobald **eines** der beiden Maße die Linie erreicht.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Was verändert die Behälterzahl mehr, der Sortierschlüssel oder die Regel?")
kind, text = verdict_aktuell(a)
getattr(st, kind)(text)

zeilen = ["| Schlüssel \\ Regel | " + " | ".join(C.REGEL_KURZ[r] for r in REGEL_LISTE) + " |", "|---|" + "---|" * len(REGEL_LISTE)]
for k in SCHLUESSEL_LISTE:
    zellen = []
    for r in REGEL_LISTE:
        wert = str(a.tabelle[k][r])
        zellen.append(f"**{wert}**" if (k, r) == (settings.schluessel, settings.regel) else wert)
    zeilen.append(f"| {C.SCHLUESSEL_KURZ[k]} | " + " | ".join(zellen) + " |")
st.markdown("Behälterzahl für alle 21 Kombinationen (die gewählte ist fett):\n\n" + "\n".join(zeilen))
kind, text = verdict_tabelle(a)
getattr(st, kind)(text)

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experimente: Gilt das für viele Instanzen?")
st.caption(
    f"Gemessen an je {C.INSTANZEN} festen Zufallsinstanzen pro Zelle, Kapazität {C.CAP} in beiden Maßen, Maße gleichverteilt von {C.LO} bis {C.HI}. "
    "Die Zahlen sind vorberechnet (`generate_precomputed.py`)."
)
e1, e2 = st.columns(2)
zus = e1.selectbox("Zusammenhang der Maße", sorted(C.ZUSAMMENHAENGE), index=2, format_func=C.ZUSAMMENHANG_LANG.get, key="exp_zus")
ni = e2.selectbox("Zahl der Teile n", list(range(len(C.MESS_N))), index=1, format_func=lambda i: str(C.MESS_N[i]), key="exp_n")
z = zeile(int(zus), int(ni))

st.markdown("### Experiment 1: Wonach sortiert man?")
basis, mittel = referenz(z)
st.plotly_chart(build_messung(mittel, f"Behälter über {basis} (Mittel, First Fit)"), width="stretch", key="exp_chart")
if z["exakt"]:
    tab = ["| Schlüssel | Über | Treffer | schlechter / besser |", "|---|---|---|---|"]
else:
    tab = ["| Schlüssel | Über | schlechter / besser |", "|---|---|---|"]
for k in SCHLUESSEL_LISTE:
    rest = f"{z['schlechter'][k]} / {z['besser'][k]}"
    if z["exakt"]:
        treff = "-" if z["anteil_opt"][k] is None else f"{z['anteil_opt'][k]:.0f} %"
        tab.append(f"| {C.SCHLUESSEL_KURZ[k]} | {mittel[k]:.2f} | {treff} | {rest} |")
    else:
        tab.append(f"| {C.SCHLUESSEL_KURZ[k]} | {mittel[k]:.2f} | {rest} |")
st.markdown("\n".join(tab))
st.caption(
    "First Fit mit dem jeweiligen Schlüssel; die roten Balken sind die Schlüssel mit nur einem Maß. „Über“: Mittel der Behälter über " + basis + ", über die Instanzen der Zelle (bei Zellen mit Optimum nur die entschiedenen). "
    "„Treffer“: Anteil der entschiedenen Instanzen, in denen die Behälterzahl gleich dem Optimum ist. „Schlechter / besser“: Zahl der Instanzen von " + str(z["instanzen"]) + ", in denen der Schlüssel mehr bzw. weniger Behälter braucht als die Lieferreihenfolge."
)
kind, text = verdict_messung(z)
getattr(st, kind)(text)

st.markdown("### Experiment 2: Zählt die Regel oder der Schlüssel mehr?")
m = z["mittel_schranke"]
tab2 = ["| Schlüssel | " + " | ".join(C.REGEL_KURZ[r] for r in REGEL_LISTE) + " |", "|---|" + "---|" * len(REGEL_LISTE)]
for k in SCHLUESSEL_LISTE:
    tab2.append(f"| {C.SCHLUESSEL_KURZ[k]} | " + " | ".join(f"{m[k][r]:.2f}" for r in REGEL_LISTE) + " |")
st.markdown("\n".join(tab2))
st.caption("Mittlere Behälter über der Schranke, alle Instanzen der Zelle. Bei gegenläufigen Maßen ab 20 Teilen ist die Schranke locker (Experiment 3): Lesen Sie dort die Unterschiede zwischen den Zeilen und Spalten, nicht den Abstand zur Schranke.")
kind, text = verdict_regeln(z)
getattr(st, kind)(text)

st.markdown("### Experiment 3: Wie scharf ist die Schranke?")
zs = schranke_zeilen()
tab3 = ["| Maße und n | Abstand | darüber | offen |", "|---|---|---|---|"]
for r in zs:
    mittel3 = "-" if r["mittel"] is None else f"{r['mittel']:.2f}"
    tab3.append(f"| {C.ZUSAMMENHAENGE[r['zusammenhang']]} {r['n']} | {mittel3} | {r['ueber']}/{r['entschieden']} | {r['offen']} |")
st.markdown("\n".join(tab3))
st.caption("Abstand: Optimum minus Schranke, Mittel über die entschiedenen Instanzen. Darüber: Instanzen, in denen das Optimum über der Schranke liegt, von den entschiedenen. Offen: nicht entschieden. Bei 20 Teilen entscheidet ein ganzzahliges Programm mit " + f"{C.ILP_ZEITLIMIT:.0f}" + " Sekunden Zeitlimit; die nicht entschiedenen Instanzen fehlen im Mittel, und die Zahl hängt von der Rechenzeit ab.")
kind, text = verdict_schranke(zs)
getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist |
|---|---|
| **Genau zwei Maße** | Mit drei oder mehr Maßen (etwa Volumen, Gewicht und Höhe) wächst die Zahl der möglichen Schlüssel; die Demo misst das nicht, und die Punktwolke braucht zwei Achsen. |
| **Die Maße sind zufällig verteilt** | Nur drei Zusammenhänge mit festem Rauschen und Werten von 5 bis 50 sind gemessen. Andere Verteilungen (wenige sehr schwere Teile, viele leichte) können anders ausfallen. |
| **Die Schranke ist scharf** | Bei gegenläufigen Maßen ab etwa 20 Teilen ist sie locker, weil dort fast immer höchstens drei Teile in einen Behälter passen; der Abstand zur Schranke sagt dort wenig (Experiment 3). |
| **Gleichstände** bleiben in Lieferreihenfolge | Bei gegenläufigen Maßen ist die Summe fast konstant, Gleichstände sind häufig. Löst man sie stattdessen nach dem größeren Volumen auf, brauchen 200 Teile mit dem Schlüssel Summe im Mittel 12,46 statt 10,58 Behälter über der Schranke (die Aufteilung ändert die Reihenfolge innerhalb der Gleichstände). |
| **Alle Teile sind vor dem Packen bekannt** | Wer jedes Teil sofort einsortieren muss, kann nicht sortieren. Das ist Online-Packen. Mehr dazu: [Online](https://sebastianhanisch.net/konzepte-online-algorithmen.html) |
| **Ein Teil ist nur eine Zahl, keine Form** | Haben die Teile eine Form (Rechtecke, Quader), kommt die Geometrie hinzu. |
"""
)

with st.expander("⚠️ Annahmen, Grenzen und bekannte Probleme"):
    st.markdown(C.ASSUMPTIONS_MARKDOWN)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lesehilfe.** *Gegeben:* Teile mit je zwei ganzzahligen Maßen und Behälter mit je einer Kapazität pro Maß. *Gesucht:* eine Zuordnung der Teile zu möglichst wenigen Behältern, sodass in jedem Behälter beide Summen höchstens die Kapazität ergeben.

| Symbol | Bedeutung |
|---|---|
| $n$ | Zahl der Teile |
| $v_i$, $w_i$ | Volumen und Gewicht von Teil $i$, $1 \le v_i, w_i \le C$ |
| $C$ | Kapazität eines Behälters in jedem der beiden Maße |
| $V$, $W$ | Summen $\sum_i v_i$ und $\sum_i w_i$ |
| $\mathrm{OPT}$ | kleinste mögliche Zahl von Behältern |
| $L$ | untere Schranke für $\mathrm{OPT}$ |

**Schlüssel und Regel.** Ein Schlüssel ordnet jedem Teil eine Zahl $s_i$ zu: $v_i$, $w_i$, $\max(v_i, w_i)$, $v_i + w_i$, $v_i^2 + w_i^2$ oder $v_i/V + w_i/W$. Die Teile werden nach fallendem $s_i$ gepackt; Gleichstände bleiben in der Lieferreihenfolge (die Variante nach größerem Volumen wird nur im Vergleich gemessen). *First Fit* setzt ein Teil in den Behälter mit der kleinsten Nummer, in dem $\ell_v + v_i \le C$ und $\ell_w + w_i \le C$ gelten ($\ell_v$, $\ell_w$ die Lasten). *Best Fit* wählt unter den passenden den mit dem kleinsten Wert $(C - \ell_v - v_i) + (C - \ell_w - w_i)$, *Skalarprodukt* den mit dem größten Wert $\ell_v v_i + \ell_w w_i$; Gleichstände gehen an den kleineren Behälter. Passt das Teil nirgends hin, öffnet es einen neuen.

**Schranke.** $L = \max\!\left(\left\lceil V / C \right\rceil, \left\lceil W / C \right\rceil\right) \le \mathrm{OPT}$. Sie ist nicht immer scharf. Bei „gegenläufig“ gilt für jedes Teil $50 \le v_i + w_i \le 60$ (so ist die Instanz gebaut, mit $C = 100$): Vier Teile haben zusammen $v + w \ge 200 = 2C$ und passen nur, wenn alle vier genau 50 haben, sonst passen höchstens drei Teile in einen Behälter. Dann ist $\mathrm{OPT} \ge n/3$ (bis auf den seltenen Fall einer solchen Vierergruppe), während $L$ nur etwa $0{,}3\,n$ ergibt (bei $n = 200$ im Mittel 57, bei $n = 20$ im Mittel 6,4).

**Exaktes Optimum** (bis 12 Teile). Für eine Menge $M$ von Teilen sei $f(M)$ die kleinste Behälterzahl. Der Behälter mit dem Teil kleinster Nummer in $M$ ist eine zulässige Teilmenge $S \subseteq M$ (beide Summen höchstens $C$) mit diesem Teil, und $f(M) = 1 + \min_S f(M \setminus S)$; $\mathrm{OPT} = f(\{1,\dots,n\})$. Bei 20 Teilen rechnet der Generator ein ganzzahliges Programm mit Zeitlimit.

**Literatur** (Zusammenfassungen aus Suchtreffern, Originale nicht gelesen). Panigrahy, Talwar, Uyeda und Wieder (ESA 2011, Microsoft Research) untersuchen Varianten von First Fit Decreasing für das Vektor-Packen und schlagen geometrische Verfahren vor, die laut Zusammenfassung meist besser sind. Übersichten: Christensen, Khan, Pokutta und Tetali (Computer Science Review 24, 2017) sowie Mommessin, Erlebach und Shakhlevich (Computers & Operations Research, 2025). Die Demo übernimmt daraus keine Zahl und keine Gütegarantie.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
