"""Kern der Demo (nur Standardbibliothek): Sortierschlüssel, Platzierungsregeln, Schranke, exaktes Optimum und der unabhängige Prüfer.

Jede Regel ist eine eigene Funktion mit expliziten Ein- und Ausgaben (DEMO-PLAYBOOK §1b). Teile sind Paare (Volumen, Gewicht); ein Behälter hält höchstens
`cap` Volumen und höchstens `cap` Gewicht. Packungen sind Listen von Behältern, jeder Behälter eine Liste von Teilenummern (Index in der Lieferreihenfolge)."""


def schluessel_wert(items, schluessel: int):
    """Sortierzahlen der Teile (größer = früher); `None` bei der Lieferreihenfolge.

    1 Volumen, 2 Gewicht, 3 das größere der beiden Maße, 4 Summe, 5 quadrierte Länge (Volumen² + Gewicht²), 6 normierte Summe v/Σv + w/Σw,
    ganzzahlig als v·Σw + w·Σv gerechnet (derselbe Wert mal Σv·Σw), damit es keine Rundungsgleichstände gibt."""
    if schluessel == 0:
        return None
    if schluessel == 1:
        return [v for v, _ in items]
    if schluessel == 2:
        return [w for _, w in items]
    if schluessel == 3:
        return [max(v, w) for v, w in items]
    if schluessel == 4:
        return [v + w for v, w in items]
    if schluessel == 5:
        return [v * v + w * w for v, w in items]
    if schluessel == 6:
        sv = sum(v for v, _ in items)
        sw = sum(w for _, w in items)
        return [v * sw + w * sv for v, w in items]
    raise ValueError(f"Schlüssel {schluessel!r} unbekannt")


def reihenfolge(items, schluessel: int, gleichstand: str = "lieferung") -> list:
    """Teilenummern in der Reihenfolge, in der gepackt wird: absteigend nach der Sortierzahl. Gleichstände: bei `gleichstand="lieferung"` (Standard) bleibt die Lieferreihenfolge,
    bei `"volumen"` entscheidet zuerst das größere Volumen, dann das größere Gewicht, zuletzt die Lieferreihenfolge (nur für den Vergleich in den Tests und in der README)."""
    if gleichstand not in ("lieferung", "volumen"):
        raise ValueError(f"Gleichstandsregel {gleichstand!r} unbekannt")
    n = len(items)
    z = schluessel_wert(items, schluessel)
    if z is None:
        return list(range(n))
    if gleichstand == "volumen":
        return sorted(range(n), key=lambda i: (-z[i], -items[i][0], -items[i][1], i))
    return sorted(range(n), key=lambda i: (-z[i], i))


def pack(items, order, cap: int, regel: int) -> list:
    """Teile in der Reihenfolge `order` in Behälter setzen. Regel 0: erster Behälter, in den das Teil passt; 1: unter den passenden der Behälter mit der kleinsten
    Restsumme (frei Volumen + frei Gewicht) nach dem Einsetzen; 2: der passende Behälter mit dem größten Skalarprodukt (Volumenlast·Volumen + Gewichtslast·Gewicht).
    Gleichstände: der Behälter mit der kleineren Nummer. Passt das Teil nirgends hin, wird ein neuer Behälter geöffnet."""
    if regel not in (0, 1, 2):
        raise ValueError(f"Regel {regel!r} unbekannt")
    if sorted(order) != list(range(len(items))):
        raise ValueError("die Reihenfolge muss jedes Teil genau einmal enthalten")
    for t in items:
        if len(t) != 2 or any(x <= 0 or x > cap for x in t):
            raise ValueError(f"Teil {t!r} ungültig (zwei Maße, je 1 bis {cap})")
    bins, last = [], []                # last[b] = [Volumenlast, Gewichtslast]
    for i in order:
        v, w = items[i]
        wahl, beste = None, None
        for b, (lv, lw) in enumerate(last):
            if lv + v <= cap and lw + w <= cap:
                if regel == 0:
                    wahl = b
                    break
                wert = (cap - lv - v) + (cap - lw - w) if regel == 1 else lv * v + lw * w
                if beste is None or (wert < beste if regel == 1 else wert > beste):
                    beste, wahl = wert, b
        if wahl is None:
            bins.append([i])
            last.append([v, w])
        else:
            bins[wahl].append(i)
            last[wahl][0] += v
            last[wahl][1] += w
    return bins


def anzahl(items, schluessel: int, regel: int, cap: int) -> int:
    return len(pack(items, reihenfolge(items, schluessel), cap, regel))


def container_pruefen(items, bins, cap: int) -> bool:
    """Unabhängiger Prüfer: jedes Teil genau einmal, in jedem Behälter beide Summen höchstens `cap`, kein leerer Behälter."""
    gesehen = sorted(i for b in bins for i in b)
    if gesehen != list(range(len(items))):
        return False
    return all(b and sum(items[i][0] for i in b) <= cap and sum(items[i][1] for i in b) <= cap for b in bins)


def schranke(items, cap: int) -> int:
    """Untere Schranke: das Größere von ⌈Σ Volumen / cap⌉ und ⌈Σ Gewicht / cap⌉."""
    sv = sum(v for v, _ in items)
    sw = sum(w for _, w in items)
    return max(-(-sv // cap), -(-sw // cap))


def optimum(items, cap: int, limit: int = 12):
    """Exaktes Optimum durch Aufzählung aller Teilmengen (Mengenpartitions-DP): dp[M] = kleinste Behälterzahl für die Teile in M; der Behälter mit dem Teil
    kleinster Nummer in M ist eine zulässige Teilmenge S von M. Bei mehr als `limit` Teilen None (zu viele Teilmengen)."""
    n = len(items)
    if n > limit:
        return None
    if n == 0:
        return 0
    voll = (1 << n) - 1
    sv = [0] * (voll + 1)
    sw = [0] * (voll + 1)
    for m in range(1, voll + 1):
        low = (m & -m).bit_length() - 1
        sv[m] = sv[m & (m - 1)] + items[low][0]
        sw[m] = sw[m & (m - 1)] + items[low][1]
    passt = [sv[m] <= cap and sw[m] <= cap for m in range(voll + 1)]
    dp = [0] + [n + 1] * voll
    for m in range(1, voll + 1):
        low = m & -m
        sub = m
        bester = n + 1
        while sub:
            if sub & low and passt[sub] and dp[m ^ sub] + 1 < bester:
                bester = dp[m ^ sub] + 1
            sub = (sub - 1) & m
        dp[m] = bester
    return dp[voll]
