import streamlit as st

# ── User fuer Login ────────────────────────────────────────────────────────────
USERS = {
    "admin": "passwort123",
    "christoph": "geheim"
}

# ── Passwort prüfen ─────────────────────────────────────────────────────────
def show_login():

    st.title("🔐 Login")

    with st.form("login_form"):

        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")

        login_button = st.form_submit_button("Anmelden")

        if login_button:

            if username in USERS and USERS[username] == password:

                st.session_state.logged_in = True
                st.session_state.username = username

                st.rerun()

            else:
                st.error("Benutzername oder Passwort falsch.")