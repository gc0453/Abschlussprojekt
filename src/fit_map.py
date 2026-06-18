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
    BLUE_PURPLE_SCALE = [
    [0.0, "#E3F2FD"],   # sehr hellblau
    [0.1, "#BBDEFB"],
    [0.2, "#90CAF9"],
    [0.3, "#64B5F6"],
    [0.4, "#42A5F5"],
    [0.5, "#1E88E5"],   # blau
    [0.6, "#1565C0"],
    [0.7, "#3949AB"],   # indigo
    [0.8, "#5E35B1"],
    [0.9, "#7B1FA2"],   # violett
    [1.0, "#AD1457"]    # magenta
    ]
    
    fig = px.scatter_mapbox(
        df,
        lat="position_lat",
        lon="position_long",
        color=color_by if color_by in df.columns else None,
        hover_data={col: True for col in available_hover},
        color_continuous_scale=BLUE_PURPLE_SCALE,
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
