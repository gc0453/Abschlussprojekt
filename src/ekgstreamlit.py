import streamlit as st
from src.person import get_person_data
from src.ekgdata import EKGdata
from src.read_fit_data import load_fit_file
from src.fit_map import plot_fit_map, COLOR_OPTIONS


def show_ekgstreamlit():
    # ── Seiteneinstellungen ──────────────────────────────────────────────────
    st.title("Dashboard für EKG-Analyse und Aktivitätskarten")

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.success(f"Angemeldet als: {st.session_state.username}")

        if st.button("Abmelden"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["EKG Analyse", "🗺️ Aktivitätskarte"])

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — EKG Analyse (bestehender Code, unverändert)
    # ════════════════════════════════════════════════════════════════════════
    with tab1:
        st.title("🫀 EKG Analyse")
        # ── Personen laden ───────────────────────────────────────────────────
        persons = get_person_data()
        person_names = [p.get_full_name() for p in persons]

        # ── Sidebar: Person auswählen ─────────────────────────────────────────
        st.sidebar.header("Person auswählen")
        selected_name = st.sidebar.selectbox("Person", person_names)
        person = next(p for p in persons if p.get_full_name() == selected_name)

        # ── Personen-Info ─────────────────────────────────────────────────────
        col1, col2 = st.columns([1, 3])

        with col1:
            try:
                st.image(person.picture_path, width=180, caption=selected_name)
            except Exception:
                st.write("📷 Kein Bild verfügbar")

        with col2:
            st.subheader(f"{person.firstname} {person.lastname}")
            st.write(f"**Geburtsjahr:** {person.date_of_birth}")
            st.write(f"**Alter:** {person.calc_age()} Jahre")
            st.write(f"**Geschlecht:** {person.gender}")
            st.write(f"**Max. Herzfrequenz:** {person.calc_max_heart_rate()} BPM")

        st.divider()

        # ── EKG-Daten ─────────────────────────────────────────────────────────
        if not person.ekg_tests:
            st.info("Keine EKG-Daten für diese Person vorhanden.")
        else:
            st.subheader("EKG-Analyse")

            ekg_options = {f"EKG vom {t['date']} (ID {t['id']})": t for t in person.ekg_tests}
            selected_ekg_label = st.selectbox("EKG-Test auswählen", list(ekg_options.keys()))
            ekg_dict = ekg_options[selected_ekg_label]

            ekg = EKGdata(ekg_dict)
            ekg.find_peaks()
            hr = ekg.estimate_hr()

            m1, m2, m3 = st.columns(3)
            m1.metric("Gefundene Peaks", len(ekg.peaks))
            m2.metric("Herzfrequenz (Ø)", f"{hr} BPM")
            m3.metric("Max. Herzfrequenz", f"{person.calc_max_heart_rate()} BPM")

            fig = ekg.plot_time_series()
            st.plotly_chart(fig, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — Aktivitätskarte aus .fit-Datei
    # ════════════════════════════════════════════════════════════════════════
    with tab2:
        st.title("🗺️ Aktivitätskarte")
        st.subheader("Aktivitätskarte")

        fit_file = st.file_uploader("FIT-Datei hochladen", type=["fit"])

        if fit_file is not None:
            with st.spinner("Daten werden geladen..."):
                df = load_fit_file(fit_file)

            if df.empty:
                st.warning("Keine GPS-Daten in dieser Datei gefunden.")
            else:
                # ── Kennzahlen ────────────────────────────────────────────────
                st.subheader("Zusammenfassung")
                cols = st.columns(4)
                if "power" in df.columns:
                    cols[0].metric("Ø Leistung", f"{df['power'].mean():.0f} W")
                    cols[1].metric("Max. Leistung", f"{df['power'].max():.0f} W")
                if "heart_rate" in df.columns:
                    cols[2].metric("Ø Herzfrequenz", f"{df['heart_rate'].mean():.0f} BPM")
                    cols[3].metric("Max. Herzfrequenz", f"{df['heart_rate'].max():.0f} BPM")

                st.divider()

                # ── Farbauswahl ───────────────────────────────────────────────
                available_options = {
                    label: col for label, col in COLOR_OPTIONS.items()
                    if col in df.columns
                }
                selected_label = st.selectbox(
                    "Farbe darstellen nach",
                    list(available_options.keys())
                )
                color_col = available_options[selected_label]

                # ── Karte ─────────────────────────────────────────────────────
                fig_map = plot_fit_map(df, color_by=color_col)
                st.plotly_chart(fig_map, use_container_width=True)

        else:
            st.info("Bitte eine .fit-Datei hochladen um die Karte anzuzeigen.")
