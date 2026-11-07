"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import vkp_constants as C

PALETTE = ("#4c78a8", "#f58518", "#54a24b", "#b279a2", "#e45756", "#72b7b2", "#9d755d", "#bab0ac", "#eeca3b", "#ff9da6")


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_behaelter(items, bins, cap):
    """Zwei Balken je Behälter: Last an Volumen und Last an Gewicht. Die rote Linie ist die Kapazität (in beiden Maßen gleich).

    Beschriftungen als Text (B1, B2 ...), damit Plotly keine lineare Achse anlegt."""
    labels = [f"B{b + 1}" for b in range(len(bins))]
    vol = [sum(items[i][0] for i in b) for b in bins]
    gew = [sum(items[i][1] for i in b) for b in bins]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Volumen", x=labels, y=vol, marker_color=C.COLOR_VOL, text=vol, textposition="outside", cliponaxis=False, hovertemplate="%{x}: Volumen %{y}<extra></extra>"))
    fig.add_trace(go.Bar(name="Gewicht", x=labels, y=gew, marker_color=C.COLOR_GEW, text=gew, textposition="outside", cliponaxis=False, hovertemplate="%{x}: Gewicht %{y}<extra></extra>"))
    fig.add_hline(y=cap, line=dict(color=C.COLOR_LINE, width=2, dash="dash"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Last (Kapazität %d)" % cap, range=[0, cap * 1.12])
    return _base(fig)


def build_punktwolke(items, bins):
    """Jedes Teil als Punkt (Volumen, Gewicht), gefärbt nach dem Behälter, in den es kommt."""
    behaelter = {i: b for b, teile in enumerate(bins) for i in teile}
    fig = go.Figure(go.Scatter(
        x=[v for v, _ in items], y=[w for _, w in items], mode="markers",
        marker=dict(size=12, color=[PALETTE[behaelter[i] % len(PALETTE)] for i in range(len(items))], line=dict(color="white", width=1)),
        customdata=[[i + 1, behaelter[i] + 1] for i in range(len(items))],
        hovertemplate="Teil %{customdata[0]}: Volumen %{x}, Gewicht %{y}, Behälter %{customdata[1]}<extra></extra>", showlegend=False))
    fig.update_xaxes(title_text="Volumen", range=[0, C.HI + 5])
    fig.update_yaxes(title_text="Gewicht", range=[0, C.HI + 5])
    return _base(fig, 320)


def build_messung(werte, titel):
    """Mittlere Behälter über der Vergleichsbasis für die sieben Schlüssel (Balken); werte = {Schlüssel: Wert}. Schlüssel mit nur einem Maß sind rot."""
    namen = [C.SCHLUESSEL_KURZ[k] for k in sorted(werte)]
    zahlen = [werte[k] for k in sorted(werte)]
    farben = [C.COLOR_EINZEL if k in C.EINZELMASS else C.COLOR_BARS for k in sorted(werte)]
    fig = go.Figure(go.Bar(x=namen, y=zahlen, marker_color=farben, text=[f"{w:.2f}" for w in zahlen], textposition="outside", cliponaxis=False,
                           hovertemplate="%{x}: %{y:.2f}<extra></extra>"))
    fig.update_yaxes(title_text=titel)
    return _base(fig, 340)
