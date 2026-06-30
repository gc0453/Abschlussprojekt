import streamlit as st
from src.person import get_person_data
from src.ekgdata import EKGdata
from src.read_fit_data import load_fit_file
from src.fit_map import plot_fit_map, COLOR_OPTIONS
from src.add_person import add_person_with_ekg, update_person, delete_person
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
#from reportlab.lib.utils import ImageReader
#from datetime import date


def show_ekgstreamlit():
    """Hauptfunktion des EKG Dashboards nach dem Login.

    Rendert die Streamlit-Oberfläche mit zwei Seiten:
    - EKG Analyse: Personenauswahl, EKG-Plot und Herzfrequenz-Kennzahlen
    - Aktivitätskarte: Upload einer .fit-Datei und interaktive GPS-Karte

    Die aktive Seite wird über st.session_state.page gesteuert.
    """

    # ── Session State initialisieren ─────────────────────────────────────────
    if st.session_state.page not in ("ekg", "karte"):
        st.session_state.page = "ekg"

    # ── Personen immer laden (auch wenn Karte aktiv) ─────────────────────────
    persons = get_person_data()
    person_names = [p.get_full_name() for p in persons]

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.success(f"Angemeldet als: {st.session_state.username}")

        if st.button("Abmelden"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

        st.divider()

        # ── Hauptnavigation ───────────────────────────────────────────────────
        st.subheader("Navigation")
        if st.button("🫀 EKG Analyse", use_container_width=True):
            st.session_state.page = "ekg"
            st.rerun()
        if st.button("🗺️ Aktivitätskarte", use_container_width=True):
            st.session_state.page = "karte"
            st.rerun()

        st.divider()

        # ── Untermenü nur wenn EKG aktiv ──────────────────────────────────────
        if st.session_state.page == "ekg":
            st.subheader("Person auswählen")
            selected_name = st.selectbox("Person", person_names)
        else:
            selected_name = person_names[0]  # Fallback, wird nicht angezeigt

    person = next(p for p in persons if p.get_full_name() == selected_name)

    # ════════════════════════════════════════════════════════════════════════
    # SEITE: EKG Analyse
    # ════════════════════════════════════════════════════════════════════════
    if st.session_state.page == "ekg":
        st.title("🫀 EKG Dashboard")

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
            st.plotly_chart(fig, use_container_width=True, key="ekg_plot_main")

            # Vergleichs-UI: Person + spezifischen Test auswählen und vergleichen (Overlay)
            if any(p.ekg_tests for p in persons):
                st.divider()
                st.subheader("EKG-Vergleich (Person & Test)")

                compare_person_name = st.selectbox("Person zum Vergleichen", person_names, index=person_names.index(selected_name) if selected_name in person_names else 0)
                compare_person = next(p for p in persons if p.get_full_name() == compare_person_name)

                if not compare_person.ekg_tests:
                    st.info(f"{compare_person.get_full_name()} hat keine EKG-Tests.")
                else:
                    # Filtere den aktuell ausgewählten Test aus der Vergleichliste
                    available_tests = [t for t in compare_person.ekg_tests if t['id'] != ekg_dict['id']]
                    
                    if not available_tests:
                        st.info("Du kannst ein EKG nicht mit sich selbst vergleichen. Bitte einen anderen Test auswählen.")
                    else:
                        compare_options = {f"EKG vom {t['date']} (ID {t['id']})": t for t in available_tests}
                        compare_label = st.selectbox("Test der Vergleichsperson auswählen", list(compare_options.keys()))
                        compare_dict = compare_options[compare_label]

                        other_ekg = EKGdata(compare_dict)
                        other_ekg.find_peaks()

                        from src.compare import compare_peak_counts, compare_heart_rates, waveform_correlation, compare_peak_timing, overlay_plot

                        if st.button("Vergleichen"):
                            pc = compare_peak_counts(ekg, other_ekg)
                            hrc = compare_heart_rates(ekg, other_ekg)
                            corr = waveform_correlation(ekg, other_ekg)
                            mt = compare_peak_timing(ekg, other_ekg)

                            cols_metrics = st.columns(4)
                            cols_metrics[0].metric("Peaks A", pc['a_count'])
                            cols_metrics[1].metric("Peaks B", pc['b_count'])
                            cols_metrics[2].metric("HR A", f"{hrc['hr_a']} BPM")
                            cols_metrics[3].metric("HR B", f"{hrc['hr_b']} BPM")

                            st.write(f"Unterschied Peaks: {pc['diff']}")
                            st.write(f"Differenz HR: {hrc['diff']} BPM ({hrc['rel_percent']}%)")
                            st.write(f"Signal-Korrelation: {corr:.3f}")
                            st.write(f"Intervall A: {mt['mi_a_ms']} ms — Intervall B: {mt['mi_b_ms']} ms — Diff: {mt['diff_ms']} ms")

                            # Overlay-Plot
                            label_a = f"{selected_name} — {ekg.date}"
                            label_b = f"{compare_person_name} — {other_ekg.date}"
                            fig_overlay = overlay_plot(
                                ekg,
                                other_ekg,
                                max_samples=2000,
                                title=f"Overlay: {selected_name} vs {compare_person_name}",
                                label_a=label_a,
                                label_b=label_b,
                            )
                            st.plotly_chart(fig_overlay, use_container_width=True, key=f"overlay_{ekg.id}_{other_ekg.id}")

        st.divider()

        # ── Neue Person + EKG hinzufügen ──────────────────────────────────
        with st.expander("➕ Neue Person + EKG hinzufügen"):
            with st.form("add_person_form"):
                st.subheader("Persönliche Daten")
                col_a, col_b = st.columns(2)
                new_firstname = col_a.text_input("Vorname")
                new_lastname = col_b.text_input("Nachname")

                col_c, col_d = st.columns(2)
                new_dob = col_c.number_input("Geburtsjahr", min_value=1900, max_value=2025, value=1990)
                new_gender = col_d.selectbox("Geschlecht", ["male", "female"])

                new_picture = st.file_uploader("Profilbild (optional)", type=["jpg", "jpeg", "png"])

                st.subheader("EKG-Test")
                new_ekg_file = st.file_uploader("EKG-Datei (.txt)", type=["txt"])
                new_ekg_date = st.text_input("Datum des Tests (z.B. 24.6.2026)")

                submitted_add = st.form_submit_button("Person speichern")

                if submitted_add:
                    if not new_firstname or not new_lastname:
                        st.error("Bitte Vor- und Nachname angeben.")
                    elif new_ekg_file is None:
                        st.error("Bitte eine EKG-Datei hochladen.")
                    elif not new_ekg_date:
                        st.error("Bitte ein Datum angeben.")
                    else:
                        msg = add_person_with_ekg(
                            firstname=new_firstname,
                            lastname=new_lastname,
                            date_of_birth=int(new_dob),
                            gender=new_gender,
                            ekg_file_bytes=new_ekg_file.read(),
                            ekg_filename=new_ekg_file.name,
                            ekg_date=new_ekg_date,
                            picture_bytes=new_picture.read() if new_picture else None,
                            picture_filename=new_picture.name if new_picture else None,
                        )
                        st.success(msg)
                        st.rerun()

        # ── Bestehende Person editieren ───────────────────────────────────
        with st.expander("✏️ Bestehende Person editieren"):
            edit_name = st.selectbox("Person auswählen", person_names, key="edit_select")
            edit_person = next(p for p in persons if p.get_full_name() == edit_name)

            with st.form("edit_person_form"):
                st.subheader("Daten bearbeiten")
                col_e, col_f = st.columns(2)
                edit_firstname = col_e.text_input("Vorname", value=edit_person.firstname)
                edit_lastname = col_f.text_input("Nachname", value=edit_person.lastname)

                col_g, col_h = st.columns(2)
                edit_dob = col_g.number_input(
                    "Geburtsjahr",
                    min_value=1900,
                    max_value=2025,
                    value=edit_person.date_of_birth
                )
                gender_options = ["male", "female"]
                edit_gender = col_h.selectbox(
                    "Geschlecht",
                    gender_options,
                    index=gender_options.index(edit_person.gender) if edit_person.gender in gender_options else 0
                )

                edit_picture = st.file_uploader(
                    "Neues Profilbild (optional, leer lassen um beizubehalten)",
                    type=["jpg", "jpeg", "png"],
                    key="edit_picture"
                )

                submitted_edit = st.form_submit_button("Änderungen speichern")

                if submitted_edit:
                    if not edit_firstname or not edit_lastname:
                        st.error("Bitte Vor- und Nachname angeben.")
                    else:
                        msg = update_person(
                            person_id=edit_person.id,
                            firstname=edit_firstname,
                            lastname=edit_lastname,
                            date_of_birth=int(edit_dob),
                            gender=edit_gender,
                            picture_bytes=edit_picture.read() if edit_picture else None,
                            picture_filename=edit_picture.name if edit_picture else None,
                        )
                        st.success(msg)
                        st.rerun()
            st.divider()
            st.warning(f"⚠️ {edit_person.firstname} {edit_person.lastname} endgültig löschen?")
            if st.button("🗑️ Person löschen", key="delete_btn"):
                msg = delete_person(edit_person.id)
                st.success(msg)
                st.rerun()                

        # PDF Export
        # ── PDF-Export ───────────────────────────────────────────────────────────
        with st.expander("📕 PDF-Report exportieren"):

            export_name = st.selectbox("Person auswählen",person_names,key="pdf_select")
            export_person = next(p for p in persons if p.get_full_name() == export_name)

            if st.button("📥 PDF erstellen", key="create_pdf"):

                pdf_buffer = BytesIO()
                c = canvas.Canvas(pdf_buffer, pagesize=A4)

                width, height = A4
                y = height - 50

                c.setFont("Helvetica-Bold", 18)
                c.drawString(50, y, "EKG-Report")
                
                try:
                    c.drawImage(
                        export_person.picture_path,      # Pfad kommt aus der Person-Klasse
                        width - 150,
                        height - 170,
                        width=90,
                        height=90,
                        preserveAspectRatio=True,
                        mask="auto"
                        )
                except Exception:
                    pass

                y -= 40

                c.setFont("Helvetica", 12)
                c.drawString(50, y, f"Name: {export_person.firstname} {export_person.lastname}")
                y -= 20
                c.drawString(50, y, f"Geburtsjahr: {export_person.date_of_birth}")
                y -= 20
                c.drawString(50, y, f"Geschlecht: {export_person.gender}")
                y -= 35

                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, y, "EKG-Tests")
                y -= 25

                c.setFont("Helvetica", 11)

                for test in export_person.ekg_tests:

                    ekg = EKGdata({
                        "id": test["id"],
                        "date": test["date"],
                        "result_link": test["result_link"]
                    })

                    ekg.find_peaks()

                    heart_rate = ekg.estimate_hr()

                    start_time = ekg.df["Zeit in ms"].iloc[0]
                    end_time = ekg.df["Zeit in ms"].iloc[-1]
                    duration_minutes = (end_time - start_time) / 1000 / 60

                    c.drawString(50, y, f"Testdatum: {test['date']}")
                    y -= 18
                    c.drawString(70, y, f"Testdauer: {duration_minutes:.1f} Minuten")
                    y -= 18
                    c.drawString(70, y, f"Durchschnittliche Herzrate: {heart_rate:.1f} BPM")
                    y -= 18
                    c.drawString(70, y, f"Gefundene Peaks: {len(ekg.peaks)}")
                    y -= 30

                    if y < 80:
                        c.showPage()
                        y = height - 50
                        c.setFont("Helvetica", 11)

                c.save()
                pdf_buffer.seek(0)

                st.download_button(
                    label="⬇️ PDF herunterladen",
                    data=pdf_buffer,
                    file_name=f"{export_person.firstname}_{export_person.lastname}_Report.pdf",
                    mime="application/pdf"
                )
    # ════════════════════════════════════════════════════════════════════════
    # SEITE: Aktivitätskarte
    # ════════════════════════════════════════════════════════════════════════
    elif st.session_state.page == "karte":
        st.title("🗺️ Aktivitätskarte")

        fit_file = st.file_uploader("   FIT-Datei hochladen", type=["fit"])

        if fit_file is not None:
            with st.spinner("Daten werden geladen..."):
                df = load_fit_file(fit_file)

            if df.empty:
                st.warning("Keine GPS-Daten in dieser Datei gefunden.")
            else:
                st.subheader("Zusammenfassung")
                cols = st.columns(4)
                if "power" in df.columns:
                    cols[0].metric("Ø Leistung", f"{df['power'].mean():.0f} W")
                    cols[1].metric("Max. Leistung", f"{df['power'].max():.0f} W")
                if "heart_rate" in df.columns:
                    cols[2].metric("Ø Herzfrequenz", f"{df['heart_rate'].mean():.0f} BPM")
                    cols[3].metric("Max. Herzfrequenz", f"{df['heart_rate'].max():.0f} BPM")

                st.divider()

                available_options = {
                    label: col for label, col in COLOR_OPTIONS.items()
                    if col in df.columns
                }
                selected_label = st.selectbox(
                    "Farbe darstellen nach",
                    list(available_options.keys())
                )
                color_col = available_options[selected_label]

                fig_map = plot_fit_map(df, color_by=color_col)
                st.plotly_chart(fig_map, use_container_width=True, key=f"fit_map_chart_{selected_label}")

        else:
            st.info("Bitte eine .fit-Datei hochladen um die Karte anzuzeigen.")