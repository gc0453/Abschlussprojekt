import streamlit as st
import bcrypt
import json
import os
import re

# ── Dateipfad und Dateiname ─────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_FILE = os.path.join(BASE_DIR,"data","users.json")

# ── Passwort prüfen ─────────────────────────────────────────────────────────
def load_users():

    if not os.path.exists(USER_FILE):
        return {}

    with open(USER_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def save_users(users):

    os.makedirs(os.path.dirname(USER_FILE), exist_ok=True)

    with open(USER_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=4)

def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )
    return hashed.decode("utf-8")

def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

def check_password_strength(password: str):
    checks = {
        "Mindestens 8 Zeichen": len(password) >= 8,
        "Groß- und Kleinbuchstaben": (
            re.search(r"[A-Z]", password) is not None
            and re.search(r"[a-z]", password) is not None
        ),
        "Mindestens ein Sonderzeichen": (
            re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\[\];']", password)
            is not None
        )
    }

    return checks

def show_register():

    st.title("👤 Benutzer erstellen")

    username = st.text_input("Neuer Benutzername")
    password = st.text_input("Neues Passwort", type="password")
    password_repeat = st.text_input("Passwort wiederholen", type="password")

    checks = check_password_strength(password)

    st.write("**Passwort-Anforderungen:**")

    for text, valid in checks.items():
        if valid:
            st.success(f"✅ {text}")
        else:
            st.error(f"❌ {text}")

    if all(checks.values()):
        st.success("🟢 Starkes Passwort")
    else:
        st.warning("Passwort erfüllt noch nicht alle Anforderungen.")

    if st.button("Benutzer erstellen"):
        users = load_users()

        if username == "" or password == "":
            st.error("Benutzername und Passwort dürfen nicht leer sein.")

        elif username in users:
            st.error("Benutzer existiert bereits.")

        elif password != password_repeat:
            st.error("Passwörter stimmen nicht überein.")

        elif not all(checks.values()):
            st.error("Das Passwort erfüllt nicht alle Anforderungen.")

        else:
            users[username] = hash_password(password)
            save_users(users)
            st.success("Benutzer wurde erfolgreich erstellt.")

    if st.button("Zum Login"):
        st.session_state.page = "login"
        st.rerun()

def show_login():

    st.title("🔐 Login")

    st.markdown("Noch kein Benutzer?")
    if st.button("Benutzer erstellen"):
        st.session_state.page = "register"
        st.rerun()

    with st.form("login_form"):
        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")

        submitted = st.form_submit_button("Anmelden")

        if submitted:
            users = load_users()

            if username in users and check_password(password, users[username]):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Benutzername oder Passwort falsch.")

