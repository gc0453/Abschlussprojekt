import streamlit as st
from src.person import get_person_data
from src.ekgdata import EKGdata

# ── Seiteneinstellungen ──────────────────────────────────────────────────────
st.set_page_config(page_title="EKG Dashboard", page_icon="🫀", layout="wide")
st.title("🫀 EKG Dashboard")

# ── Personen laden ───────────────────────────────────────────────────────────
persons = get_person_data()
person_names = [p.get_full_name() for p in persons]

# ── Sidebar: Person auswählen ────────────────────────────────────────────────
st.sidebar.header("Person auswählen")
selected_name = st.sidebar.selectbox("Person", person_names)
person = next(p for p in persons if p.get_full_name() == selected_name)

# ── Personen-Info ────────────────────────────────────────────────────────────
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

# ── EKG-Daten ────────────────────────────────────────────────────────────────
if not person.ekg_tests:
    st.info("Keine EKG-Daten für diese Person vorhanden.")
else:
    st.subheader("EKG-Analyse")

    # EKG-Test auswählen (falls mehrere vorhanden)
    ekg_options = {f"EKG vom {t['date']} (ID {t['id']})": t for t in person.ekg_tests}
    selected_ekg_label = st.selectbox("EKG-Test auswählen", list(ekg_options.keys()))
    ekg_dict = ekg_options[selected_ekg_label]

    ekg = EKGdata(ekg_dict)
    ekg.find_peaks()
    hr = ekg.estimate_hr()

    # ── Kennzahlen ───────────────────────────────────────────────────────────
    m1, m2, m3 = st.columns(3)
    m1.metric("Gefundene Peaks", len(ekg.peaks))
    m2.metric("Herzfrequenz (Ø)", f"{hr} BPM")
    m3.metric("Max. Herzfrequenz", f"{person.calc_max_heart_rate()} BPM")

    # ── Plot ──────────────────────────────────────────────────────────────────
    fig = ekg.plot_time_series()
    st.plotly_chart(fig, use_container_width=True)
