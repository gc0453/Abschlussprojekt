import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.signal import find_peaks


class EKGdata:
    """Klasse zum Laden, Analysieren und Visualisieren von EKG-Daten."""

    def __init__(self, ekg_dict: dict):
        """Konstruktor: Lädt die EKG-Daten aus dem übergebenen Dictionary.
        
        Args:
            ekg_dict: Dictionary mit 'id', 'date' und 'result_link'
        """
        self.id = ekg_dict["id"]
        self.date = ekg_dict["date"]
        self.data_path = ekg_dict["result_link"]

        self.df = pd.read_csv(
            self.data_path, sep='\t', header=None,
            names=["Messwerte in mV", "Zeit in ms"]
        )
        self.peaks = np.array([])  # wird durch find_peaks() befüllt

    @staticmethod
    def load_by_id(ekg_id: int, person_data: list = None):
        """Instanziiert ein EKGdata-Objekt anhand der EKG-ID.
        
        Args:
            ekg_id: Die ID des gesuchten EKG-Tests
            person_data: Optional – Liste aller Personen-Dicts. Wird aus JSON geladen falls None.
        
        Returns:
            EKGdata-Objekt oder None
        """
        if person_data is None:
            with open("data/person_db.json", "r", encoding="utf-8") as f:
                person_data = json.load(f)

        for person in person_data:
            for ekg_test in person.get("ekg_tests", []):
                if ekg_test["id"] == ekg_id:
                    return EKGdata(ekg_test)
        return None

    def find_peaks(self, height: float = 340, distance: int = 200):
        """Findet Peaks (R-Zacken) in den EKG-Daten.
        
        Args:
            height: Mindestwert der Peaks in mV (Standard: 340)
            distance: Mindestabstand zwischen Peaks in Samples (Standard: 200)
        
        Returns:
            Array mit den Indizes der gefundenen Peaks
        """
        peaks, _ = find_peaks(
            self.df["Messwerte in mV"],
            height=height,
            distance=distance
        )
        self.peaks = peaks
        return self.peaks

    def estimate_hr(self) -> float:
        """Berechnet die durchschnittliche Herzfrequenz in BPM anhand der gefundenen Peaks.
        
        Returns:
            Herzfrequenz in BPM (Schläge pro Minute), oder 0.0 falls keine Peaks vorhanden.
        """
        if len(self.peaks) < 2:
            return 0.0

        peak_times = self.df["Zeit in ms"].iloc[self.peaks].values
        intervals_ms = np.diff(peak_times)
        mean_interval_ms = np.mean(intervals_ms)

        hr = 60000 / mean_interval_ms  # ms → BPM
        return round(hr, 1)

    def plot_time_series(self, num_samples: int = 2000) -> go.Figure:
        """Erstellt einen interaktiven Plot der EKG-Zeitreihe mit markierten Peaks.
        
        Args:
            num_samples: Anzahl der darzustellenden Samples (Standard: 2000)
        
        Returns:
            Plotly Figure-Objekt
        """
        df_plot = self.df.head(num_samples)

        fig = px.line(
            df_plot,
            x="Zeit in ms",
            y="Messwerte in mV",
            title="EKG Zeitreihe",
            labels={"Zeit in ms": "Zeit (ms)", "Messwerte in mV": "Amplitude (mV)"}
        )

        # Peaks einzeichnen, falls vorhanden
        if len(self.peaks) > 0:
            visible_peaks = self.peaks[self.peaks < num_samples]
            if len(visible_peaks) > 0:
                peak_df = self.df.iloc[visible_peaks]
                fig.add_trace(go.Scatter(
                    x=peak_df["Zeit in ms"],
                    y=peak_df["Messwerte in mV"],
                    mode="markers",
                    marker=dict(color="red", size=8, symbol="x"),
                    name="Peaks (R-Zacken)"
                ))

        fig.update_layout(
            xaxis_title="Zeit (ms)",
            yaxis_title="Amplitude (mV)",
            legend_title="Legende"
        )
        return fig


if __name__ == "__main__":
    with open("data/person_db.json", "r", encoding="utf-8") as f:
        person_data = json.load(f)

    ekg_dict = person_data[0]["ekg_tests"][0]
    ekg = EKGdata(ekg_dict)
    ekg.find_peaks()
    print(f"Gefundene Peaks: {len(ekg.peaks)}")
    print(f"Geschätzte Herzfrequenz: {ekg.estimate_hr()} BPM")
