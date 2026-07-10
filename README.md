# Abschlussprojekt
Abschlussprojekt Programmierübung II

# EKG Dashboard

Ein einfaches Projekt für die Analyse von EKG-Daten und Aktivitätsdaten.

## Ziel
- EKG-Daten anzeigen und auswerten
- Personen mit EKG-Tests verwalten
- Aktivitätsdaten als Karte darstellen
- Login und Registrierung für die Nutzung

## Funktionen
- Login / Registrierung
- Personen anlegen, bearbeiten und löschen
- EKG-Analyse mit Peaks und Herzfrequenz
- Vergleich von EKG-Tests
- Upload von .fit-Dateien und Anzeige auf einer Karte

## Voraussetzungen
- Python 3.14
- Streamlit
- weitere Abhängigkeiten aus der Projektdatei

## Starten lokal
```bash
pip install -r requirements.txt
streamlit run main.py
```

## Streamlit Share
- Live-Version: https://abschlussprojekt-gleinser-behensky-bingen.streamlit.app/
- Die App kann auch über Streamlit Community Cloud bereitgestellt werden.

## Struktur
- data/: lokale Daten und Dateien
- src/: Funktionen und Klassen der App
- main.py: Startpunkt der Anwendung