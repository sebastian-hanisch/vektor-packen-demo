# Zwei Grenzen: Volumen und Gewicht – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-vektor-packen-demo.streamlit.app/)** -->

Stück 14 der Konzepte-Reihe **„Packen: Reihenfolge und Platzierungsregel“** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (ein Verfahren mit wachsendem Beispiel: eine Packung entsteht aus einer Reihenfolge der Teile und einer Regel, wohin das nächste kommt). Die Demo geht von einer Größe je Teil zu zwei Größen, Volumen und Gewicht, und fragt, **wonach man dann sortiert** und ob die Wahl des Sortierschlüssels oder die der Regel mehr verändert. Die Fall-Demos mit Containern zeigen die Anwendung samt Kostenmodell; diese Demo erklärt den Mechanismus davor.

## Warum dieses Problem

Ein Behälter hat im Alltag zwei Grenzen zugleich: Volumen und Gewicht. Bei einer einzigen Größe sortiert man „das größte zuerst“. Bei zwei Maßen gibt es dieses „größte“ nicht, man muss erst aus beiden Zahlen eine Sortierzahl machen. Die Demo zeigt an zwölf Teilen, dass Sortieren nach nur einem der beiden Maße zwei Behälter mehr braucht als gar nicht zu sortieren, und misst dasselbe an je 100 Zufallsinstanzen in 12 Zellen.

## Modell

Teile mit zwei ganzzahligen Maßen (Volumen vᵢ, Gewicht wᵢ, je 5 bis 50), Behälter mit Kapazität 100 in beiden Maßen, alle Teile vorab bekannt. **Schlüssel** (Sortierzahl, absteigend; Gleichstand: Lieferreihenfolge): Lieferreihenfolge, Volumen, Gewicht, das größere der beiden Maße, Summe, quadrierte Länge, normierte Summe vᵢ/Σv + wᵢ/Σw. **Regeln:** *First Fit* (der erste Behälter, in dem beide Maße passen), *Best Fit* (unter den passenden der mit der kleinsten Restsumme nach dem Einsetzen), *Skalarprodukt* (der passende Behälter mit der größten Summe aus Volumenlast mal Volumen und Gewichtslast mal Gewicht). **Schranke:** das Größere von ⌈Σv / 100⌉ und ⌈Σw / 100⌉; **exaktes Optimum** bis zwölf Teile durch Aufzählung aller Teilmengen. **Drei Zusammenhänge der Maße:** *unabhängig*, *gleichlaufend* (Gewicht = Volumen ± 5) und *gegenläufig* (Gewicht ≈ 55 − Volumen ± 5, jeweils auf 5 bis 50 begrenzt). Formeln im Expander 📐 der App.

## Methodik

- **Kern** (`vkp_algorithm.py`): `schluessel_wert`, `reihenfolge`, `pack` (drei Regeln), `schranke`, `optimum` (Mengenpartitions-DP über Bitmasken), `container_pruefen` (unabhängiger Zulässigkeitsprüfer).
- **Handbeispiel:** zwölf feste Teile. Die App zeigt die Punktwolke der Teile (Volumen gegen Gewicht), die Behälter mit je zwei Balken (Last an Volumen und an Gewicht) und alle 21 Kombinationen aus Schlüssel und Regel.
- **Messraster:** drei Zusammenhänge × vier Teilezahlen (12, 20, 50, 200) × **100 feste Instanzen** je Zelle. Maßstab ist bei 12 und 20 Teilen das Optimum (bei 12 aus der Aufzählung, bei 20 aus einem ganzzahligen Programm mit {{ILP_ZEITLIMIT}} Sekunden Zeitlimit je Instanz, nicht entschiedene Instanzen fehlen im Mittel), bei 50 und 200 Teilen die Schranke. Die Summen stehen als ganze Zahlen in `vkp_precomputed.json` (erzeugt von `generate_precomputed.py`).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind Messungen an den Instanzen dieser Demo (feste Seeds), nachgerechnet in `tests/test_claims.py`, `tests/test_algorithm.py` und `tests/test_oracle_vektor_packen.py`. Tabellenwerte sind Mittel über die Instanzen einer Zelle von (Behälter minus Vergleichsbasis) mit First Fit.

| Frage | Befund |
|---|---|
| Handbeispiel (zwölf Teile, Summe der Volumen 329, der Gewichte 346, Schranke 4, Optimum 4) | First Fit braucht in Lieferreihenfolge **4** Behälter, nach dem Volumen **6**, nach dem Gewicht **5**, nach dem Maximum **5**, nach der Summe **4**, nach der Länge **5**, nach der normierten Summe **4** (`tests/test_algorithm.py`) |
| Schadet Sortieren nach nur einem Maß? | In **8 von 12** Zellen (alle mit unabhängigen oder gegenläufigen Maßen) liegt First Fit mit Schlüssel Volumen und mit Schlüssel Gewicht im Mittel höher als in Lieferreihenfolge; in den **4** Zellen mit gleichlaufenden Maßen niedriger |
| Wie oft trifft First Fit das Optimum? | Bei 12 Teilen mit gegenläufigen Maßen nach Volumen in 16 %, nach Gewicht in 19 %, in Lieferreihenfolge in 50 % und nach der Summe in 58 % der 100 Instanzen; bei 20 Teilen in 7 %, 8 %, 71 % und 79 % der 98 entschiedenen |
| Welcher Schlüssel ist am besten? | Die Summe liegt in allen 12 Zellen höchstens **0,02** über dem besten Schlüssel der Zelle (Mittel, auf zwei Stellen gerundet), ist aber nicht in jeder Zelle der beste. Bei gegenläufigen Maßen und 200 Teilen ist sie mit 10,58 gegen 10,85 nur wenig besser als die Lieferreihenfolge (besser in 38, schlechter in 17 von 100 Instanzen) |
| Zählt die Regel oder der Schlüssel mehr? | In allen **12** Zellen ist der Unterschied zwischen den sieben Schlüsseln (bei gleicher Regel) größer als der zwischen den drei Regeln (bei gleichem Schlüssel): die Regeln unterscheiden sich um höchstens **0,93** Behälter, die Schlüssel um **0,08** bis **10,50** |
| Wie scharf ist die Schranke? | Das Optimum liegt bei 12 und 20 Teilen im Mittel höchstens 0,07 über ihr, nur bei gegenläufigen Maßen und 20 Teilen um **0,63** (in 62 von 98 entschiedenen Instanzen darüber); bei 50 und 200 Teilen fehlt das Optimum |
| Wirkt die Auflösung von Gleichständen? | Bei gegenläufigen Maßen ist die Summe fast konstant (50 bis 60), Gleichstände sind häufig. Mit Gleichstand nach dem größeren Volumen statt nach der Lieferreihenfolge brauchen 200 Teile im Schlüssel Summe im Mittel 12,46 statt 10,58 Behälter über der Schranke |
| Wie viele Instanzen bleiben bei 20 Teilen offen? | **2** von 300 (beide bei gegenläufigen Maßen); die Zahl hängt von der Rechenzeit ab |

**Sortierschlüssel gegen Zusammenhang** (Mittel der Behälter über der Vergleichsbasis, First Fit; bei 12 und 20 Teilen über dem Optimum, bei 50 und 200 über der Schranke; bei gegenläufigen Maßen ab 20 Teilen ist die Schranke locker, dort zählt nur die Rangfolge der Schlüssel):

{{TABELLE_A}}

**Optimum getroffen** (Anteil der entschiedenen Instanzen, in denen First Fit mit dem Schlüssel genau das Optimum braucht):

{{TABELLE_B}}

**Optimum gegen Schranke** (Mittel über die entschiedenen Instanzen):

{{TABELLE_C}}

## Ehrliche Grenzen

- Alle Aussagen gelten für zwei Maße, drei Zusammenhänge mit festem Rauschen und Werte von 5 bis 50, vier Teilezahlen und eine Sorte Behälter. Andere Verteilungen (wenige sehr schwere Teile, viele leichte), mehr als zwei Maße und Praxisdaten sind nicht gemessen.
- Die Schranke ist bei gegenläufigen Maßen ab etwa 20 Teilen locker. Der Abstand zur Schranke bei 50 und 200 Teilen ist dort zum großen Teil Lockerheit der Schranke und kein schlechtes Packen; gelesen werden darf nur die Rangfolge der Schlüssel.
- Das Optimum bei 20 Teilen kommt aus einem ganzzahligen Programm mit Zeitlimit; die nicht entschiedenen Instanzen fehlen im Mittel, und ihre Zahl hängt von der Rechenzeit ab. Bei 30 Teilen wäre es bei gegenläufigen Maßen zu oft unentschieden und die Mittel wären verzerrt, deshalb fehlt n = 30.
- Die Wahl der Platzierungsregel (drei Regeln) ist ein Nebenbefund, kein Vergleich aller bekannten Regeln; die Literaturhinweise zu Vektor-Packen (Panigrahy u. a. 2011, Christensen u. a. 2017, Mommessin u. a. 2025) stammen aus Suchtreffern, die Originale wurden nicht gelesen, und es wird keine Zahl und keine Gütegarantie daraus übernommen.
- Das Raster sagt nichts über Teile, die einzeln nacheinander ohne Kenntnis der späteren eintreffen (Online-Packen, Konzepte-Reihe Online-Algorithmen).

### Annahmen, Grenzen und bekannte Probleme (Text wie in der App)

{{ANNAHMEN}}

## Verifikation

- **Kern:** First Fit mit den Schlüsseln Volumen, Gewicht, Summe und Lieferreihenfolge sowie die Gleichstandsregeln an einer von Hand gerechneten Mini-Instanz (fünf Teile, Kapazität 10); Best Fit und Skalarprodukt an je einem Handbeispiel mit eindeutiger Wahl; das Handbeispiel der App mit den Behälterlasten der Packungen; unabhängiger Zulässigkeitsprüfer; Randfälle (leere Eingabe, ein Teil, Teil gleich Kapazität, Grenze inklusive, ungültige Eingaben).
- **Orakel** (`tests/test_oracle_vektor_packen.py`): Optimum gegen Aufzählung aller Zerlegungen (n ≤ 7, 40 Instanzen) und gegen ein ganzzahliges Programm (n ≤ 8, 8 Instanzen); die drei Regeln gegen eine bewusst naive Zweitumsetzung (40 Instanzen, drei Schlüssel); die normierte Summe gegen Bruchrechnung; Eigenschaften: Behälterzahl ≥ Optimum ≥ Schranke, Vertauschen von Volumen und Gewicht, gemeinsames Skalieren, Eingabereihenfolge, bei gleichen Maßen das eindimensionale FFD.
- **Messraster:** jede der 12 Zellen wird frisch gerechnet und exakt mit `vkp_precomputed.json` verglichen, die Optima bei 12 Teilen frisch aus der Aufzählung, bei 20 Teilen eine Stichprobe mit dem ganzzahligen Programm; jede Zahl dieser README als Textsuche (`tests/test_claims.py`).
- **Verdikte:** alle Zweige und Schwellen an von Hand gesetzten Werten (`tests/test_verdicts.py`).
- **Presets und Layout:** vollständig, Werte innerhalb der Reglergrenzen, erstes Preset gleich Standardeinstellung; Schnellstart oben in der Seitenleiste, fester Kopf, genau das passende Preset hervorgehoben (`tests/test_layout.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jede Auswahl in jedem Wert, Startzahl an den Grenzen) und Footer-Test.
- **Tests gesamt:** {{TESTS}}.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `dev/ilp.py` | ganzzahliges Programm für das Optimum bei 20 Teilen (nur Generator und Tests) |
| `dev/readme_bauen.py`, `dev/readme_vorlage.md` | setzen die README aus der Vorlage, den Tabellen der Messzellen und dem Text der Annahmen zusammen |
| `generate_precomputed.py` | erzeugt `vkp_precomputed.json` (Messraster); `--check` vergleicht, `--keep-opt` behält die Optima |
| `requirements-dev.txt` | Laufzeit plus pytest und scipy |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `vkp_algorithm.py` | Kern: Schlüssel, Regeln, Schranke, exaktes Optimum, Zulässigkeitsprüfer |
| `vkp_constants.py` | Handbeispiel, Reglerwerte, Messraster, Farben, Presets, Text der Annahmen |
| `vkp_evaluation.py` | Analyse, Verdikte, Messzellen |
| `vkp_layout.py` | Fester Kopf (Stylesheet) |
| `vkp_precomputed.json` | vorberechnete Summen und Optima des Messrasters |
| `vkp_presets.py` | Permalink (Begrenzen), Presets (Schnellstart, aktives Preset hervorgehoben), Würfel-Button |
| `vkp_scenario.py` | Instanzen: Handbeispiel und Zufallsinstanzen mit festen Seeds |
| `vkp_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Mini-Instanz und Handrechnung, Orakel, Randfälle, Verdikte, Presets, Layout, Messraster und Zahlen der README, AppTest-Rauchtest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Mehr als zwei Maße, andere Verteilungen der Maße:** nicht Gegenstand dieses Stücks.
- **Stärkere Schranken für Vektor-Packen (L₂ oder LP-Schranke für zwei Maße):** bräuchten eine eigene Herleitung; die Lockerheit der einfachen Schranke steht stattdessen als Befund da.
- **Optimum bei mehr als 20 Teilen:** bräuchte ein stärkeres Modell (Spaltenerzeugung oder Arc-Flow), das ganzzahlige Programm lässt bei 30 Teilen zu viele Instanzen offen.
- **Gütegarantien und Zahlen aus der Literatur:** Die Originale wurden nicht gelesen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit und Plotly.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
