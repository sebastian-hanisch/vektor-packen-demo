"""Konstanten: Regler-Grenzen, feste Beispiele, Messraster, Farben und Presets."""

CAP = 100                 # Kapazität eines Behälters in jedem der beiden Maße (Volumen, Gewicht)
OPT_LIMIT = 12            # so viele Teile darf das exakte Optimum (Aufzählung aller Teilmengen) höchstens verarbeiten
LO, HI = 5, 50            # jedes Maß eines Teils liegt in diesem Bereich (ganzzahlig, gleichverteilt)
RAUSCHEN = 5              # Abweichung der Zusammenhänge „gleichlaufend“ und „gegenläufig“ (siehe zufallsinstanz)
GEGENLAUF_SUMME = 55      # bei „gegenläufig“ ist Volumen + Gewicht eines Teils etwa so groß

# --- Handbeispiel (Teile als (Volumen, Gewicht) in Lieferreihenfolge) ----------------------------------------------------------------------
# Summe der Volumen 329, der Gewichte 346, Schranke 4, Optimum 4. First Fit: Lieferreihenfolge 4, nach der Summe 4, nach dem Gewicht 5, nach dem Volumen 6 (Phase 0, von Hand nachgerechnet).
HANDBEISPIEL = ((22, 35), (23, 35), (24, 35), (42, 13), (37, 23), (22, 36), (28, 30), (30, 22), (24, 35), (49, 9), (15, 36), (13, 37))

# Quellen der Instanz: 0 = Handbeispiel, 1 bis 3 = Zufallsinstanzen mit dem jeweiligen Zusammenhang der beiden Maße
QUELLEN = {0: "Handbeispiel (zwölf Teile)", 1: "zufällig, unabhängige Maße", 2: "zufällig, gleichlaufende Maße", 3: "zufällig, gegenläufige Maße"}
ZUSAMMENHAENGE = {1: "unabhängig", 2: "gleichlaufend", 3: "gegenläufig"}         # Schlüssel = Quelle
ZUSAMMENHANG_LANG = {1: "unabhängige Maße", 2: "gleichlaufende Maße", 3: "gegenläufige Maße"}
ZUSAMMENHANG_DAT = {1: "unabhängigen Maßen", 2: "gleichlaufenden Maßen", 3: "gegenläufigen Maßen"}   # nach „bei“
N_WERTE = (12, 20, 50)                    # Zahl der Teile der Zufallsinstanzen in der App

SCHLUESSEL = {
    0: "Lieferreihenfolge (nicht sortiert)",
    1: "nach Volumen (größtes zuerst)",
    2: "nach Gewicht (größtes zuerst)",
    3: "nach dem Größeren der beiden Maße",
    4: "nach der Summe beider Maße",
    5: "nach der Länge (Wurzel aus Volumen² + Gewicht²)",
    6: "nach den Anteilen an der Gesamtlast (normierte Summe)",
}
SCHLUESSEL_KURZ = {0: "Lieferung", 1: "Volumen", 2: "Gewicht", 3: "Maximum", 4: "Summe", 5: "Länge", 6: "normiert"}
SCHLUESSEL_MIT = {0: "der Lieferreihenfolge", 1: "dem Volumen", 2: "dem Gewicht", 3: "dem größeren Maß", 4: "der Summe", 5: "der Länge", 6: "der normierten Summe"}
EINZELMASS = (1, 2)                       # Schlüssel, die nur ein Maß benutzen

REGELN = {0: "erster passender (First Fit)", 1: "passendster (Best Fit, kleinste Restsumme)", 2: "Skalarprodukt (Last mal Last, größtes gewinnt)"}
REGEL_KURZ = {0: "First Fit", 1: "Best Fit", 2: "Skalarprodukt"}
REGEL_CODES = {0: "ff", 1: "bf", 2: "dot"}

SEED_MAX, DEFAULT_SEED = 999999, 7

# --- Messraster ---------------------------------------------------------------------------------------------------------------------------
INSTANZEN = 100                           # Instanzen je Zelle; der Wert steht neben jeder Zahl
MESS_N = (12, 20, 50, 200)
EXAKT_N = (12, 20)                        # in diesen Zellen gibt es das Optimum (bei 20 per ganzzahligem Programm mit Zeitlimit, ggf. nicht entschieden)
ILP_ZEITLIMIT = 60.0                      # Sekunden je Instanz (Generator); nicht entschiedene Instanzen stehen in einer eigenen Spalte

COLOR_VOL = "#2F6B65"
COLOR_GEW = "#c47f17"
COLOR_LINE = "#c0392b"
COLOR_BARS = "#4c78a8"
COLOR_EINZEL = "#c0392b"

PRESETS = {
    "Handbeispiel, nach Volumen": {"quelle": 0, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": 1, "regel": 0},
    "Handbeispiel, nach der Summe": {"quelle": 0, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": 4, "regel": 0},
    "Gegenläufige Maße, nach Gewicht": {"quelle": 3, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": 2, "regel": 0},
    "Gleichlaufende Maße, nach Volumen": {"quelle": 2, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": 1, "regel": 0},
}
PRESET_HELP = {
    "Handbeispiel, nach Volumen": "Zwölf Teile mit Volumen und Gewicht, sortiert wie bei einer einzigen Größe: das größte Volumen zuerst. Das Ergebnis ist zwei Behälter schlechter als das Optimum.",
    "Handbeispiel, nach der Summe": "Dieselben zwölf Teile, aber nach der Summe von Volumen und Gewicht sortiert. Jetzt ist die Packung optimal.",
    "Gegenläufige Maße, nach Gewicht": "Eine zufällige Instanz, in der ein Teil mit viel Volumen wenig Gewicht hat und umgekehrt. Sortiert nach nur einem Maß.",
    "Gleichlaufende Maße, nach Volumen": "Eine zufällige Instanz, in der ein Teil mit viel Volumen auch viel Gewicht hat. Dann verhalten sich beide Maße wie eines.",
}

# Text des Expanders „Annahmen, Grenzen und bekannte Probleme“; derselbe Wortlaut steht in der README (tests/test_claims.py vergleicht beide).
ASSUMPTIONS_MARKDOWN = f"""**Annahmen.** Genau zwei Maße je Teil (Volumen und Gewicht, ganzzahlig, {LO} bis {HI}); alle Behälter gleich, in beiden Maßen Kapazität {CAP}; alle Teile sind vor dem Packen bekannt; keine Geometrie, nur Zahlen.

**Grenzen.** Das Messraster deckt drei Zusammenhänge der beiden Maße (unabhängig, gleichlaufend, gegenläufig) und vier Teilezahlen ab, jeweils mit {INSTANZEN} Instanzen je Zelle. Andere Verteilungen der Maße, mehr als zwei Maße und Praxisdaten kommen nicht vor. Das exakte Optimum gibt es live bis {OPT_LIMIT} Teile und vorberechnet bei 20 Teilen (mit Zeitlimit, nicht entschiedene Instanzen stehen in einer eigenen Spalte), bei 50 und 200 Teilen nicht.

**Bekannte Probleme und Unsicherheiten.** Die Schranke aus den beiden Summen ist bei gegenläufigen Maßen ab etwa 20 Teilen locker, weil dort fast immer höchstens drei Teile in einen Behälter passen; bei 50 und 200 Teilen darf deshalb nur die Rangfolge der Sortierschlüssel gelesen werden, nicht der Abstand zur Schranke. Die Zahl der bei 20 Teilen nicht entschiedenen Instanzen hängt von der Rechenzeit ab. Die Mittelwerte des Rasters gelten für diese festen Instanzen; mit anderen Startzahlen ändern sie sich etwas, und eine einzelne Zelle ist kein Gesetz. Die Literaturhinweise im Mathematik-Expander stammen aus Suchtreffern (nur Zusammenfassungen), die Originale wurden nicht gelesen. Die App wurde im Browser bedient (Presets, Würfel-Button und Ausklapper auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät."""
