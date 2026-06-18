import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Beschriftungen für die Farbauswahl
COLOR_OPTIONS = {
    "Leistung (W)": "power",
    "Herzfrequenz (BPM)": "heart_rate",
    "Geschwindigkeit (m/s)": "speed",
    "Höhe (m)": "altitude",
    "Kadenz (RPM)": "cadence",
}


def plot_fit_map(df: pd.DataFrame, color_by: str = "power") -> go.Figure:
    """Erstellt eine interaktive Karte der Aktivität mit farbkodierten Datenpunkten.

    Args:
        df: DataFrame aus load_fit_file() mit GPS- und Messdaten
        color_by: Spaltenname der Größe die als Farbe dargestellt wird (z.B. 'power')

    Returns:
        Plotly Figure-Objekt
    """
    # Hover-Text mit allen verfügbaren Werten zusammenbauen
    hover_cols = ["timestamp", "power", "heart_rate", "cadence", "speed", "altitude"]
    available_hover = [col for col in hover_cols if col in df.columns]

    fig = px.scatter_mapbox(
        df,
        lat="position_lat",
        lon="position_long",
        color=color_by if color_by in df.columns else None,
        hover_data={col: True for col in available_hover},
        color_continuous_scale="RdYlGn_r",
        zoom=12,
        height=600,
        title=f"Aktivitätskarte — Farbe: {color_by}"
    )

    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        coloraxis_colorbar=dict(title=color_by)
    )

    return fig
