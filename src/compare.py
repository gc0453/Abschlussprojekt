import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import Tuple, Dict
from src.ekgdata import EKGdata


def compare_peak_counts(ekg_a: EKGdata, ekg_b: EKGdata) -> Dict[str, int]:
    """Vergleicht die Anzahl gefundener Peaks zwischen zwei EKGs.

    Returns a dict with counts and the absolute difference.
    """
    a = len(ekg_a.peaks)
    b = len(ekg_b.peaks)
    return {"a_count": a, "b_count": b, "diff": abs(a - b)}


def compare_heart_rates(ekg_a: EKGdata, ekg_b: EKGdata) -> Dict[str, float]:
    """Vergleicht die geschätzten Herzfrequenzen (BPM).

    Liefert die beiden Werte und die Differenz (absolut und relativ in %).
    """
    hr_a = ekg_a.estimate_hr()
    hr_b = ekg_b.estimate_hr()
    diff = hr_a - hr_b
    rel = (diff / hr_b * 100) if hr_b else float('nan')
    return {"hr_a": hr_a, "hr_b": hr_b, "diff": round(diff, 1), "rel_percent": round(rel, 1)}


def align_waveforms(ekg_a: EKGdata, ekg_b: EKGdata, max_samples: int = 2000, align_first_peak: bool = False) -> Tuple[pd.Series, pd.Series]:
    """Gleicht zwei Signalreihen auf gemeinsame Zeitachse ab und gibt die abgeschnittenen Series zurück.

    Beide Series werden auf `max_samples` gekürzt (oder gepadded mit NaN), sodass sie gleich lang sind.
    
    Args:
        ekg_a: Erstes EKG
        ekg_b: Zweites EKG
        max_samples: Maximale Anzahl der Samples
        align_first_peak: Wenn True, werden die EKGs zeitlich so ausgerichtet, dass ihre ersten Peaks übereinander liegen
    """
    sa = ekg_a.df["Messwerte in mV"].reset_index(drop=True).astype(float)
    sb = ekg_b.df["Messwerte in mV"].reset_index(drop=True).astype(float)

    # Wenn Peak-Alignment gewünscht ist
    if align_first_peak and len(ekg_a.peaks) > 0 and len(ekg_b.peaks) > 0:
        first_peak_a = ekg_a.peaks[0]
        first_peak_b = ekg_b.peaks[0]
        peak_diff = first_peak_b - first_peak_a
        
        # Verschiebe die kürzere Serie, um die Peaks auszurichten
        if peak_diff > 0:
            # ekg_b Peak liegt später, also ekg_a am Anfang mit NaN auffüllen
            sa = pd.Series(np.concatenate([np.full(peak_diff, np.nan), sa.values]))
        elif peak_diff < 0:
            # ekg_a Peak liegt später, also ekg_b am Anfang mit NaN auffüllen
            sb = pd.Series(np.concatenate([np.full(-peak_diff, np.nan), sb.values]))
        
        # Neuindexierung nach der Verschiebung
        sa = sa.reset_index(drop=True).astype(float)
        sb = sb.reset_index(drop=True).astype(float)

    la = min(len(sa), max_samples)
    lb = min(len(sb), max_samples)

    sa = sa.iloc[:la]
    sb = sb.iloc[:lb]

    target = max(la, lb)
    if target < max_samples:
        target = max_samples

    sa = sa.reindex(range(target))
    sb = sb.reindex(range(target))

    return sa, sb


def waveform_correlation(ekg_a: EKGdata, ekg_b: EKGdata, max_samples: int = 2000, align_first_peak: bool = False) -> float:
    """Berechnet die Pearson-Korrelation zwischen zwei EKG-Zeitreihen.

    Gibt einen Wert in [-1, 1] zurück; NaN wird zu 0.0 konvertiert.
    
    Args:
        align_first_peak: Wenn True, werden die EKGs zeitlich so ausgerichtet, dass ihre ersten Peaks übereinander liegen
    """
    sa, sb = align_waveforms(ekg_a, ekg_b, max_samples=max_samples, align_first_peak=align_first_peak)
    joined = pd.concat([sa, sb], axis=1)
    joined.columns = ["a", "b"]
    corr = joined.corr().iloc[0, 1]
    if pd.isna(corr):
        return 0.0
    return float(corr)


def overlay_plot(ekg_a: EKGdata, ekg_b: EKGdata, max_samples: int = 2000, title: str = "EKG Overlay", label_a: str = None, label_b: str = None, align_first_peak: bool = True) -> go.Figure:
    """Erstellt eine überlagerte Plotly-Figur mit beiden EKG-Zeitreihen.

    Die Reihen werden auf `max_samples` gekürzt/aufgefüllt und übereinander dargestellt.
    
    Args:
        ekg_a: Erstes EKG
        ekg_b: Zweites EKG
        max_samples: Maximale Anzahl der Samples
        title: Titel des Plots
        label_a: Label für EKG A
        label_b: Label für EKG B
        align_first_peak: Wenn True (Standard), werden die EKGs zeitlich so ausgerichtet, dass ihre ersten Peaks übereinander liegen
    """
    sa, sb = align_waveforms(ekg_a, ekg_b, max_samples=max_samples, align_first_peak=align_first_peak)

    # x-Achse: wenn zeitstempel vorhanden, verwende die von ekg_a (angepasst), sonst Sample-Index
    try:
        time_a = ekg_a.df["Zeit in ms"].reset_index(drop=True).astype(float).iloc[:len(sa)]
        x = list(time_a.index) if time_a.isnull().all() else time_a.fillna(method="ffill").tolist()
    except Exception:
        x = list(range(len(sa)))

    fig = go.Figure()
    name_a = label_a if label_a is not None else f"A: {ekg_a.date} (ID {ekg_a.id})"
    name_b = label_b if label_b is not None else f"B: {ekg_b.date} (ID {ekg_b.id})"
    fig.add_trace(go.Scatter(x=x, y=sa.values, mode="lines", name=name_a, line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=x, y=sb.values, mode="lines", name=name_b, line=dict(color="red", width=1), opacity=0.7))

    fig.update_layout(title=title, xaxis_title="Zeit (ms) / Samples", yaxis_title="Amplitude (mV)")
    return fig


def compare_peak_timing(ekg_a: EKGdata, ekg_b: EKGdata) -> Dict[str, float]:
    """Vergleicht die durchschnittliche Peak-Intervalldauer (ms) beider EKGs.

    Liefert die mittleren Intervalle und ihre Differenz.
    """
    def mean_interval_ms(ekg: EKGdata) -> float:
        if len(ekg.peaks) < 2:
            return 0.0
        times = ekg.df["Zeit in ms"].iloc[ekg.peaks].values
        return float(np.mean(np.diff(times)))

    mi_a = mean_interval_ms(ekg_a)
    mi_b = mean_interval_ms(ekg_b)
    return {"mi_a_ms": round(mi_a, 1), "mi_b_ms": round(mi_b, 1), "diff_ms": round(abs(mi_a - mi_b), 1)}


__all__ = [
    "compare_peak_counts",
    "compare_heart_rates",
    "align_waveforms",
    "waveform_correlation",
    "compare_peak_timing",
]
