import streamlit as st
#from src.person import get_person_data
#from src.ekgdata import EKGdata
from src.ekgstreamlit import show_ekgstreamlit
from src.login import show_login

# ── Seiteneinstellungen ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="EKG Dashboard",
    page_icon="🫀",
    layout="wide"
)


# ── Test-Benutzer ────────────────────────────────────────────────────────────
USERS = {
    "admin": "passwort123",
    "christoph": "geheim"
}

# ── Session State initialisieren ────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""


# ── App starten ─────────────────────────────────────────────────────────────
if st.session_state.logged_in:
    show_ekgstreamlit()
else:
    show_login()