import pandas as pd
from fitparse import FitFile


def load_fit_file(path: str) -> pd.DataFrame:
    """Liest eine .fit-Datei ein und gibt einen DataFrame mit allen relevanten Spalten zurück.

    Args:
        path: Pfad zur .fit-Datei (String oder Streamlit UploadedFile)

    Returns:
        DataFrame mit den Spalten: timestamp, power, heart_rate, cadence, speed, altitude,
        position_lat, position_long. Zeilen ohne GPS-Daten werden entfernt.
    """
    fit = FitFile(path)

    records = []
    for record in fit.get_messages("record"):
        data = {}
        for field in record.fields:
            data[field.name] = field.value
        records.append(data)

    df = pd.DataFrame(records)

    # Nur relevante Spalten behalten (falls vorhanden)
    wanted_columns = [
        "timestamp", "power", "heart_rate", "cadence",
        "speed", "altitude", "position_lat", "position_long"
    ]
    available = [col for col in wanted_columns if col in df.columns]
    df = df[available].copy()

    # GPS-Koordinaten von Garmin-Einheiten (semicircles) in Grad umrechnen
    if "position_lat" in df.columns:
        df["position_lat"] = df["position_lat"] * (180 / 2**31)
    if "position_long" in df.columns:
        df["position_long"] = df["position_long"] * (180 / 2**31)

    # Zeilen ohne GPS-Koordinaten entfernen
    if "position_lat" in df.columns and "position_long" in df.columns:
        df = df.dropna(subset=["position_lat", "position_long"])

    df = df.reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = load_fit_file("data/activity.fit")
    print(df.head())
    print(f"\nSpalten: {list(df.columns)}")
    print(f"Datenpunkte: {len(df)}")
